# backend/logs/signal_logger.py

import os
import csv
import re
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("logs/signals_lite.csv")
os.makedirs(LOG_FILE.parent, exist_ok=True)

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

def parse_lite_signal(response: str) -> dict:
    """
    Extrae acción, TP, SL, confianza y riesgo desde el texto generado por el LLM (modo lite).
    """
    def extract(pattern):
        match = re.search(pattern, response, re.IGNORECASE)
        return match.group(1).strip() if match else None

    return {
        "action": extract(r"Acción:\s*(LONG|SHORT|ESPERAR)"),
        "take_profit": extract(r"TP(?:\.|:)?\s*\$?(\d+\.?\d*)"),
        "stop_loss": extract(r"SL(?:\.|:)?\s*\$?(\d+\.?\d*)"),
        "confidence": extract(r"Confianza:\s*(\d+)%"),
        "risk": extract(r"Riesgo:\s*(\d+)/10")
    }

def log_lite_signal(token: str, price: float, response: str):
    parsed = parse_lite_signal(response)
    if not parsed["action"]:
        print("[⚠️] No se detectó señal clara en la respuesta. No se guarda.")
        return

    entry = {
        "timestamp": datetime.now().isoformat(),
        "token": token.upper(),
        "price_at_analysis": price,
        "llm_response": response,
        **parsed
    }

    log_exists = LOG_FILE.exists()
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not log_exists:
            writer.writeheader()
        writer.writerow(entry)

    print(f"[✅] Señal LITE guardada: {entry['action']} en {token.upper()} @ ${price}")
