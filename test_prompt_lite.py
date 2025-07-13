# test_prompt_lite.py

import asyncio
from backend.deepseek_client import get_response_from_llm
from backend.market_data import get_market_data
from backend.utils.format_prompt_lite import build_prompt
from backend.logs.signal_logger import log_lite_signal

async def test():
    token = "eth"
    user_message = "¿Cuál es la mejor señal para hoy?"
    market_data = get_market_data(token)
    
    if market_data.get("error"):
        print("[❌] Error al obtener datos:", market_data["error"])
        return

    prompt = build_prompt(token, user_message, market_data)
    print("📡 Enviando prompt...")
    result = await get_response_from_llm(prompt)
    print("\n📨 Respuesta:\n", result)

    # Log automático
    log_lite_signal(token, market_data["price"], result)

if __name__ == "__main__":
    asyncio.run(test())
