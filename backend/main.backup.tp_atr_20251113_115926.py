from __future__ import annotations
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
from backend.db import get_conn, init_db, insert_lite, insert_pro, page_lite
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
    row["meta"] = {"source":"llm","features_used": bool(features_summary), **(row.get("meta") or {})}
    _ = insert_lite(conn, row)
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

