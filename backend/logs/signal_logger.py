import os
import csv
from pathlib import Path
from datetime import datetime
import pytz
import uuid


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

def log_lite_signal(token: str, price: float, prompt: str, response: str,
                    action: str = "", confidence: str = "", risk: str = "",
                    timeframe: str = "", timestamp: str = ""):
    token = token.lower()
    path = Path(f"backend/logs/LITE/{token}.csv")
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "timestamp",
        "token",
        "price",
        "action",
        "confidence",
        "risk",
        "timeframe"
    ]

    row = {
        "timestamp": timestamp,
        "token": token.upper(),
        "price": round(price, 4),
        "action": action,
        "confidence": confidence,
        "risk": risk,
        "timeframe": timeframe
    }

    write_header = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)

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
