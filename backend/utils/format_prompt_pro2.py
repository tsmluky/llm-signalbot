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

    return f"""#PRO_PROMPT_V7

Analiza profesionalmente el estado actual del token {token.upper()} combinando datos técnicos, narrativos y de mercado. Comunica como un analista senior. Sé claro, estructurado y útil. Devuelve todo en español neutro.

#INPUT_DATA
TOKEN: {token.upper()}
DATE: {now_str}
PRICE: {price}
CHANGE_24H: {change_24h}
VOLUME_24H: {volume_24h}
MARKET_CAP: {market_cap}
SENTIMENT: {sentiment}

#USER_QUERY
"{user_message.strip()}"

#BRAIN_CONTEXT
{brain_context.strip() or "Sin contexto adicional."}

# --- Fin del contexto extendido ---

#ANALYSIS_START

## 🌐 Contexto
Analiza el entorno macroeconómico, institucional y narrativo que afecta a {token.upper()} en las últimas 24–48h.

## 📊 Análisis Técnico
Evalúa el gráfico de {token.upper()}: resistencias, soportes, volumen, patrones e indicadores técnicos clave.

## 📅 Plan de Acción
Ofrece una recomendación clara: entrar, salir o mantener, justificando tu decisión.

## 🧠 Insight
Agrega una intuición única basada en los datos anteriores. Aporta una visión que no sea obvia.

## ⚙️ Parámetros
- Acción recomendada
- Nivel de confianza (1–10)
- Nivel de riesgo (1–10)

#ANALYSIS_END
"""
