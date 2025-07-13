# test_prompt_pro.py

import asyncio
from backend.deepseek_client import get_response_from_llm
from backend.market_data import get_market_data
from backend.utils.format_prompt import build_prompt

async def test():
    token = "eth"
    user_message = "Hazme un análisis técnico con posibles escenarios para hoy."
    
    print(f"📡 Obteniendo datos reales para {token.upper()}")
    market_data = get_market_data(token)
    if market_data.get("error"):
        print("[❌] Error al obtener datos:", market_data["error"])
        return

    prompt = build_prompt(token, user_message, market_data)
    print("📡 Enviando prompt modo PRO...")
    result = await get_response_from_llm(prompt)
    print("\n📨 Respuesta del LLM:\n", result)

if __name__ == "__main__":
    asyncio.run(test())
