from __future__ import annotations
import sqlite3, os, json

DB_DIR = "backend/data"
os.makedirs(DB_DIR, exist_ok=True)

def get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db(conn: sqlite3.Connection):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS signals_lite(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      ts TEXT NOT NULL,
      token TEXT NOT NULL,
      timeframe TEXT NOT NULL,
      price REAL,
      action TEXT CHECK(action IN ('LONG','SHORT','ESPERAR')) NOT NULL,
      confidence INTEGER CHECK(confidence BETWEEN 0 AND 100),
      risk TEXT,
      tp REAL,
      sl REAL,
      meta_json TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_lite_token_time ON signals_lite(token, timeframe, ts);

    CREATE TABLE IF NOT EXISTS evaluated_lite(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      signal_id INTEGER NOT NULL,
      evaluated_ts TEXT NOT NULL,
      result TEXT CHECK(result IN ('HIT','MISS','OPEN')) NOT NULL,
      pct_move REAL,
      details_json TEXT,
      FOREIGN KEY(signal_id) REFERENCES signals_lite(id)
    );

    CREATE TABLE IF NOT EXISTS signals_pro(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      ts TEXT NOT NULL,
      token TEXT NOT NULL,
      timeframe TEXT NOT NULL,
      price REAL,
      analysis_md TEXT NOT NULL,
      meta_json TEXT
    );
    """)
    conn.commit()

def insert_lite(conn, row: dict) -> int:
    cur = conn.execute("""
      INSERT INTO signals_lite(ts,token,timeframe,price,action,confidence,risk,tp,sl,meta_json)
      VALUES(?,?,?,?,?,?,?,?,?,?)
    """, (
      row["ts"], row["token"], row["timeframe"], row.get("price"),
      row["action"], row.get("confidence"), row.get("risk"),
      row.get("tp"), row.get("sl"), json.dumps(row.get("meta", {}))
    ))
    conn.commit()
    return cur.lastrowid

def insert_pro(conn, row: dict) -> int:
    cur = conn.execute("""
      INSERT INTO signals_pro(ts,token,timeframe,price,analysis_md,meta_json)
      VALUES(?,?,?,?,?,?)
    """, (
      row["ts"], row["token"], row["timeframe"], row.get("price"),
      row["analysis_md"], json.dumps(row.get("meta", {}))
    ))
    conn.commit()
    return cur.lastrowid

def page_lite(conn, token: str, timeframe: str|None, limit: int, offset: int):
    q = "SELECT id,ts,token,timeframe,price,action,confidence,risk,tp,sl,meta_json FROM signals_lite WHERE token=?"
    args = [token]
    if timeframe:
        q += " AND timeframe=?"; args.append(timeframe)
    q += " ORDER BY ts DESC LIMIT ? OFFSET ?"; args += [limit, offset]
    cur = conn.execute(q, args)
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]
