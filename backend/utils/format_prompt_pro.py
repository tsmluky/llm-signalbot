# backend/utils/format_prompt_pro.py

from datetime import datetime
import pytz
import importlib

print("🟢 NUEVO PROMPT_PRO ACTIVADO")

def build_prompt(token: str, user_message: str, market_data: dict) -> str:
    timezone = pytz.timezone("Europe/Madrid")
    now_str = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S %Z")

    message = user_message.strip() if user_message.strip() else "Sin consulta específica. Analiza normalmente."

    price = market_data.get("price", "N/D")
    change = market_data.get("change_24h", "N/D")
    volume = market_data.get("volume_24h", "N/D")
    cap = market_data.get("market_cap", "N/D")
    sentiment = market_data.get("sentiment", "neutral")

    try:
        context_module = importlib.import_module(f"backend.utils.tokens.{token.lower()}")
        context = context_module.get_context()
    except Exception:
        from backend.utils.tokens.default import get_context
        context = get_context()

    return f"""#PRO_PROMPT_V3

#INPUT_DATA
TOKEN: {token.upper()}
DATE: {now_str}
PRICE: {price}
CHANGE_24H: {change}%
VOLUME_24H: {volume}
MARKET_CAP: {cap}
SENTIMENT: {sentiment}

#USER_QUERY
"{message}"

#CONTEXT
{context}

#EXAMPLE_OUTPUT
#ANALYSIS_START

#CTXT#
BTC cotiza en $118K, con volumen moderado y contexto post-halving. ETFs e instituciones siguen influyendo en la narrativa de acumulación. Resistencia clave en $125K.

#TA#
- RSI: 55 (neutral)
- EMAs: EMA200 ($115K) como soporte estructural. EMA50 ($120K) como resistencia inmediata.
- MACD: Señal bajista débil.
- Volumen: Decreciente en rallies. Falta de convicción institucional.
- Soporte: $112K. Resistencia: $125K.

#PLAN#
1. Alcista: romper $125K con volumen alto → LONG hasta $135K  
2. Bajista: perder $112K → SHORT hasta $105K  
3. Lateral: consolidación entre $112K-$125K → esperar confirmación

#INSIGHT#
BTC sigue en fase de acumulación, pero sin fuerza compradora clara. ETFs y tasas de interés son claves. Solo operar ruptura con volumen.

#PARAMS#
[ACTION]: ESPERAR  
[CONFIDENCE]: 72%  
[RISK]: 6.3 / 10

#ANALYSIS_END
"""
