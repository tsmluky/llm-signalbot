import os
import httpx
from dotenv import load_dotenv
from pathlib import Path

# Cargar .env desde la raíz del proyecto
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("DEEPSEEK_API_KEY") or "TU_API_KEY_DIRECTAMENTE_AQUÍ"
API_URL = "https://api.deepseek.com/v1/chat/completions"

if not API_KEY or API_KEY.startswith("TU_API_KEY"):
    raise ValueError("❌ DEEPSEEK_API_KEY no cargada correctamente.")

async def get_response_from_llm(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Eres un analista técnico experto en criptomonedas."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }

    print("[🧠 Prompt enviado a DeepSeek]:", prompt)

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            print("[✅ Respuesta recibida de DeepSeek]")
            return content

    except Exception as e:
        print("[❌] Error al contactar con DeepSeek:", e)
        return "Error interno al contactar con el analista técnico."
