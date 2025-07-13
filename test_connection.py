# test_connection.py

import asyncio
from backend.deepseek_client import get_response_from_llm
from backend.market_data import get_market_data

def build_prompt(token: str, market_data: dict) -> str:
    price = market_data.get("price", "N/D")
    volume = market_data.get("volume_24h", "N/D")
    change = market_data.get("change_24h", "N/D")
    market_cap = market_data.get("market_cap", "N/D")

    return f"""
Eres un analista técnico profesional especializado en criptomonedas. A continuación tienes los datos reales del mercado para el token {token.upper()}:

📊 **Datos del mercado:**
- Precio actual: ${price}
- Volumen en 24h: {volume}
- Cambio en 24h: {change}%
- Capitalización de mercado: ${market_cap}

Genera un análisis técnico breve sobre la situación actual de este activo.
"""

async def test():
    token = "eth"
    print("📡 Obteniendo datos de mercado para", token.upper())
    market_data = get_market_data(token)
    if market_data.get("error"):
        print("[❌] Error al obtener datos:", market_data["error"])
        return

    prompt = build_prompt(token, market_data)
    print("📡 Enviando prompt con datos reales...")
    result = await get_response_from_llm(prompt)
    print("📨 Respuesta del LLM:\n", result)

if __name__ == "__main__":
    asyncio.run(test())
