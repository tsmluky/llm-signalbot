from datetime import datetime
import pytz
import importlib

def build_prompt(token: str, user_message: str, market_data: dict) -> str:
    price = market_data.get("price", "N/D")
    volume_24h = market_data.get("volume_24h", "N/D")
    change_24h = market_data.get("change_24h", "N/D")
    market_cap = market_data.get("market_cap", "N/D")
    sentiment = market_data.get("sentiment", "neutral")

    timezone = pytz.timezone("Europe/Madrid")
    now_str = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S %Z")

    # Cargar contexto del token desde backend/utils/tokens/{token}.py
    try:
        context_module = importlib.import_module(f"backend.utils.tokens.{token.lower()}")
        context = context_module.get_context()
    except Exception:
        from backend.utils.tokens.default import get_context
        context = get_context()

    return f"""
🧑‍💼 Eres un asesor financiero senior en criptomonedas. Tu rol es guiar al usuario con claridad, estrategia y empatía. No estás obligado a dar señales a menos que se solicite. Podés hablar de gestión del riesgo, ciclos del mercado, errores comunes, o interpretar el comportamiento reciente.

📍 Token: {token.upper()}
🕒 Fecha: {now_str}
💰 Precio actual: ${price}
📈 Cambio 24h: {change_24h}%
📊 Volumen: {volume_24h}
🏦 Market Cap: ${market_cap}
😶 Sentimiento general: {sentiment}

📚 Contexto técnico relevante:
{context}

📨 El usuario ha planteado:
“{user_message}”

🎯 Detectá si está buscando guía técnica, emocional o estratégica.

💬 Respondé con lenguaje humano, profesional y reflexivo. Evitá jergas innecesarias y contestá como un mentor que acompaña a un inversor que quiere aprender y tomar mejores decisiones.
"""
