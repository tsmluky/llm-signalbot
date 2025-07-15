import csv
from pathlib import Path
from datetime import datetime
import re

def extract_value(text, key):
    pattern = rf"\[{key}\]:\s*(.*)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""

def log_lite_signal(token, price, formatted_prompt, response_text):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "timestamp": now,
        "token": token.upper(),
        "price": price,
        "action": extract_value(response_text, "ACTION"),
        "confidence": extract_value(response_text, "CONFIDENCE").replace("%", ""),
        "risk": extract_value(response_text, "RISK"),
        "timeframe": extract_value(response_text, "TIMEFRAME"),
        "prompt": formatted_prompt,
        "response": response_text
    }

    _write_row("logs/signals_lite.csv", data)

def log_pro_signal(token, price, formatted_prompt, response_text):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "timestamp": now,
        "token": token.upper(),
        "price": price,
        "strategy": extract_value(response_text, "STRATEGY"),
        "action": extract_value(response_text, "ACTION"),
        "tp": extract_value(response_text, "TP"),
        "sl": extract_value(response_text, "SL"),
        "confidence": extract_value(response_text, "CONFIDENCE").replace("%", ""),
        "risk": extract_value(response_text, "RISK"),
        "timeframe": extract_value(response_text, "TIMEFRAME"),
        "comment": extract_value(response_text, "COMMENT"),
        "prompt": formatted_prompt,
        "response": response_text
    }

    _write_row("logs/signals_pro.csv", data)

def log_advisor_interaction(token, user_message, response_text, formatted_prompt=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "timestamp": now,
        "token": token.upper(),
        "user_message": user_message,
        "advisor_response": response_text
    }

    if formatted_prompt:
        data["prompt"] = formatted_prompt

    _write_row("logs/interactions_advisor.csv", data)

def _write_row(filepath, data: dict):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists()

    with open(path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
