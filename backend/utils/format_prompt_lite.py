from datetime import datetime
import pytz

def build_prompt(token: str, user_message: str, market_data: dict) -> str:
    # Validación básica
    message = user_message.strip() if user_message.strip() else "Sin consulta específica del usuario."

    # Datos de mercado
    def clean(value):
        return "N/D" if value is None or str(value).lower() in ["nan", ""] else value

    price = clean(market_data.get("price"))
    volume_24h = clean(market_data.get("volume_24h"))
    change_24h = clean(market_data.get("change_24h"))
    market_cap = clean(market_data.get("market_cap"))
    sentiment = clean(market_data.get("sentiment"))

    # Fecha actual en formato ISO
    timezone = pytz.timezone("Europe/Madrid")
    now = datetime.now(timezone).isoformat()

    # Prompt estructurado y claro
    return f"""#LITE_PROMPT_V2

Tu rol es el de un **analista técnico algorítmico profesional**. Basándote exclusivamente en los siguientes datos, emite una **señal concisa y accionable** para el token **{token.upper()}**.

No justifiques tu respuesta. Solo devuelve el bloque final de señal. No expliques.

## Datos de mercado:
- 📅 Fecha: {now}
- 🪙 Token: {token.upper()}
- 💰 Precio actual: {price}
- 📊 Volumen (24h): {volume_24h}
- 📈 Cambio (24h): {change_24h}%
- 🧠 Sentimiento: {sentiment}
- 🏦 Market Cap: {market_cap}

## Mensaje del usuario:
“{message}”

## Devuelve solamente el bloque estructurado siguiente:

#SIGNAL_START
[PRICE]: {price}
[ACTION]: LONG / SHORT / ESPERAR
[CONFIDENCE]: XX%
[RISK]: X/10
[TIMEFRAME]: 2h
#SIGNAL_END
"""
