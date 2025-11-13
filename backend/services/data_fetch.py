from __future__ import annotations
import time
from typing import List, Optional, Tuple
import pandas as pd
import ccxt

# Exchanges donde el "quote" estándar es USDT (no USD)
_USDT_EXCHANGES = {"binance", "bybit", "mexc", "okx", "kucoin", "gate"}
# Timeframes soportados (ajusta si quieres más)
_TF = {"1m","3m","5m","15m","30m","1h","2h","4h","6h","12h","1d"}

def _adapt_symbol_for_exchange(symbol: str, exchange: str) -> str:
    """
    Si el exchange usa mayormente USDT, convertimos ETH/USD -> ETH/USDT.
    Si ya está en USDT, se respeta.
    """
    base, quote = symbol.split("/")
    if exchange.lower() in _USDT_EXCHANGES and quote.upper() == "USD":
        return f"{base}/USDT"
    return symbol

def _fetch_once(ex_name: str, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
    ex_cls = getattr(ccxt, ex_name, None)
    if not ex_cls:
        raise ValueError(f"Exchange no soportado: {ex_name}")
    ex = ex_cls()
    try:
        ex.load_markets()
    except Exception:
        # No hacemos fatal si falla load_markets; muchos endpoints funcionan igual
        pass
    data = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    if not data:
        raise ValueError(f"Sin datos en {ex_name} {symbol} {timeframe}")
    df = pd.DataFrame(data, columns=["ts","open","high","low","close","volume"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms", errors="coerce").dt.tz_localize(None).astype(str)
    return df

def fetch_ohlcv_with_fallback(
    exchange: str,
    symbol: str,
    timeframe: str,
    limit: int = 300,
    retries: int = 3,
    backoff_sec: float = 0.8,
    fallbacks: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, str, str]:
    """
    Devuelve (df, exchange_usado, symbol_usado). Intenta `exchange` y luego `fallbacks`.
    Aplica adaptación de símbolo por exchange.
    """
    if timeframe not in _TF:
        raise ValueError(f"Timeframe no soportado: {timeframe}")
    chain = [exchange] + list(fallbacks or [])
    last_err = None
    for idx, ex in enumerate(chain):
        sym = _adapt_symbol_for_exchange(symbol, ex)
        for r in range(max(1, retries)):
            try:
                df = _fetch_once(ex, sym, timeframe, limit)
                return df, ex, sym
            except Exception as e:
                last_err = e
                # backoff rápido y seguimos
                time.sleep(backoff_sec * (1 + r*0.5))
        # siguiente exchange
    raise RuntimeError(f"Error CCXT: {last_err or 'desconocido'}")
