import csv
from datetime import datetime
from pathlib import Path
from backend.logs.validator import parse_lite_signal, is_valid_signal

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "signals_lite.csv"

FIELDNAMES = [
    "timestamp",
    "token",
    "price_at_analysis",
    "action",
    "take_profit",
    "stop_loss",
    "confidence",
    "risk",
    "llm_response"
]

def log_lite_signal(token: str, price: float, response: str):
    parsed = parse_lite_signal(response)

    if not is_valid_signal(parsed):
        print("[⚠️] Señal inválida o incompleta. No se registra.")
        return

    entry = {
        "timestamp": datetime.now().isoformat(),
        "token": token.upper(),
        "price_at_analysis": price,
        "llm_response": response,
        **parsed
    }

    write_headers = not LOG_FILE.exists()

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_headers:
            writer.writeheader()
        writer.writerow(entry)

    print(f"[✅] Señal LITE guardada: {parsed['action']} {token.upper()} @ ${price}")
