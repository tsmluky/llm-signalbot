# backend/utils/prompt_compiler.py

import importlib
import logging

# Modularizado por modo
from backend.utils import format_prompt_lite, format_prompt_pro, format_prompt_assist

logger = logging.getLogger(__name__)

def compile_prompt(mode: str, token: str, user_message: str, market_data: dict) -> str:
    """
    Compila el prompt combinando:
    - Prompt base (según modo)
    - Contexto específico del token
    """
    token = token.lower().strip()
    context = _load_token_context(token)

    try:
        if mode == "lite":
            prompt_core = format_prompt_lite.build_prompt(token, user_message, market_data)
        elif mode == "pro":
            prompt_core = format_prompt_pro.build_prompt(token, user_message, market_data)
        elif mode == "advisor":
            prompt_core = format_prompt_assist.build_prompt(token, user_message, market_data)
        else:
            raise ValueError(f"[❌ Modo inválido] '{mode}' no es un modo válido.")
    except Exception as e:
        logger.error(f"[❌ Error al generar prompt base para modo '{mode}']: {e}")
        prompt_core = f"[⚠️ Error generando prompt para {token.upper()} en modo {mode.upper()}]"

    full_prompt = "\n\n".join(filter(None, [context.strip(), prompt_core.strip()]))

    logger.debug(f"[🧠 Prompt final generado ({len(full_prompt)} chars)]")
    return full_prompt


def _load_token_context(token: str) -> str:
    """
    Intenta importar un módulo de contexto específico del token.
    Fallback: `default.py` si no existe.
    """
    try:
        module_path = f"backend.utils.tokens.{token}"
        token_module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        logger.debug(f"[ℹ️ Token '{token}']: no se encontró archivo, usando 'default.py'")
        module_path = "backend.utils.tokens.default"
        token_module = importlib.import_module(module_path)
    except Exception as e:
        logger.warning(f"[⚠️ Error cargando contexto para {token}]: {e}")
        return ""

    get_ctx = getattr(token_module, "get_context", None)
    if callable(get_ctx):
        return get_ctx()
    else:
        logger.debug(f"[ℹ️ '{token}']: el módulo no contiene función 'get_context'")
        return ""
