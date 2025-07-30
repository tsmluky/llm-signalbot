# backend/utils/format_prompt_pro.py

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

    return f"""Analiza profesionalmente el estado actual del token {token.upper()} combinando datos técnicos, narrativos y de mercado. Comunica como un analista financiero senior. Sé claro, estructurado, profundo y profesional. Escribe con riqueza de ideas, justificación cuantitativa y visión táctica. Devuelve el resultado en Markdown, sin símbolos como '•', usa '-' en listas.

**Datos actuales del mercado:**
- Fecha: {now_str}
- Token: {token.upper()}
- Precio: {price}
- Cambio 24h: {change_24h}%
- Volumen 24h: {volume_24h}
- Market Cap: {market_cap}
- Sentimiento: {sentiment}

**Contexto adicional:**  
{brain_context.strip() or "Sin contexto adicional."}

**Consulta del usuario:**  
"{user_message.strip()}"

Estructura el análisis en las siguientes secciones:

## 🌐 Contexto  
Describe factores macroeconómicos, institucionales y narrativos que influyen en {token.upper()}. Incluye datos recientes, menciona actores relevantes (como BlackRock, ETF, etc.) y compara con tendencias anteriores si es relevante.

## 📊 Análisis Técnico  
Detalla resistencias, soportes, volumen, indicadores técnicos (RSI, MACD, EMAs, Bollinger Bands), patrones gráficos, y datos on-chain si es pertinente.

## 📅 Plan de Acción  
Recomienda una acción: comprar, mantener o vender. Justifica con argumentos sólidos y escenarios posibles.

## 🧠 Insight  
Ofrece una reflexión profunda o táctica sobre el comportamiento del mercado de {token.upper()}. Puede incluir hipótesis, comparaciones o señales institucionales.

## ⚙️ Parámetros  
- Acción recomendada  
- Nivel de confianza (1–10)  
- Nivel de riesgo (1–10)

## 🎯 Recomendación Operativa  
- Entry: nivel o rango sugerido de entrada  
- TP1: objetivo de beneficio inicial  
- TP2: segundo objetivo (si aplica)  
- SL: nivel de stop-loss sugerido  
- Justificación: explicación táctica sobre estos niveles.
"""
