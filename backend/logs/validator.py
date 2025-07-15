import csv
from datetime import datetime, timedelta
from pathlib import Path
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("COINMARKETCAP_API_KEY")

VALIDATION_WINDOW_HOURS = 2
INPUT_FILES = {
    "lite": "logs/signals_lite.csv",
    "pro": "logs/signals_pro.csv"
}
OUTPUT_FILES = {
    "lite": "logs/evaluated_signals_lite.csv",
    "pro": "logs/evaluated_signals_pro.csv"
}


def get_price(token: str) -> float:
    try:
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        params = {"symbol": token, "convert": "USD"}
        headers = {"X-CMC_PRO_API_KEY": API_KEY}
        res = requests.get(url, params=params, headers=headers).json()
        return float(res["data"][token]["quote"]["USD"]["price"])
    except Exception as e:
        print(f"[❌] Error al obtener precio de {token}: {e}")
        return None


def evaluate_signals(mode="lite"):
    input_path = Path(INPUT_FILES[mode])
    output_path = Path(OUTPUT_FILES[mode])

    if not input_path.exists():
        print(f"[⚠️] No se encontraron señales en {mode}")
        return

    with input_path.open("r", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        signals = [row for row in reader if not row.get("result")]

    if not signals:
        print(f"[✔️] No hay señales nuevas para validar en {mode}.")
        return

    with output_path.open("a", newline="", encoding="utf-8") as f_out:
        fieldnames = list(signals[0].keys()) + ["result", "price_after"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        if output_path.stat().st_size == 0:
            writer.writeheader()

        for row in signals:
            try:
                timestamp = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
                if datetime.now() < timestamp + timedelta(hours=VALIDATION_WINDOW_HOURS):
                    continue

                token = row["token"]
                price_now = get_price(token)
                if price_now is None:
                    continue

                price_at_signal = float(row["price"])
                action = row["action"]

                if mode == "lite":
                    threshold = 0.005  # 0.5%
                    if action == "LONG" and price_now > price_at_signal * (1 + threshold):
                        result = "SUCCESS"
                    elif action == "SHORT" and price_now < price_at_signal * (1 - threshold):
                        result = "SUCCESS"
                    elif action == "ESPERAR":
                        result = "NEUTRAL"
                    else:
                        result = "FAIL"

                elif mode == "pro":
                    try:
                        tp = float(row["tp"])
                        sl = float(row["sl"])
                        if action == "LONG":
                            if price_now >= tp:
                                result = "SUCCESS"
                            elif price_now <= sl:
                                result = "FAIL"
                            else:
                                result = "NEUTRAL"
                        elif action == "SHORT":
                            if price_now <= tp:
                                result = "SUCCESS"
                            elif price_now >= sl:
                                result = "FAIL"
                            else:
                                result = "NEUTRAL"
                        else:
                            result = "NEUTRAL"
                    except Exception as e:
                        print(f"[⚠️] No se pudo interpretar TP/SL para {token}: {e}")
                        result = "UNKNOWN"

                row["result"] = result
                row["price_after"] = round(price_now, 4)
                writer.writerow(row)
                print(f"[✅] Evaluada {mode.upper()} | {token} | {action} → {result}")

            except Exception as e:
                print(f"[❌] Error evaluando señal: {e}")


if __name__ == "__main__":
    evaluate_signals("lite")
    evaluate_signals("pro")
