import csv
import os
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
import pytz

LITE_DIR = Path("backend/logs/LITE")
EVAL_DIR = Path("backend/logs/EVALUATED")
EVAL_DIR.mkdir(parents=True, exist_ok=True)


TOKEN_IDS = {
    "ETH": "ethereum",
    "BTC": "bitcoin",
    "SOL": "solana",
    "ADA": "cardano",
    "BNB": "binancecoin",
    "MATIC": "matic-network",
}

THRESHOLD = 0.01  # 1% movimiento mínimo
MINUTES_WAIT = 120  # Tiempo a esperar para evaluar

def fetch_price(token_id: str) -> float:
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd"
    res = requests.get(url)
    data = res.json()
    return data[token_id]["usd"]

def evaluate_signal(signal: dict) -> dict:
    token = signal["token"].upper()
    token_id = TOKEN_IDS.get(token)
    if not token_id:
        return None

    try:
        timestamp = datetime.fromisoformat(signal["timestamp"])
        now = datetime.now(pytz.timezone("Europe/Madrid"))

        if (now - timestamp) < timedelta(minutes=MINUTES_WAIT):
            return None  # Aún no han pasado 2 horas

        price_now = fetch_price(token_id)
        price_then = float(signal.get("price", 0))

        if not price_then or price_then <= 0:
            return None

        pct_change = (price_now - price_then) / price_then

        action = signal.get("action", "").upper()
        if action == "LONG":
            result = "CORRECTA" if pct_change >= THRESHOLD else "INCORRECTA"
        elif action == "SHORT":
            result = "CORRECTA" if pct_change <= -THRESHOLD else "INCORRECTA"
        else:
            result = "SIN ACCIÓN"

        return {
            "id": signal["id"],
            "token": token,
            "original_price": price_then,
            "price_after_2h": price_now,
            "change_pct": round(pct_change * 100, 2),
            "result": result,
            "evaluation_time": now.isoformat(),
        }

    except Exception as e:
        print(f"[❌ Error evaluando]: {e}")
        return None

def get_evaluated_ids(filepath):
    if not filepath.exists():
        return set()

    with open(filepath, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["id"] for row in reader if "id" in row}

def evaluate_all_signals():
    for file in LITE_DIR.glob("*.csv"):
        token = file.stem.upper()
        evaluated_path = EVAL_DIR / f"{token.lower()}.evaluated.csv"
        evaluated_ids = get_evaluated_ids(evaluated_path)

        with open(file, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            signals = list(reader)

        results = []
        for signal in signals:
            if signal["id"] not in evaluated_ids:
                eval_result = evaluate_signal(signal)
                if eval_result:
                    results.append(eval_result)
                    print(f"✅ Evaluada {signal['id']} [{eval_result['result']}]")

        if results:
            write_header = not evaluated_path.exists()
            with open(evaluated_path, "a", newline='', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                if write_header:
                    writer.writeheader()
                writer.writerows(results)

if __name__ == "__main__":
    evaluate_all_signals()
def log_evaluated_signal(data: dict):
    """
    Guarda manualmente una evaluación de señal en backend/logs/EVALUATED/{token}.csv
    Esta función es usada por el endpoint /evaluate_signal
    """
    token = data["token"].lower()
    filepath = EVAL_DIR / f"{token}.csv"

    headers = [
        "id", "token", "original_price", "price_after_2h",
        "change_pct", "result", "evaluation_time"
    ]

    write_header = not filepath.exists()
    with open(filepath, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if write_header:
            writer.writeheader()
        writer.writerow({
            "id": data.get("id", ""),
            "token": data.get("token", ""),
            "original_price": data.get("price", ""),
            "price_after_2h": data.get("price_after_2h", ""),
            "change_pct": data.get("percent", ""),
            "result": data.get("result", ""),
            "evaluation_time": data.get("timestamp", datetime.now().isoformat()),
        })
