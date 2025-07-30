import os
import csv
from pathlib import Path
from datetime import datetime
import pytz
import uuid

BASE_DIR = Path(__file__).resolve().parent.parent.parent / "backend" / "logs"

def ensure_dir(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)

def generate_id():
    return str(uuid.uuid4())

def log_lite_signal(token: str, price: float, prompt: str, response: str):
    now = datetime.now(pytz.timezone("Europe/Madrid"))
    filename = BASE_DIR / "LITE" / f"{token.lower()}.csv"
    ensure_dir(filename)

    signal_id = generate_id()

    parsed = {
        "id": signal_id,
        "timestamp": now.isoformat(),
        "token": token.upper(),
        "price": round(price, 4),
        "prompt": prompt.strip(),
        "raw": response.strip(),
    }

    for line in response.splitlines():
        if "[ACTION]:" in line:
            parsed["action"] = line.split(":", 1)[1].strip()
        elif "[TP]:" in line:
            parsed["tp"] = line.split(":", 1)[1].strip()
        elif "[SL]:" in line:
            parsed["sl"] = line.split(":", 1)[1].strip()
        elif "[CONFIDENCE]:" in line:
            parsed["confidence"] = line.split(":", 1)[1].strip()
        elif "[RISK]:" in line:
            parsed["risk"] = line.split(":", 1)[1].strip()
        elif "[TIMEFRAME]:" in line:
            parsed["timeframe"] = line.split(":", 1)[1].strip()

    headers = [
        "id", "timestamp", "token", "price", "prompt", "raw",
        "action", "tp", "sl", "confidence", "risk", "timeframe"
    ]

    write_header = not filename.exists()
    with open(filename, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if write_header:
            writer.writeheader()
        writer.writerow(parsed)


def log_pro_signal(token: str, price: float, prompt: str, response: str):
    now = datetime.now(pytz.timezone("Europe/Madrid"))
    filename = BASE_DIR / "PRO" / f"{token.lower()}.csv"
    ensure_dir(filename)

    parsed = {
        "id": generate_id(),
        "timestamp": now.isoformat(),
        "token": token.upper(),
        "price": round(price, 4),
        "prompt": prompt.strip(),
        "raw": response.strip(),
    }

    headers = ["id", "timestamp", "token", "price", "prompt", "raw"]

    write_header = not filename.exists()
    with open(filename, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if write_header:
            writer.writeheader()
        writer.writerow(parsed)


def log_advisor_interaction(token: str, message: str, response: str, prompt: str):
    now = datetime.now(pytz.timezone("Europe/Madrid"))
    filename = BASE_DIR / "ADVISOR" / f"{token.lower()}.csv"
    ensure_dir(filename)

    parsed = {
        "id": generate_id(),
        "timestamp": now.isoformat(),
        "token": token.upper(),
        "question": message.strip(),
        "answer": response.strip(),
        "prompt": prompt.strip(),
    }

    headers = ["id", "timestamp", "token", "question", "answer", "prompt"]

    write_header = not filename.exists()
    with open(filename, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if write_header:
            writer.writeheader()
        writer.writerow(parsed)
