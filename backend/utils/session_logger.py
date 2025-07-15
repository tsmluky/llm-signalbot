# services/session_logger.py

import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("logs/advisor_sessions")

def _get_session_file(token: str) -> Path:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    return BASE_DIR / f"{token.upper()}_session.json"

def log_advisor_session(token: str, user_message: str, advisor_response: str):
    session_file = _get_session_file(token)
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_entry = {
        "timestamp": now,
        "user": user_message.strip(),
        "advisor": advisor_response.strip()
    }

    if session_file.exists():
        with open(session_file, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = []

    history.append(new_entry)

    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def get_session_history(token: str) -> list:
    session_file = _get_session_file(token)
    if session_file.exists():
        with open(session_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
