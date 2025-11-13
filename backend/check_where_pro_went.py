import os, sqlite3
p = r"backend/data/signalbot.db"
conn = sqlite3.connect(p)
cur = conn.cursor()
def count(t):
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        return cur.fetchone()[0]
    except Exception as e:
        return f"error: {e}"
def tail(t):
    try:
        cur.execute(f"SELECT id, ts, token, timeframe, substr(analysis_md,1,60) FROM {t} ORDER BY id DESC LIMIT 1")
        return cur.fetchone()
    except Exception as e:
        return f"error: {e}"
for t in ("pro_analyses","signals_pro"):
    print(t, "count:", count(t), "last:", tail(t))
conn.close()
