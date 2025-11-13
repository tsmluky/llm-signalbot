from __future__ import annotations
import sqlite3`r`nfrom __future__ import annotations
import sys, pathlib as _pl
_pkg = _pl.Path(__file__).resolve().parent
_root = _pkg.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import os, datetime as dt
from typing import Optional, Dict, Any
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import settings
from backend.db import get_conn, init_db, insert_lite, insert_pro, page_lite, page_pro, ensure_schema, page_pro
from backend.schemas import FeaturesIn, LiteSignalOut, ProAnalysisOut
from backend.services.indicators import compute_features
from backend.services.llm_orchestrator import LLMOrchestrator
from backend.services.data_fetch import fetch_ohlcv_with_fallback

try:
    from backend.utils.rl_cache import RateLimiter
    _rl = RateLimiter(settings.rate_limit_per_min)
    def _rate_limit():
        if not _rl.allow():
            raise HTTPException(429, "Rate limit")
        return None
except Exception:
    def _rate_limit():
        return None

app = FastAPI(title="SignalBot API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

conn = get_conn(settings.db_path); init_db(conn)
llm = LLMOrchestrator(settings.deepseek_api_key)

def _normalize_ohlc(df: pd.DataFrame):
    df.columns = [str(c).strip().lower() for c in df.columns]
    alias = {"timestamp":"ts","time":"ts","date":"ts","open_time":"ts","o":"open","h":"high","l":"low","c":"close","vol":"volume","qty":"volume"}
    for old,new in alias.items():
        if old in df.columns and new not in df.columns:
            df.rename(columns={old:new}, inplace=True)
    need = {"ts","open","high","low","close","volume"}
    missing = sorted(list(need - set(df.columns)))
    if missing:
        raise HTTPException(400, f"CSV debe contener columnas {sorted(list(need))}. Faltan: {missing}.")
    if pd.api.types.is_numeric_dtype(df["ts"]):
        mx = float(df["ts"].max()); unit = "ms" if mx > 1e12 else "s"
        df["ts"] = pd.to_datetime(df["ts"], unit=unit, errors="coerce")
    else:
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    df["ts"] = df["ts"].dt.tz_localize(None).astype(str)
    for c in ["open","high","low","close","volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if df[["open","high","low","close"]].isna().any().any():
        bad = df[["open","high","low","close"]].isna().sum().to_dict()
        raise HTTPException(400, f"OHLC contiene NaN tras coerción numérica: {bad}.")
    return df

@app.get("/health")
def health(): return {"ok": True, "db": settings.db_path}

@app.post("/features")
def features(payload: FeaturesIn, _: None = Depends(_rate_limit)):
    import os
    try:
        if payload.data and "csv_path" in payload.data:
            p = payload.data["csv_path"]
            p = os.path.expanduser(p)
            if not os.path.isabs(p):
                p = os.path.normpath(os.path.join(str(_root), p))
            if not os.path.exists(p):
                raise HTTPException(400, f"CSV no encontrado: {p}")
            df = pd.read_csv(p)
        elif payload.data and "rows" in payload.data:
            df = pd.DataFrame(payload.data["rows"])
        else:
            raise HTTPException(400, "Falta data (csv_path o rows)")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Error leyendo CSV: {e!r}")

    df = _normalize_ohlc(df)
    win = int(payload.window or 120)
    if len(df) > win: df = df.tail(win)
    cfg = payload.config or {}
    try:
        feats = compute_features(df, cfg)
    except Exception as e:
        raise HTTPException(400, f"Fallo en compute_features: {e.__class__.__name__}: {e}")
    return {"price":{"close":df["close"].tail(5).tolist(),"ts":df["ts"].tail(5).tolist()},
            "indicators":feats, "meta":{"window":win,"timeframe":payload.timeframe,"source":"csv/local"}}

class CCXTFeaturesIn(BaseModel):
    token: str
    timeframe: str
    exchange: str = "kraken"
    symbol: str = "ETH/USD"
    limit: int = 300
    config: dict | None = None
    window: int | None = 120
    fallbacks: list[str] | None = ["binance", "bybit", "mexc", "okx"]

@app.post("/features/ccxt")
def features_ccxt(payload: CCXTFeaturesIn, _: None = Depends(_rate_limit)):
    try:
        df, used_ex, used_sym = fetch_ohlcv_with_fallback(
            payload.exchange, payload.symbol, payload.timeframe,
            limit=payload.limit, fallbacks=payload.fallbacks
        )
    except Exception as e:
        raise HTTPException(400, f"Error CCXT: {e}")
    df = _normalize_ohlc(df)
    win = int(payload.window or 120)
    if len(df) > win: df = df.tail(win)
    cfg = payload.config or {}
    try:
        feats = compute_features(df, cfg)
    except Exception as e:
        raise HTTPException(400, f"Fallo en compute_features: {e.__class__.__name__}: {e}")
    return {"price":{"close":df['close'].tail(5).tolist(),"ts":df['ts'].tail(5).tolist()},
            "indicators":feats,
            "meta":{"window":win,"timeframe":payload.timeframe,"source":f"ccxt/{used_ex}:{used_sym}"}}

@app.post("/analyze/lite", response_model=LiteSignalOut)
def analyze_lite(token: str, timeframe: str, features_summary: Dict[str, Any] | None = None, price: float | None = None):
    payload = {"token": token, "timeframe": timeframe, "features_summary": features_summary or {}}
    result = llm.analyze("LITE", payload)

    out = LiteSignalOut(**result)
    row = out.model_dump()
    row["meta"] = {"source": "llm", "features_used": bool(features_summary)}

    def _last_or_none(x):
        try:
            return float(x[-1]) if isinstance(x, (list, tuple)) and x else None
        except Exception:
            return None

    # Extraer features relevantes si vinieron
    atr_last = None
    ema_f_last = None
    ema_s_last = None
    rsi_last  = None
    try:
        fs = features_summary or {}
        if "atr_last" in fs:
            atr_last = float(fs["atr_last"])
        elif isinstance(fs.get("atr"), dict):
            arr = fs["atr"].get("p14") or fs["atr"].get("values")
            atr_last = _last_or_none(arr)

        if "ema_fast_last" in fs: ema_f_last = float(fs["ema_fast_last"])
        if "ema_slow_last" in fs: ema_s_last = float(fs["ema_slow_last"])
        if "rsi_last" in fs:      rsi_last  = float(fs["rsi_last"])

        if ema_f_last is None and isinstance(fs.get("ema"), dict):
            ema_f_last = _last_or_none(fs["ema"].get("ema_fast") or fs["ema"].get("fast"))
            ema_s_last = _last_or_none(fs["ema"].get("ema_slow") or fs["ema"].get("slow"))

        if rsi_last is None and isinstance(fs.get("rsi"), dict):
            rsi_last = _last_or_none(fs["rsi"].get("p14") or fs["rsi"].get("values"))
    except Exception:
        pass

    try:
        # Caso A: LLM ya da LONG/SHORT => TP/SL si hay ATR y price
        if out.action in ("LONG", "SHORT"):
            if price is not None and atr_last is not None:
                tp, sl = _compute_tp_sl_by_atr(out.action, float(price), float(atr_last))
                if tp is not None and sl is not None:
                    row["tp"] = tp
                    row["sl"] = sl
                    out = LiteSignalOut(**row)
        # Caso B: LLM dice ESPERAR => aplicamos regla técnica mínima si hay datos
        elif out.action == "ESPERAR":
            tech_action = None
            if ema_f_last is not None and ema_s_last is not None and rsi_last is not None:
                if ema_f_last > ema_s_last and rsi_last > 52:
                    tech_action = "LONG"
                elif ema_f_last < ema_s_last and rsi_last < 48:
                    tech_action = "SHORT"

            if tech_action is not None:
                row["action"] = tech_action
                # Confianza base por regla: 60; ajusta si quieres en función de distancia EMAs / RSI
                base_conf = 60
                try:
                    slope_bonus = 0
                    if ema_f_last is not None and ema_s_last is not None:
                        slope_bonus = min(10, max(0, abs(ema_f_last - ema_s_last) / max(1, ema_s_last) * 1000))
                    rsi_bonus = min(10, max(0, (rsi_last - 50))) if tech_action == "LONG" else min(10, max(0, (50 - rsi_last)))
                    row["confidence"] = int(min(85, base_conf + slope_bonus * 0.5 + rsi_bonus * 0.5))
                except Exception:
                    row["confidence"] = base_conf

                if price is not None and atr_last is not None:
                    tp, sl = _compute_tp_sl_by_atr(tech_action, float(price), float(atr_last))
                    if tp is not None and sl is not None:
                        row["tp"] = tp
                        row["sl"] = sl

                out = LiteSignalOut(**row)
    except Exception:
        pass

    _ = insert_lite(conn, out.model_dump())
    return out

def _ensure_pro_format(md: str, token: str, tf: str) -> str:
    req = ["#CTXT","#TA","#PLAN","#INSIGHT","#PARAMS"]
    if all(r in md for r in req): return md
    return "\n".join([
        f"#CTXT {token} {tf}",
        "#TA (sin-proveer)",
        "#PLAN (sin-proveer)",
        "#INSIGHT " + (md.replace("\r"," ").replace("\n"," ").strip()[:1800] or "(vacío)"),
        "#PARAMS rsi=14 ema_fast=21 ema_slow=50 macd=12/26/9 bb=20x2",
    ])

@app.post("/analyze/pro", response_model=ProAnalysisOut)
def analyze_pro(token: str, timeframe: str, features_summary: Dict[str, Any] | None = None, price: float | None = None):
    payload = {"token": token, "timeframe": timeframe, "features_summary": features_summary or {}}
    md = str(llm.analyze("PRO", payload))
    md = _ensure_pro_format(md, token, timeframe)
    out = ProAnalysisOut(
        ts=dt.datetime.utcnow().isoformat()+"Z",
        token=token, timeframe=timeframe, price=price,
        analysis_md=md, meta={"features_used": bool(features_summary)}
    )
    _ = insert_pro(conn, out.model_dump())
    return out

@app.get("/logs/lite")
def logs_lite(token: str, timeframe: Optional[str] = None, limit: int = 50, offset: int = 0):
    return {"items": page_lite(conn, token, timeframe, limit, offset), "limit": limit, "offset": offset}



def _compute_tp_sl_by_atr(action: str, price: float, atr_last: float, k_tp: float = 1.5, k_sl: float = 1.0):
    if price is None or atr_last is None:
        return None, None
    if action == "LONG":
        tp = price + k_tp * atr_last
        sl = price - k_sl * atr_last
    elif action == "SHORT":
        tp = price - k_tp * atr_last
        sl = price + k_sl * atr_last
    else:
        return None, None
    return float(round(tp, 2)), float(round(sl, 2))

@app.get("/logs/pro")
def logs_pro(token: str, timeframe: Optional[str] = None, limit: int = 50, offset: int = 0):
    try:
        # 1) intento con page_pro si existe
        try:
            return {"items": page_pro(conn, token, timeframe, limit, offset), "limit": limit, "offset": offset}
        except Exception as e1:
            # 2) bypass: query directa
            q = ["SELECT id, ts, token, timeframe, price, analysis_md, meta_json FROM pro_analyses WHERE token = ?"]
            args = [token]
            if timeframe:
                q.append("AND timeframe = ?")
                args.append(timeframe)
            q.append("ORDER BY ts DESC LIMIT ? OFFSET ?")
            args.extend([int(limit), int(offset)])
            sql = " ".join(q)
            cur = conn.execute(sql, tuple(args))
            rows = []
            import json
            for r in cur.fetchall():
                try:
                    meta = json.loads(r[6]) if r[6] else None
                except Exception:
                    meta = None
                rows.append({
                    "id": r[0], "ts": r[1], "token": r[2], "timeframe": r[3],
                    "price": r[4], "analysis_md": r[5], "meta": meta,
                })
            return {"items": rows, "limit": limit, "offset": offset, "bypass": True, "note": str(e1)}
    except Exception as e2:
        # 3) debug: nunca 500; devuelvo 200 con mensaje de error
        return {"items": [], "limit": limit, "offset": offset, "error": str(e2)}

@app.post("/__migrate")
def __migrate():
    ensure_schema(conn)
    return {"ok": True}




