# backend/evaluator/evaluate_lite_signals.py

import os
import csv
from pathlib import Path
from datetime import datetime, timedelta
import requests
from backend.logs.signal_logger import log_evaluated_signal

# Mapas de tokens para CoinGecko
TOKEN_IDS = {
    "eth": "ethereum",
    "btc": "bitcoin",
    "sol": "solana",
    "matic": "matic-network",
    "ada": "cardano",
    "bnb": "binancecoin",
}

# Ruta base donde están los logs LITE
BASE_LOG_PATH = Path("backend/logs/LITE")

def parse_signal_content(content: str) -> dict:
    lines = content.splitlines()
    parsed = {}
    for line in lines:
        if ":" in line:
            key, val = line.split(":", 1)
            parsed[key.strip().lower()] = val.strip().replace("$", "")
    return parsed

def get_current_price(token: str) -> float:
    token_id = TOKEN_IDS.get(token.lower())
    if not token_id:
        return None
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd"
    res = requests.get(url)
    data = res.json()
    return float(data[token_id]["usd"])

def evaluate_signals():
    now = datetime.utcnow()
    for file in BASE_LOG_PATH.glob("*.csv"):
        token = file.stem.lower()

        try:
            with open(file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            for row in rows:
                signal_id = row.get("id")
                timestamp_str = row.get("timestamp")
                if not timestamp_str:
                    continue

                signal_time = datetime.fromisoformat(timestamp_str)
                if now - signal_time < timedelta(hours=2):
                    continue  # aún no han pasado 2 horas

                # Ya fue evaluada antes
                evaluated_path = Path(f"backend/logs/EVALUATED/{token}.evaluated.csv")
                if evaluated_path.exists():
                    with open(evaluated_path, newline="", encoding="utf-8") as ef:
                        evaluated_ids = [r["id"] for r in csv.DictReader(ef)]
                    if signal_id in evaluated_ids:
                        continue

                signal = parse_signal_content(row.get("analysis", ""))
                action = signal.get("action", "").upper()
                tp = float(signal.get("tp", 0))
                sl = float(signal.get("sl", 0))
                entry = float(signal.get("price", 0))

                current_price = get_current_price(token)
                if current_price is None:
                    continue

                result = "correcta"
                if action == "LONG":
                    if current_price >= tp:
                        result = "correcta"
                    elif current_price <= sl:
                        result = "incorrecta"
                elif action == "SHORT":
                    if current_price <= tp:
                        result = "correcta"
                    elif current_price >= sl:
                        result = "incorrecta"
                else:
                    result = "indefinida"

                log_evaluated_signal(
                    token=token,
                    signal_id=signal_id,
                    result=result,
                    price_at_signal=entry,
                    price_after_2h=current_price
                )

                print(f"[✓] Señal evaluada: {token.upper()} | {signal_id} → {result}")

        except Exception as e:
            print(f"[⚠️ Error evaluando {token}]:", e)

if __name__ == "__main__":
    evaluate_signals()
