from datetime import datetime
import pytz

def build_prompt(token: str, user_message: str, market_data: dict) -> str:
    # Validación básica
    user_message = user_message.strip() or "Sin consulta específica del usuario."

    # Datos de mercado
    price = market_data.get("price", "N/D")
    volume_24h = market_data.get("volume_24h", "N/D")
    change_24h = market_data.get("change_24h", "N/D")
    market_cap = market_data.get("market_cap", "N/D")
    sentiment = market_data.get("sentiment", "neutral")

    # Fecha actual con zona horaria
    timezone = pytz.timezone("Europe/Madrid")
    now_str = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S %Z")

    # Prompt mejorado
    return f"""#LITE_PROMPT_V1

🎯 Eres un **analista técnico profesional** especializado en criptomonedas. Tu única tarea es emitir una **señal clara, accionable y concisa** sobre el token **{token.upper()}**, considerando exclusivamente la información proporcionada.

✅ **Objetivo**: Indicar si es conveniente abrir una posición LONG, SHORT o si es mejor ESPERAR. No incluyas explicaciones extensas, objetivos de precio ni stop loss. Sé directo y determinante.

📅 **Fecha del análisis**: {now_str}
🪙 **Token**: {token.upper()}
💰 **Precio actual**: ${price}
📊 **Volumen (24h)**: {volume_24h}
📈 **Cambio (24h)**: {change_24h}%
🏦 **Market Cap**: ${market_cap}
🧭 **Sentimiento del mercado**: {sentiment}

🗣️ **Consulta del usuario**:
“{user_message}”

📌 Devuelve únicamente el siguiente bloque con formato estructurado y limpio:

#SIGNAL_START
[ACTION]: LONG / SHORT / ESPERAR  
[CONFIDENCE]: XX%  
[RISK]: X/10  
[TIMEFRAME]: 2h (o el indicado por el usuario)  
#SIGNAL_END
"""
