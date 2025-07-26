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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("signalbot")

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
    mode: str = "pro"

def is_valid_response(mode: str, response: str) -> bool:
    if not response or "❌" in response:
        return False
    response = response.strip()

    if mode == "lite":
        return "#SIGNAL_START" in response and "#SIGNAL_END" in response

    elif mode == "pro":
        if "#ANALYSIS_START" in response and "#ANALYSIS_END" in response:
            try:
                content = response.split("#ANALYSIS_START", 1)[1].split("#ANALYSIS_END", 1)[0].strip()
                return len(content) > 100
            except Exception:
                return False
        else:
            # aceptar respuestas libres si tienen contenido sustancial
            return len(response) > 300 and ("ETH" in response.upper() or "Ethereum" in response)

    elif mode == "advisor":
        return len(response.strip()) > 50

    return False

def build_markdown_from_analysis(text: str) -> str:
    try:
        raw = text.strip().replace("#ANALYSIS_START", "").replace("#ANALYSIS_END", "")
        sections = {
            "CTXT": "🌐 Contexto",
            "TA": "📊 Análisis Técnico",
            "PLAN": "📅 Plan de Acción",
            "INSIGHT": "🧠 Insight",
            "PARAMS": "⚙️ Parámetros"
        }
        current_section = None
        parsed = {k: "" for k in sections}
        for line in raw.splitlines():
            tag = re.match(r"#(CTXT|TA|PLAN|INSIGHT|PARAMS)#", line.strip())
            if tag:
                current_section = tag.group(1)
                continue
            elif current_section:
                parsed[current_section] += line + "\n"

        markdown = ""
        for key, title in sections.items():
            content = parsed[key].strip()
            if content:
                markdown += f"## {title}\n\n{content}\n\n"

        return markdown.strip()
    except Exception as e:
        logger.warning(f"[⚠️ Error al formatear análisis PRO]: {e}")
        return "⚠️ Error al formatear análisis técnico. Intenta nuevamente."

@app.post("/analyze")
async def analyze_token(req: AnalysisRequest):
    try:
        token = req.token.upper().strip()
        mode = req.mode.lower().strip()
        message = req.message.strip()

        if not token or not message:
            raise ValueError("Token y mensaje son obligatorios.")

        market_data = get_market_data(token.lower())
        price = market_data.get("price")

        if not market_data or price is None or str(price).lower() in ["nan", "n/d", ""]:
            raise ValueError(f"No se pudo obtener información válida del token '{token}'.")

        prompt = compile_prompt(mode=mode, token=token, user_message=message, market_data=market_data)
        logger.info(f"[🧠 Prompt generado] [{mode.upper()}] {token}")
        print("📤 PROMPT COMPLETO:\n", prompt)

        response = await get_response_from_llm(prompt)
        logger.info(f"[📨 Respuesta LLM recibida]")
        print("[📨 RAW LLM RESPONSE]:", response)

        if not is_valid_response(mode, response):
            logger.warning(f"[❌ Respuesta inválida] Modo: {mode} | Token: {token}")
            return JSONResponse(
                status_code=200,
                content={
                    "status": "error",
                    "analysis": "❌ El modelo no devolvió contenido útil.",
                    "token": token,
                    "mode": mode,
                    "prompt": prompt,
                    "raw_response": response,
                    "timestamp": datetime.now(pytz.timezone("Europe/Madrid")).isoformat()
                }
            )

        # Logging por modo
        if mode == "lite":
            if "#SIGNAL_END" in response:
                price_line = f"[PRICE]: ${float(price):.4f}  \n"
                response = response.replace("#SIGNAL_END", price_line + "#SIGNAL_END")
            log_lite_signal(token, float(price), prompt, response)
            logger.info("📝 Señal LITE registrada.")

        elif mode == "pro":
            log_pro_signal(token, float(price), prompt, response)
            logger.info("📊 Señal PRO registrada.")

        elif mode == "advisor":
            log_advisor_interaction(token, message, response, prompt)
            log_advisor_session(token, message, response)
            logger.info("💬 Interacción ADVISOR registrada.")

        # Formato final de respuesta
        if mode == "pro":
            if "#ANALYSIS_START" in response and "#ANALYSIS_END" in response:
                formatted_response = build_markdown_from_analysis(response)
            else:
                formatted_response = response
        else:
            formatted_response = response

        return {
            "status": "ok",
            "mode": mode,
            "token": token,
            "analysis": formatted_response,
            "prompt": prompt,
            "timestamp": datetime.now(pytz.timezone("Europe/Madrid")).isoformat()
        }

    except Exception as e:
        logger.error(f"[❌ Error] {str(e)}")
        return JSONResponse(
            status_code=400 if isinstance(e, ValueError) else 500,
            content={
                "status": "error",
                "message": "No se pudo completar el análisis.",
                "details": str(e),
                "analysis": "❌ Error interno. Intenta de nuevo más tarde."
            }
        )
