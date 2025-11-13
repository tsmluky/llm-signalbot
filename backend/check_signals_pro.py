import os, sqlite3
p = r"backend/data/signalbot.db"
print("DB:", os.path.abspath(p))
conn = sqlite3.connect(p)
cur  = conn.cursor()

def count(t):
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        return cur.fetchone()[0]
    except Exception as e:
        return f"error: {e}"

for t in ["pro_analyses","signals_pro"]:
    print(t, "->", count(t))

# ver últimas filas en signals_pro (si existieran)
try:
    cur.execute("SELECT id, ts, token, timeframe, substr(analysis_md,1,80) FROM signals_pro ORDER BY id DESC LIMIT 3")
    for r in cur.fetchall():
        print("signals_pro ROW:", r)
except Exception as e:
    print("signals_pro scan error:", e)

conn.close()
