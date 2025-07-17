# main.py

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from collections import Counter
import logging
import csv

from backend.deepseek_client import get_response_from_llm
from backend.market_data import get_market_data
from backend.logs.signal_logger import log_lite_signal, log_pro_signal, log_advisor_interaction
from backend.utils.prompt_compiler import compile_prompt
from backend.utils.session_logger import log_advisor_session

app = FastAPI()

# 🛡️ Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 🌐 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📥 Request Model
class AnalysisRequest(BaseModel):
    token: str
    message: str
    mode: str = "pro"  # 'lite' | 'pro' | 'advisor'

# ✅ Validación inteligente por modo
def is_valid_response(mode: str, response: str) -> bool:
    if not response or "❌" in response:
        return False
    if mode == "lite":
        return "#SIGNAL_START" in response and "#SIGNAL_END" in response
    elif mode == "pro":
        return "#ANALYSIS_START" in response and "#ANALYSIS_END" in response
    elif mode == "advisor":
        return len(response.strip()) > 50
    return False

# 🔍 Endpoint principal de análisis
@app.post("/analyze")
async def analyze_token(req: AnalysisRequest):
    try:
        if not isinstance(req.message, str) or not isinstance(req.token, str):
            raise ValueError("El mensaje y el token deben ser strings.")

        token = req.token.upper().strip()
        mode = req.mode.lower().strip()

        market_data = get_market_data(token.lower())
        price = market_data.get("price")

        if not market_data or price is None or str(price).lower() in ["nan", "n/d", ""]:
            raise ValueError(f"No se pudo obtener información válida del token '{token}'.")

        # 🧠 Compilación del prompt
        prompt = compile_prompt(mode=mode, token=token, user_message=req.message, market_data=market_data)
        logger.info(f"[🧠 Prompt generado] Modo: {mode.upper()} | Token: {token}")
        logger.debug(f"[🧾 Prompt completo ({len(prompt)} chars)]:\n{prompt}")

        # 📡 Llamada al modelo
        response = await get_response_from_llm(prompt)

        if not is_valid_response(mode, response):
            logger.warning(f"⚠️ Prompt enviado:\n{prompt}")
            logger.warning(f"⚠️ Respuesta inválida o incompleta (modo: {mode}):\n{response}")
            raise RuntimeError("El modelo no devolvió una respuesta válida o estructurada.")

        logger.info("✅ Respuesta recibida del LLM.")

        # 📝 Logging por modo
        if mode == "lite":
            log_lite_signal(token, float(price), prompt, response)
            logger.info("📝 Señal Lite registrada en logs.")
        elif mode == "pro":
            log_pro_signal(token, float(price), prompt, response)
            logger.info("📊 Señal Pro registrada en logs.")
        elif mode == "advisor":
            log_advisor_interaction(token, req.message, response, prompt)
            log_advisor_session(token, req.message, response)
            logger.info("💬 Interacción Advisor y sesión registrada en logs.")

        return {
            "status": "ok",
            "mode": mode,
            "token": token,
            "analysis": response,
            "prompt": prompt
        }

    except Exception as e:
        logger.error(f"[❌ Error] {str(e)}")
        status_code = 400 if isinstance(e, ValueError) else 500
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "error",
                "message": "No se pudo completar el análisis.",
                "details": str(e)
            }
        )

# 📄 Devuelve todas las señales guardadas en modo Lite
@app.get("/signals_lite")
@app.get("/signals_lite")
def get_signals_lite():
    log_path = Path("logs/signals_lite.csv")
    if not log_path.exists():
        return []

    try:
        with log_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Ordenar por timestamp descendente (más reciente primero)
        rows.sort(key=lambda x: x["timestamp"], reverse=True)
        return {
            "status": "ok",
            "total": len(rows),
            "signals": rows
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Error al leer señales Lite.",
                "details": str(e)
            }
        )

# 📊 Estadísticas resumidas del modo Lite
@app.get("/stats_lite")
def get_lite_stats():
    def parse_risk_value(risk_str: str) -> float:
        try:
            if "/" in risk_str:
                num, denom = risk_str.split("/")
                return float(num) / float(denom) * 10
            return float(risk_str)
        except:
            return 0.0

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
        avg_risk = sum(parse_risk_value(row["risk"]) for row in rows if row["risk"]) / total

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

# 🧠 Historial de conversaciones modo advisor
@app.get("/session_history/{token}")
def get_advisor_session(token: str):
    session_file = Path(f"logs/sessions/{token.upper()}.csv")
    if not session_file.exists():
        return JSONResponse(status_code=404, content={"status": "error", "message": "No hay conversaciones para este token."})

    try:
        with session_file.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            history = list(reader)

        return {
            "status": "ok",
            "token": token.upper(),
            "history": history
        }

    except Exception as e:
        logger.error(f"[❌ Error al leer sesión de {token}]: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": "Error al leer el historial.",
            "details": str(e)
        })
