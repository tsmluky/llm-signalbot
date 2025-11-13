from __future__ import annotations
import pandas as pd
import numpy as np

def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    down = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
    rs = np.where(down==0, np.nan, up/down)
    rsi = 100 - (100/(1+rs))
    return pd.Series(rsi, index=series.index)

def macd(series: pd.Series, fast: int=12, slow: int=26, signal: int=9):
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def bollinger(series: pd.Series, period: int=20, mult: float=2.0):
    ma = series.rolling(period).mean()
    sd = series.rolling(period).std()
    upper = ma + mult*sd
    lower = ma - mult*sd
    return upper, ma, lower

def atr(df: pd.DataFrame, period: int=14):
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def compute_features(df: pd.DataFrame, cfg: dict) -> dict:
    close = df["close"]
    feat = {}
    feat["rsi"] = {"p14": rsi(close, cfg.get("rsi_period",14)).tail(5).tolist()}
    ef = cfg.get("ema_fast",21); es = cfg.get("ema_slow",50)
    feat["ema"] = {
        "fast": ef, "slow": es,
        "ema_fast": ema(close, ef).tail(5).tolist(),
        "ema_slow": ema(close, es).tail(5).tolist()
    }
    mf, ms, msig = cfg.get("macd_fast",12), cfg.get("macd_slow",26), cfg.get("macd_signal",9)
    m, s, h = macd(close, mf, ms, msig)
    feat["macd"] = {"fast":mf,"slow":ms,"signal":msig,
                    "macd": m.tail(5).tolist(), "signal": s.tail(5).tolist(), "hist": h.tail(5).tolist()}
    up, mid, low = bollinger(close, cfg.get("bb_period",20), cfg.get("bb_mult",2))
    feat["bb"] = {"period": cfg.get("bb_period",20), "mult": cfg.get("bb_mult",2),
                  "upper": up.tail(5).tolist(), "middle": mid.tail(5).tolist(), "lower": low.tail(5).tolist()}
    feat["atr"] = {"p14": atr(df, cfg.get("atr_period",14)).tail(5).tolist()}
    return feat
