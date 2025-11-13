import os, sqlite3
p = r"backend/data/signalbot.db"
print("DB:", os.path.abspath(p))
conn = sqlite3.connect(p)
cur  = conn.cursor()
cur.execute("PRAGMA journal_mode")
print("journal_mode:", cur.fetchone())
cur.execute("SELECT COUNT(*) FROM pro_analyses")
print("pro_analyses count:", cur.fetchone()[0])
cur.execute("SELECT id, ts, token, timeframe, substr(analysis_md,1,80), meta_json FROM pro_analyses ORDER BY id DESC LIMIT 5")
rows = cur.fetchall()
for r in rows:
    print("pro_analyses ROW:", r)
conn.close()
