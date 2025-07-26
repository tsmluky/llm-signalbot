# backend/utils/format_prompt_pro_flexible.py

from datetime import datetime
import pytz

def build_prompt(token: str, user_message: str, market_data: dict, brain_context: str = "") -> str:
    timezone = pytz.timezone("Europe/Madrid")
    now_str = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S %Z")

    price = market_data.get("price", "N/D")
    volume_24h = market_data.get("volume_24h", "N/D")
    change_24h = market_data.get("change_24h", "N/D")
    market_cap = market_data.get("market_cap", "N/D")
    sentiment = market_data.get("sentiment", "neutral")

    return f"""Eres un analista profesional de mercados cripto. Quiero que analices de forma detallada la situación actual del token {token.upper()}.

Basándote en los siguientes datos de mercado y contexto, ofrece un análisis técnico y narrativo que ayude a tomar decisiones informadas. No utilices estructuras rígidas ni bloques marcados. Escribe como si redactaras un informe breve para otro analista.

Fecha actual: {now_str}
Token: {token.upper()}
Precio actual: {price}
Cambio 24h: {change_24h}%
Volumen 24h: {volume_24h}
Capitalización de mercado: {market_cap}
Sentimiento general: {sentiment}

Contexto adicional:
{brain_context.strip() or "Sin contexto disponible."}

Consulta del usuario:
{user_message.strip()}

Escribe directamente tu análisis completo a continuación:
"""
