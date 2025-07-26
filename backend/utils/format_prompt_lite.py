# backend/utils/format_prompt_lite.py

from datetime import datetime
import pytz

def build_prompt(token: str, user_message: str, market_data: dict, brain_context: str = "") -> str:
    # Validación de mensaje
    message = user_message.strip() if user_message.strip() else "Sin consulta específica del usuario."

    # Datos de mercado con limpieza
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

    # Contexto extendido (opcional)
    context_snippet = f"\n\n## Contexto adicional:\n{brain_context.strip()}" if brain_context.strip() else ""

    # Prompt final
    return f"""#LITE_PROMPT_V3

Tu rol es el de un **analista técnico algorítmico profesional**. Basándote exclusivamente en los siguientes datos, emite una **señal concisa y accionable** para el token **{token.upper()}**.

No justifiques tu respuesta. No expliques. Devuelve únicamente el bloque final de señal.

## Datos de mercado:
- 📅 Fecha: {now}
- 🪙 Token: {token.upper()}
- 💰 Precio actual: {price}
- 📊 Volumen (24h): {volume_24h}
- 📈 Cambio (24h): {change_24h}%
- 🧠 Sentimiento: {sentiment}
- 🏦 Market Cap: {market_cap}

## Mensaje del usuario:
“{message}”{context_snippet}

## Devuelve solamente el siguiente bloque estructurado:

#SIGNAL_START
[PRICE]: {price}
[ACTION]: LONG / SHORT / ESPERAR
[CONFIDENCE]: XX%
[RISK]: X/10
[TIMEFRAME]: 2h
#SIGNAL_END
"""
