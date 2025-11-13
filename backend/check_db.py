import os, sqlite3, json
p = r"backend/data/signalbot.db"
print("DB abs path:", os.path.abspath(p))
conn = sqlite3.connect(p)
cur  = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tablas:", [r[0] for r in cur.fetchall()])
try:
    cur.execute("SELECT COUNT(*) FROM pro_analyses")
    print("pro_analyses count:", cur.fetchone()[0])
    cur.execute("SELECT id, ts, token, timeframe, substr(analysis_md,1,80) FROM pro_analyses ORDER BY id DESC LIMIT 3")
    for row in cur.fetchall():
        print("ROW:", row)
except Exception as e:
    print("pro_analyses no existe:", e)
conn.close()
