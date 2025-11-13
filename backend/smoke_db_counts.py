import sqlite3
conn = sqlite3.connect(r"backend/data/signalbot.db"); cur = conn.cursor()
for t in ("pro_analyses","signals_pro"):
    cur.execute(f"SELECT COUNT(*), MAX(id) FROM {t}"); print(t, cur.fetchone())
conn.close()
