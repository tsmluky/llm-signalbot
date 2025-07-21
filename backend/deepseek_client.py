import os
import httpx
import logging
from dotenv import load_dotenv
from pathlib import Path

# Setup de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Solo cargar .env si está disponible (útil en local)
env_path = Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Obtener API Key desde variable de entorno
API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

if not API_KEY:
    logging.critical("❌ DEEPSEEK_API_KEY no está definida. Verifica tu entorno (.env o variables en Render).")
    exit(1)

if API_KEY.startswith("TU_API_KEY"):
    logging.critical("❌ DEEPSEEK_API_KEY parece ser un placeholder. Reemplázala por una clave válida.")
    exit(1)

async def get_response_from_llm(prompt: str, system_message: str = "Eres un analista técnico experto en criptomonedas, tienes que respetar la estructura y devolver una idea clara.") -> str:
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
        "temperature": 0.9,
        "max_tokens": 7000,
        "top_p": 1.0,
        "presence_penalty": 0.3
    }

    logging.info("🧠 Prompt enviado a DeepSeek: %s", prompt)

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            logging.info("✅ Respuesta recibida correctamente")
            return content

    except httpx.HTTPStatusError as e:
        logging.error("❌ Código HTTP: %s | Respuesta: %s", e.response.status_code, e.response.text)
        return f"❌ Error HTTP {e.response.status_code}: {e.response.text}"

    except Exception as e:
        logging.error("❌ Error general al contactar con DeepSeek: %s", str(e))
        return "❌ Error interno al contactar con el modelo de análisis."
