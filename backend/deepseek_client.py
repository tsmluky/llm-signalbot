import os
import httpx
import logging
from dotenv import load_dotenv
from pathlib import Path

# Setup de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Cargar .env
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

if not API_KEY or API_KEY.startswith("TU_API_KEY"):
    logging.critical("❌ DEEPSEEK_API_KEY no cargada correctamente. Revisa tu archivo .env.")
    exit(1)

async def get_response_from_llm(prompt: str, system_message: str = "Eres un analista técnico experto en criptomonedas.") -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }

    logging.info("[🧠 Prompt enviado a DeepSeek]: %s", prompt)

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            logging.info("[✅ Respuesta recibida correctamente]")
            return content

    except httpx.HTTPStatusError as e:
        logging.error("[❌] Código HTTP: %s | Texto: %s", e.response.status_code, e.response.text)
    except Exception as e:
        logging.error("[❌] Error general al contactar con DeepSeek: %s", str(e))

    return "Error interno al contactar con el analista técnico."
