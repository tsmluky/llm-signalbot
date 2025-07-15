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
📌 Eres un analista técnico senior especializado en mercados cripto. Realizas análisis detallado con base en indicadores relevantes y lógica institucional. Tu horizonte base es de 24h, salvo que el usuario indique lo contrario.

🪙 Token: {token.upper()}
🕒 Fecha del análisis: {now_str}
💰 Precio actual: ${price}
📈 Cambio 24h: {change_24h}%
📊 Volumen 24h: {volume_24h}
🏦 Market Cap: ${market_cap}
😶 Sentimiento: {sentiment}

📨 El usuario ha indicado:
“{user_message}”
Identifica si su consulta requiere cambiar el horizonte o el tipo de estrategia.

📉 Indicadores a considerar:
- RSI (1h y 4h)  
- EMAs (20/50)  
- MACD  
- Volumen comparado con promedio  
- Soporte/Resistencia cercano  

🔽 Devuelve únicamente el siguiente bloque estructurado:

#PRO_ANALYSIS_START
[STRATEGY]: Pullback / Breakout / Lateral / Otra  
[ACTION]: LONG / SHORT / ESPERAR  
[TP]: $XXX  
[SL]: $XXX  
[CONFIDENCE]: XX%  
[RISK]: X/10  
[TIMEFRAME]: 24h o la indicada por el usuario  
[COMMENT]: Breve resumen técnico en 2–3 líneas  
#PRO_ANALYSIS_END
"""
