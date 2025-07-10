# backend/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.deepseek_client import get_response_from_llm
from backend.market_data import get_market_data
from backend.logs.signal_logger import log_lite_signal
import logging

# Imports para modo LITE y PRO
from backend.utils import format_prompt, format_prompt_lite

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    token: str
    message: str
    mode: str = "pro"  # puede ser 'pro' o 'lite'

@app.post("/analyze")
async def analyze_token(req: AnalysisRequest):
    try:
        market_data = get_market_data(req.token.lower())
        if not market_data or market_data.get("price") is None:
            raise ValueError(f"No se pudo obtener información del token '{req.token}'")

        # Generar el prompt según el modo
        if req.mode == "lite":
            prompt = format_prompt_lite.build_prompt(req.token.upper(), req.message, market_data)
        else:
            prompt = format_prompt.build_prompt(req.token.upper(), req.message, market_data)

        logger.info(f"[🧠 Prompt generado - modo {req.mode}]: {prompt[:150]}...")

        # Obtener respuesta del LLM
        response = get_response_from_llm(prompt)
        logger.info("✅ Respuesta recibida correctamente.")

        # Guardar señal Lite si corresponde
        if req.mode == "lite":
            log_lite_signal(
                token=req.token.upper(),
                price=market_data.get("price", 0),
                response=response
            )

        return {
            "analysis": response,
            "prompt": prompt
        }

    except Exception as e:
        logger.error(f"[❌] Error en el análisis: {str(e)}")
        return {
            "error": "No se pudo completar el análisis.",
            "details": str(e)
        }
