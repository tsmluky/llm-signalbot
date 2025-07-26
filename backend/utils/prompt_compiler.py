# backend/utils/prompt_compiler.py

import logging
from backend.utils import format_prompt_lite, format_prompt_pro, format_prompt_assist
from backend.utils import retriever

logger = logging.getLogger(__name__)

def compile_prompt(mode: str, token: str, user_message: str, market_data: dict) -> str:
    """
    Compila el prompt usando el constructor del modo elegido.
    Integra contexto adicional desde la carpeta brain/ para mejorar los análisis.
    """
    token = token.lower().strip()

    # Recuperar contexto extendido desde brain/
    brain_context = retriever.retrieve_context(token)

    try:
        if mode == "lite":
            prompt = format_prompt_lite.build_prompt(token, user_message, market_data, brain_context)
        elif mode == "pro":
            prompt = format_prompt_pro.build_prompt(token, user_message, market_data, brain_context)
        elif mode == "advisor":
            prompt = format_prompt_assist.build_prompt(token, user_message, market_data)
        else:
            raise ValueError(f"[❌ Modo inválido] '{mode}' no es un modo válido.")
    except Exception as e:
        logger.error(f"[❌ Error al generar prompt para modo '{mode}']: {e}")
        prompt = f"[⚠️ Error generando prompt para {token.upper()} en modo {mode.upper()}]"

    logger.debug(f"[🧠 Prompt generado ({len(prompt)} chars)]")
    print("📤 PROMPT COMPLETO:\n", prompt)

    return prompt
