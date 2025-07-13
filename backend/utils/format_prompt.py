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
📌 Rol: Eres un **analista técnico senior especializado en criptomonedas**. Analiza el activo desde una perspectiva profesional, con lógica de mercado y foco institucional.

---

📍 Activo: {token.upper()}
🕒 Fecha/Hora: {now_str}

📊 Datos del mercado:
- Precio: ${price}
- Volumen (24h): {volume_24h}
- Cambio 24h: {change_24h}%
- Market Cap: ${market_cap}
- Sentimiento: {sentiment}

📉 Indicadores estimados:
- RSI (1h): 55–70 (momentum moderado)
- EMAs: posible cruce alcista
- Volumen: creciente

🧠 Instrucciones:
1. Evalúa si conviene entrar en posición.
2. Justifica el análisis técnico.
3. Sugiere SL y TP razonables.
4. Propón estrategia (pullback, breakout...).
5. Finaliza con una recomendación clara:
   - Probabilidad de oportunidad (%)
   - Nivel de riesgo (1–10)

---

📋 Formato de respuesta sugerido:
- Acción recomendada: LONG / SHORT / ESPERAR
- Precio actual: ${price}
- SL / TP sugeridos
- Nivel de riesgo
- Confianza en la operación

---

📣 Consulta del usuario:
> "{user_message}"

Responde con criterio profesional. Evita generalidades. Tu respuesta debe ser operativa y accionable.
"""
