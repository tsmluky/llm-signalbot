import os, sqlite3, json

p = r"backend/data/signalbot.db"
conn = sqlite3.connect(p)
cur  = conn.cursor()

# Comprobar columnas comunes
def cols(table):
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]

src = "signals_pro"
dst = "pro_analyses"

src_cols = set(cols(src))
dst_cols = set(cols(dst))
common   = [c for c in ["ts","token","timeframe","price","analysis_md","meta_json"] if c in src_cols and c in dst_cols]

if not common:
    print("No hay columnas comunes suficientes para migrar.")
else:
    cols_list = ", ".join(common)
    sql = f"INSERT INTO {dst} ({cols_list}) SELECT {cols_list} FROM {src}"
    cur.execute(sql)
    conn.commit()
    print("Migración realizada. Filas insertadas (posiblemente 0 si ya existían/estaban vacías).")

# Contadores finales
for t in [dst, src]:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(t, "->", cur.fetchone()[0])
    except Exception as e:
        print(t, "count error:", e)

conn.close()
