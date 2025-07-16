from datetime import datetime
import pytz

def build_prompt(token: str, user_message: str, market_data: dict) -> str:
    timezone = pytz.timezone("Europe/Madrid")
    now_str = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S %Z")

    message = user_message.strip() if user_message.strip() else "Sin consulta específica. Analiza normalmente."

    price = market_data.get("price", "N/D")
    change = market_data.get("change_24h", "N/D")
    volume = market_data.get("volume_24h", "N/D")
    cap = market_data.get("market_cap", "N/D")
    sentiment = market_data.get("sentiment", "neutral")

    return f"""
#PRO_PROMPT_V3
#INPUT_DATA
TOKEN: {token.upper()}
DATE: {now_str}
PRICE: {price}
CHANGE_24H: {change}%
VOLUME_24H: {volume}
MARKET_CAP: {cap}
SENTIMENT: {sentiment}

#USER_QUERY
“{message}”

#EVAL_INSTRUCTIONS
[CTXT]: contexto técnico global actual.
[TA]: indicadores clave (RSI, EMAs, MACD, Volumen, Soportes/Resistencias).
[PLAN]: estrategia operativa sugerida según escenario.
[INSIGHT]: comentario profesional final, directo y analítico.
[PARAMS]: acción sugerida, confianza, riesgo, TP, SL y timeframe.

#OUTPUT_FORMAT
Responde exclusivamente dentro de #ANALYSIS_START y #ANALYSIS_END.
Respeta este orden estructural y usa un tono de analista profesional.

#ANALYSIS_START
[CTXT]:
…

[TA]:
…

[PLAN]:
…

[INSIGHT]:
…

[PARAMS]:
[ACTION]: LONG / SHORT / ESPERAR
[CONFIDENCE]: XX%
[RISK]: X/10
[TP]: $XXX
[SL]: $XXX
[TIMEFRAME]: 24h u otro
#ANALYSIS_END
"""
