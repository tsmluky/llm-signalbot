from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.deepseek_client import get_response_from_llm
from backend.market_data import get_market_data
from backend.logs.signal_logger import log_lite_signal
from backend.utils import format_prompt, format_prompt_lite
import logging

app = FastAPI()

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class AnalysisRequest(BaseModel):
    token: str
    message: str
    mode: str = "pro"  # valores posibles: 'lite' o 'pro'

@app.post("/analyze")
async def analyze_token(req: AnalysisRequest):
    try:
        if not isinstance(req.message, str) or not isinstance(req.token, str):
            raise ValueError("El mensaje y el token deben ser strings.")

        token = req.token.upper()
        mode = req.mode.lower()

        # Obtener datos del mercado
        market_data = get_market_data(token.lower())
        if not market_data or market_data.get("price") is None:
            raise ValueError(f"No se pudo obtener información del token '{token}'")

        # Construcción del prompt según modo
        if mode == "lite":
            prompt = format_prompt_lite.build_prompt(token, req.message, market_data)
        elif mode == "pro":
            prompt = format_prompt.build_prompt(token, req.message, market_data)
        else:
            raise ValueError(f"Modo inválido: '{mode}'. Usa 'lite' o 'pro'.")

        logger.info(f"[🧠 Prompt generado] Modo: {mode.upper()} | Token: {token}")
        logger.debug(f"Prompt completo:\n{prompt}")

        # Llamada async al LLM
        response = await get_response_from_llm(prompt)
        logger.info("✅ Respuesta recibida del LLM.")

        if mode == "lite":
            log_lite_signal(
                token=token,
                price=market_data.get("price", 0),
                response=response
            )
            logger.info("📝 Señal Lite registrada en logs.")

        return {
            "status": "ok",
            "mode": mode,
            "token": token,
            "analysis": response,
            "prompt": prompt
        }

    except Exception as e:
        logger.error(f"[❌ Error] {str(e)}")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "No se pudo completar el análisis.",
                "details": str(e)
            }
        )
