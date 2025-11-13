from __future__ import annotations
import ccxt, json, datetime as dt
from backend.db import get_conn

def _last_price(exchange: str, symbol: str) -> float:
    ex = getattr(ccxt, exchange)()
    o = ex.fetch_ticker(symbol)
    return float(o["last"])

def evaluate_open_lite(db_path: str, exchange: str, symbol: str, threshold_pct: float = 1.0):
    conn = get_conn(db_path)
    rows = conn.execute("""
      SELECT id, ts, token, timeframe, price, action FROM signals_lite
      WHERE id NOT IN (SELECT signal_id FROM evaluated_lite)
      ORDER BY ts DESC LIMIT 200
    """).fetchall()
    if not rows: return 0
    price_now = _last_price(exchange, symbol)
    now = dt.datetime.utcnow().isoformat() + "Z"
    count = 0
    for (sid, ts, token, tf, price, action) in rows:
        if price is None: continue
        move = (price_now - price) / price * 100.0
        result = "OPEN"
        if action == "LONG":
            if move >= threshold_pct: result = "HIT"
            elif move <= -threshold_pct: result = "MISS"
        elif action == "SHORT":
            if move <= -threshold_pct: result = "HIT"
            elif move >= threshold_pct: result = "MISS"
        conn.execute("""
          INSERT INTO evaluated_lite(signal_id, evaluated_ts, result, pct_move, details_json)
          VALUES(?,?,?,?,?)
        """, (sid, now, result, move, json.dumps({"price_now": price_now, "threshold_pct": threshold_pct})))
        count += 1
    conn.commit()
    return count
