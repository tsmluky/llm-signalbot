from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.deepseek_client import get_response_from_llm
from backend.market_data import get_market_data
from backend.logs.signal_logger import log_lite_signal
from backend.utils import format_prompt, format_prompt_lite
from pathlib import Path
import logging
import csv

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

@app.get("/signals_lite")
def get_signals_lite():
    log_path = Path("logs/signals_lite.csv")
    if not log_path.exists():
        return []

    with open(log_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

import csv
from pathlib import Path
from collections import Counter

@app.get("/stats_lite")
def get_lite_stats():
    try:
        log_file = Path("logs/signals_lite.csv")
        if not log_file.exists():
            return {"status": "ok", "stats": {}}

        with log_file.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        total = len(rows)
        if total == 0:
            return {"status": "ok", "stats": {}}

        actions = Counter(row["action"] for row in rows)
        avg_confidence = sum(int(row["confidence"]) for row in rows if row["confidence"]) / total
        avg_risk = sum(float(row["risk"]) for row in rows if row["risk"]) / total

        return {
            "status": "ok",
            "stats": {
                "total_signals": total,
                "long_count": actions.get("LONG", 0),
                "short_count": actions.get("SHORT", 0),
                "wait_count": actions.get("ESPERAR", 0),
                "avg_confidence": round(avg_confidence, 2),
                "avg_risk": round(avg_risk, 2)
            }
        }

    except Exception as e:
        logger.error(f"[❌ Error en /stats_lite] {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "No se pudieron calcular las estadísticas.",
                "details": str(e)
            }
        )
