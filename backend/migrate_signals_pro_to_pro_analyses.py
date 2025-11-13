import sqlite3
conn = sqlite3.connect(r"backend/data/signalbot.db")
cur = conn.cursor()
cur.execute("PRAGMA table_info(signals_pro)"); sc = [r[1] for r in cur.fetchall()]
cur.execute("PRAGMA table_info(pro_analyses)"); pc = [r[1] for r in cur.fetchall()]
common = [c for c in ("ts","token","timeframe","price","analysis_md","meta_json") if c in sc and c in pc]
if common:
    cols = ", ".join(common)
    cur.execute(f"INSERT INTO pro_analyses ({cols}) SELECT {cols} FROM signals_pro WHERE ts NOT IN (SELECT ts FROM pro_analyses)")
    conn.commit()
conn.close()
