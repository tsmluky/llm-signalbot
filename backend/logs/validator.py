import re

def parse_lite_signal(response: str) -> dict:
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

def is_valid_signal(parsed: dict) -> bool:
    try:
        return (
            parsed["action"] in {"LONG", "SHORT", "ESPERAR"} and
            float(parsed["take_profit"]) > 0 and
            float(parsed["stop_loss"]) > 0 and
            0 <= int(parsed["confidence"]) <= 100 and
            1 <= int(parsed["risk"]) <= 10
        )
    except Exception:
        return False
