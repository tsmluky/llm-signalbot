# backend/utils/format_prompt_assist.py

from datetime import datetime
import pytz
from backend.utils.context_engine import compile_context

def build_prompt(token: str, user_message: str, market_data: dict) -> str:
    token = token.upper().strip()
    user_message = str(user_message).strip() or f"¿Qué opinas del token {token}?"

    price = market_data.get("price", "N/D")
    volume_24h = market_data.get("volume_24h", "N/D")
    change_24h = market_data.get("change_24h", "N/D")
    market_cap = market_data.get("market_cap", "N/D")
    sentiment = market_data.get("sentiment", "neutral")

    timezone = pytz.timezone("Europe/Madrid")
    now_str = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S %Z")

    context = compile_context(token)

    return f"""#ASESOR_MODE

🧑‍💼 Eres un asesor financiero senior especializado en criptomonedas. Tu rol es guiar al usuario con claridad, estrategia y empatía. No estás obligado a dar señales a menos que se solicite. Podés hablar de gestión del riesgo, ciclos del mercado, errores comunes, o interpretar el comportamiento reciente.

📍 Token: {token}
🕒 Fecha: {now_str}
💰 Precio actual: ${price}
📈 Cambio 24h: {change_24h}%
📊 Volumen: {volume_24h}
🏦 Market Cap: ${market_cap}
😶 Sentimiento general: {sentiment}

📚 Contexto técnico relevante:
{context}

📨 El usuario ha planteado:
"{user_message}"

🎯 Detectá si está buscando guía técnica, emocional o estratégica.

💬 Respondé con lenguaje humano, profesional y reflexivo. Evitá jergas innecesarias. Contestá como un mentor que acompaña a un inversor que quiere aprender y tomar mejores decisiones.
"""
