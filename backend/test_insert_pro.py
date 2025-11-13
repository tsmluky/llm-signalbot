import os, sqlite3, json, time
from backend.db import insert_pro, ensure_schema

p = r"backend/data/signalbot.db"
conn = sqlite3.connect(p)
ensure_schema(conn)

row = {
  "ts": "TEST-"+str(int(time.time())),
  "token": "ETH",
  "timeframe": "30m",
  "price": None,
  "analysis_md": "#CTXT test\n#TA ...\n#PLAN ...\n#INSIGHT ...\n#PARAMS ...",
  "meta": {"source":"unit","ok":True}
}
id_ = insert_pro(conn, row)
print("insert_pro id:", id_)
cur = conn.execute("SELECT COUNT(*) FROM pro_analyses")
print("pro_analyses count now:", cur.fetchone()[0])
conn.close()
