# utils/format_prompt.py

from datetime import datetime
import pytz

def build_prompt(token: str, user_message: str, market_data: dict) -> str:
    timezone = pytz.timezone("Europe/Madrid")
    now_str = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S %Z")

    message = user_message.strip() if user_message.strip() else "Sin consulta específica. Analiza normalmente."

    price = market_data.get("price", "N/D")
    change = market_data.get("change_24h", "N/D")
    volume = market_data.get("volume_24h", "N/D")
    cap = market_data.get("market_cap", "N/D")
    sentiment = market_data.get("sentiment", "neutral")

    return f"""
#PRO_PROMPT_V1

📌 **Análisis técnico avanzado de {token.upper()}**

🎯 Tu tarea es generar un análisis técnico profesional para el token {token.upper()}, combinando indicadores clásicos, estructura de mercado y lógica institucional. El horizonte base es de **24h**, salvo que el usuario indique lo contrario. El lenguaje debe ser formal, preciso y accionable. Evitá frases vagas o genéricas.

🕒 Fecha del análisis: {now_str}  
🪙 Token: {token.upper()}  
💰 Precio actual: ${price}  
📈 Cambio en 24h: {change}%  
📊 Volumen en 24h: {volume}  
🏦 Capitalización: ${cap}  
🧭 Sentimiento general: {sentiment}

🗣️ **Consulta del usuario:**  
“{message}”

---

🔍 Indicadores sugeridos (elige los más relevantes según contexto actual):  
- RSI (1h, 4h, 24h)  
- EMAs (20, 50, 100)  
- MACD  
- Volumen relativo  
- Estructura de mercado  
- Soportes y resistencias  
- Contexto macroeconómico y sentimiento

---

🎓 **Estructura de la respuesta:**

#ANALYSIS_START

📊 **Análisis Técnico Detallado:**  
Describe la situación técnica actual, nivel clave, momentum, zonas a vigilar. Incluye interpretación con lógica profesional.

📈 **Estrategia Sugerida:**  
Tipo de movimiento: Pullback / Breakout / Rango / Otra. Justifica por qué.

🧠 **Comentario Profesional:**  
Resumen técnico del escenario con lenguaje claro, pero experto. Conclusión sólida.

🎯 **Parámetros de Acción:**
[ACTION]: LONG / SHORT / ESPERAR  
[CONFIDENCE]: XX%  
[RISK]: X/10  
[TP]: $XXX  
[SL]: $XXX  
[TIMEFRAME]: 24h u otro indicado por el usuario

#ANALYSIS_END
"""
