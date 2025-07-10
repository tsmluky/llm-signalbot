# backend/logs/validator.py

import csv
import requests
from datetime import datetime, timedelta
from pathlib import Path

INPUT_CSV = Path("logs/signals_lite.csv")
OUTPUT_CSV = Path("logs/validated_signals.csv")
API_URL = "https://api.coingecko.com/api/v3/simple/price"

def get_current_price(token_id: str):
    try:
        resp = requests.get(API_URL, params={"ids": token_id, "vs_currencies": "usd"}, timeout=10)
        resp.raise_for_status()
        return resp.json()[token_id]["usd"]
    except Exception as e:
        print(f"[❌] Error obteniendo precio actual para {token_id}: {e}")
        return None

def validate_signals():
    if not INPUT_CSV.exists():
        print("[⚠️] No se encontró ningún archivo de señales.")
        return

    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        signals = list(reader)

    validated = []
    now = datetime.now()

    for signal in signals:
        ts = datetime.fromisoformat(signal["timestamp"])
        if (now - ts) < timedelta(hours=24):
            continue  # solo validamos señales viejas

        token_id = signal["token"].lower()
        current_price = get_current_price(token_id)

        if current_price is None:
            continue

        result = "⏳ Inconclusa"
        action = signal["action"]
        tp = float(signal["take_profit"] or 0)
        sl = float(signal["stop_loss"] or 0)

        if action == "LONG":
            if current_price >= tp:
                result = "✅ TP alcanzado"
            elif current_price <= sl:
                result = "❌ SL alcanzado"
        elif action == "SHORT":
            if current_price <= tp:
                result = "✅ TP alcanzado"
            elif current_price >= sl:
                result = "❌ SL alcanzado"

        validated.append({
            **signal,
            "validation_time": now.isoformat(),
            "price_now": current_price,
            "result": result
        })

    if validated:
        with open(OUTPUT_CSV, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=validated[0].keys())
            if not OUTPUT_CSV.exists():
                writer.writeheader()
            writer.writerows(validated)

        print(f"[✅] Validaciones guardadas: {len(validated)}")
    else:
        print("[ℹ️] No hay señales para validar aún.")

if __name__ == "__main__":
    validate_signals()
