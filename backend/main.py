from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import re
from datetime import datetime
import pytz

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

# 🧾 Conversión robusta a markdown visual
def transform_pro_response_to_markdown(text: str) -> str:
    try:
        raw = text.strip()
        raw = raw.replace("#ANALYSIS_START", "").replace("#ANALYSIS_END", "")

        blocks = {
            "CTXT": {"title": "🌐 Contexto", "content": ""},
            "TA": {"title": "📊 Análisis Técnico", "content": ""},
            "PLAN": {"title": "📅 Plan de Acción", "content": ""},
            "INSIGHT": {"title": "🧠 Insight", "content": ""},
            "PARAMS": {"title": "⚙️ Parámetros", "content": ""}
        }

        current = None
        for line in raw.splitlines():
            tag_match = re.match(r"#(CTXT|TA|PLAN|INSIGHT|PARAMS)#", line.strip())
            if tag_match:
                current = tag_match.group(1)
                continue
            elif current:
                blocks[current]["content"] += line + "\n"

        result = ""
        for key in ["CTXT", "TA", "PLAN", "INSIGHT", "PARAMS"]:
            content = blocks[key]["content"].strip()
            if content:
                result += f"## {blocks[key]['title']}\n\n{content}\n\n"

        return result.strip()

    except Exception as e:
        logger.warning(f"[⚠️ Error al convertir a markdown]: {e}")
        return text

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
        print("debug response:", response)
        logger.warning(f"[🧪 RESPUESTA BRUTA DEL MODELO]:\n{response}")
        logger.warning(f"[📨 PROMPT ENVIADO]:\n{prompt}")

        if not is_valid_response(mode, response):
            logger.warning(f"⚠️ Prompt enviado:\n{prompt}")
            logger.warning(f"⚠️ Respuesta inválida o incompleta (modo: {mode}):\n{response}")
            raise RuntimeError("El modelo no devolvió una respuesta válida o estructurada.")

        logger.info("✅ Respuesta recibida del LLM.")

        # 📝 Logging por modo + inyección de precio si es LITE
        if mode == "lite":
            if "#SIGNAL_END" in response:
                price_line = f"[PRICE]: ${float(price):.4f}  \n"
                response = response.replace("#SIGNAL_END", price_line + "#SIGNAL_END")
            log_lite_signal(token, float(price), prompt, response)
            logger.info("📝 Señal Lite registrada en logs.")
        elif mode == "pro":
            log_pro_signal(token, float(price), prompt, response)
            logger.info("📊 Señal Pro registrada en logs.")
        elif mode == "advisor":
            log_advisor_interaction(token, req.message, response, prompt)
            log_advisor_session(token, req.message, response)
            logger.info("💬 Interacción Advisor y sesión registrada en logs.")

        # 🧾 Markdown estructurado para modo PRO
        if mode == "pro":
            markdown_response = transform_pro_response_to_markdown(response)
        else:
            markdown_response = response

        # 🕒 Timestamp
        timezone = pytz.timezone("Europe/Madrid")
        timestamp = datetime.now(timezone).isoformat()

        return {
            "status": "ok",
            "mode": mode,
            "token": token,
            "analysis": markdown_response,
            "prompt": prompt,
            "timestamp": timestamp
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
