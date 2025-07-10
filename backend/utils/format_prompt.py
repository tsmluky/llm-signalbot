# backend/utils/format_prompt.py

from datetime import datetime
import pytz  # pip install pytz

def build_prompt(token: str, user_message: str, market_data: dict) -> str:
    price = market_data.get("price", "N/D")
    volume_24h = market_data.get("volume_24h", "N/D")
    change_24h = market_data.get("change_24h", "N/D")
    market_cap = market_data.get("market_cap", "N/D")
    sentiment = market_data.get("sentiment", "neutral")

    # Fecha y hora actual con zona horaria (España por defecto)
    timezone = pytz.timezone("Europe/Madrid")
    now_str = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S %Z")

    return f"""
📌 Rol: Eres un **analista técnico senior especializado en criptomonedas**, con enfoque en lectura de mercado, indicadores y gestión del riesgo. Tu objetivo es producir un análisis claro, lógico y táctico, como si asesoraras a un fondo institucional.

---

📍 **Activo analizado:** {token.upper()}
🕒 **Hora del análisis:** {now_str}

📊 **Datos actuales del mercado (fuente: CoinGecko):**
- Precio: ${price}
- Volumen (24h): {volume_24h}
- Cambio 24h: {change_24h}%
- Capitalización de mercado: ${market_cap}
- Sentimiento general: {sentiment}

📉 **Indicadores técnicos estimados (simulados por el sistema):**
- RSI (1h): entre 55 y 70 → momentum moderado
- EMAs (20/50): posible cruce alcista reciente
- Soportes/Resistencias: basados en estructura local
- Volumen: normal o creciente

📚 **Métodos de análisis sugeridos**: RSI, EMAs, patrones de consolidación, volumen relativo, soportes dinámicos, estructura de velas.

---

🧠 **Instrucciones para tu análisis:**

1. Evalúa si es un buen momento para **entrar en posición**, basándote en los datos mostrados.
2. Justifica tu análisis con **argumentos técnicos concretos** y escenarios posibles.
3. Sugiere rangos razonables de **Stop-Loss (SL)** y **Take-Profit (TP)**.
4. Propón la **estrategia técnica** más adecuada (pullback, breakout, etc.) y por qué.
5. Finaliza con una **recomendación clara**, incluyendo:
   - ✅ Probabilidad estimada de oportunidad de entrada (ej. 65%)
   - ⚠️ Nivel de riesgo (1 = muy riesgoso, 10 = muy seguro)

---

📋 **Resumen accionable (obligatorio, formato tabla o listado):**
- Acción recomendada: LONG / SHORT / ESPERAR
- Precio actual: ${price}
- SL / TP sugeridos
- Nivel de riesgo (1-10)
- Confianza en la operación (porcentaje)

---

🧾 **Consulta del usuario:**
> "{user_message}"

📣 Responde con lenguaje profesional, sin frases genéricas ni especulaciones vagas. Cierra con una recomendación práctica, útil y precisa.
"""
