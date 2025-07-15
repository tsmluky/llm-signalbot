from datetime import datetime
import pytz

def build_prompt(token: str, user_message: str, market_data: dict) -> str:
    price = market_data.get("price", "N/D")
    volume_24h = market_data.get("volume_24h", "N/D")
    change_24h = market_data.get("change_24h", "N/D")
    market_cap = market_data.get("market_cap", "N/D")
    sentiment = market_data.get("sentiment", "neutral")

    timezone = pytz.timezone("Europe/Madrid")
    now_str = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S %Z")

    return f"""
🎯 Eres un analista técnico profesional. Tu única tarea es emitir una señal clara y directa sobre el comportamiento esperado del token {token.upper()} en las **próximas 2 horas**, salvo que el usuario indique otro plazo.

📌 No incluyas objetivos de precio ni stop loss. Solo indica si es buen momento para entrar (LONG o SHORT), o si conviene esperar. Sé conciso y determinante.

🕒 Fecha del análisis: {now_str}
🪙 Token: {token.upper()}
💰 Precio actual: ${price}
📈 Cambio 24h: {change_24h}%
📊 Volumen 24h: {volume_24h}
🏦 Capitalización de mercado: ${market_cap}
🧭 Sentimiento general: {sentiment}

🗣 Consulta del usuario:
“{user_message}”

🔽 Devuelve exclusivamente el siguiente bloque con formato estructurado:

#SIGNAL_START
[ACTION]: LONG / SHORT / ESPERAR  
[CONFIDENCE]: XX%  
[RISK]: X/10  
[TIMEFRAME]: 2h o el indicado por el usuario  
#SIGNAL_END
"""
