# backend/utils/prompt_compiler.py

import importlib
import logging
from backend.utils import format_prompt_lite, format_prompt, format_prompt_assist

logger = logging.getLogger(__name__)

def compile_prompt(mode: str, token: str, user_message: str, market_data: dict) -> str:
    """
    Compila el prompt combinando:
    - Prompt base (Lite, Pro, Advisor)
    - Contexto específico del token (si existe)
    """
    token = token.lower().strip()
    context = _load_token_context(token)

    try:
        if mode == "lite":
            prompt_core = format_prompt_lite.build_prompt(token, user_message, market_data)
        elif mode == "pro":
            prompt_core = format_prompt.build_prompt(token, user_message, market_data)
        elif mode == "advisor":
            prompt_core = format_prompt_assist.build_prompt(token, user_message, market_data)
        else:
            raise ValueError(f"Modo desconocido: {mode}")
    except Exception as e:
        logger.error(f"[❌ Prompt base] Error al generar prompt para modo '{mode}': {e}")
        prompt_core = f"[⚠️ Error al generar prompt base para {token.upper()} en modo {mode.upper()}]"

    return "\n\n".join(filter(None, [context.strip(), prompt_core.strip()]))

def _load_token_context(token: str) -> str:
    """
    Intenta importar un archivo de contexto específico para el token.
    Fallback a default si no existe.
    """
    try:
        module_path = f"backend.utils.tokens.{token}"
        token_module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        logger.debug(f"[ℹ️ Contexto] No hay archivo para el token '{token}', se usará 'default.py'")
        module_path = "backend.utils.tokens.default"
        token_module = importlib.import_module(module_path)
    except Exception as e:
        logger.warning(f"[⚠️ Error al importar contexto de {token}]: {e}")
        return ""

    get_ctx = getattr(token_module, "get_context", None)
    if callable(get_ctx):
        return get_ctx()
    else:
        logger.debug(f"[ℹ️ Contexto] El módulo '{token}' no tiene función 'get_context'.")
        return ""
