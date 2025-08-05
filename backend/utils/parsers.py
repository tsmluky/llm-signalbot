import re

def extract_fields_from_signal(raw: str) -> dict:
    def get(label):
        match = re.search(rf"\[{label.upper()}\]:\s*(.+)", raw)
        return match.group(1).strip() if match else ""

    return {
        "price": get("PRICE"),
        "action": get("ACTION"),
        "confidence": get("CONFIDENCE"),
        "risk": get("RISK"),
        "timeframe": get("TIMEFRAME"),
    }
