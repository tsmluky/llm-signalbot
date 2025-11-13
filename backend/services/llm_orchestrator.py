from __future__ import annotations
import datetime as dt
from typing import Literal, Dict, Any, List

try:
    from backend.services.deepseek_client import DeepSeekClient
except Exception:
    DeepSeekClient = None  # por si no existe

Mode = Literal["LITE","PRO","ADVISOR"]

_LITE_SYS = (
    "Eres un asistente de trading objetivo. Devuelve una acción LITE "
    "(LONG|SHORT|ESPERAR) y una confianza [0..100] considerando el contexto; "
    "NO inventes niveles; si no hay setup claro, usar ESPERAR."
)

_PRO_SYS = (
    "Eres un analista técnico profesional. Responde en el formato estricto:\n"
    "#CTXT <token> <timeframe>\n#TA <análisis técnico breve y concreto>\n"
    "#PLAN <plan táctico (entradas/TP/SL)>\n#INSIGHT <observaciones clave>\n"
    "#PARAMS rsi=<..> ema_fast=<..> ema_slow=<..> macd=12/26/9 bb=20x2"
)

class LLMOrchestrator:
    def __init__(self, api_key: str | None):
        self.api_key = api_key
        self.client = DeepSeekClient(api_key) if (api_key and DeepSeekClient) else None

    def _now(self) -> str:
        return dt.datetime.utcnow().isoformat() + "Z"

    # ---------- LITE ----------
    def _lite_mock(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ts": self._now(),
            "token": payload["token"],
            "timeframe": payload["timeframe"],
            "price": None,
            "action": "ESPERAR",
            "confidence": 55,
            "risk": "5/10",
            "tp": None, "sl": None,
            "meta": {"mock": True}
        }

    def _lite_deepseek(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Llama a DeepSeek pero MANTIENE el contrato LiteSignalOut."""
        if not self.client:
            return self._lite_mock(payload)

        token = payload["token"]; tf = payload["timeframe"]
        fs = payload.get("features_summary") or {}
        messages: List[Dict[str,str]] = [
            {"role":"system","content": _LITE_SYS},
            {"role":"user","content": f"Token={token} TF={tf} FeaturesSummary={fs}"}
        ]
        try:
            txt = self.client.chat_sync(messages, model="deepseek-chat", temperature=0.4, max_tokens=300)
            # Simplificación: interpretamos acción/score por heurística muy básica
            t = txt.lower()
            if any(w in t for w in ["short fuerte","vender","caída","bearish","bajista"]):
                action = "SHORT"; conf = 65
            elif any(w in t for w in ["long fuerte","comprar","subida","bullish","alcista"]):
                action = "LONG"; conf = 65
            elif "esperar" in t or "no operar" in t:
                action = "ESPERAR"; conf = 55
            else:
                action = "ESPERAR"; conf = 55
            out = self._lite_mock(payload)
            out.update({"action": action, "confidence": conf})
            out["meta"] = {"model": "deepseek", "raw": txt[:400]}
            return out
        except Exception:
            return self._lite_mock(payload)

    # ---------- PRO ----------
    def _pro_mock(self, payload: Dict[str, Any]) -> str:
        return "\n".join([
            f"#CTXT {payload['token']} {payload['timeframe']}",
            "#TA Cruce EMA21/50 estable, RSI 52-55; MACD cercano a señal.",
            "#PLAN Entrada escalonada; TP1 1.5%, TP2 3%; SL -0.8%",
            "#INSIGHT Momentum tibio; esperar confirmación volumen.",
            "#PARAMS rsi=14 ema_fast=21 ema_slow=50 macd=12/26/9 bb=20x2"
        ])

    def _pro_deepseek(self, payload: Dict[str, Any]) -> str:
        if not self.client:
            return self._pro_mock(payload)
        token = payload["token"]; tf = payload["timeframe"]
        fs = payload.get("features_summary") or {}
        messages: List[Dict[str,str]] = [
            {"role":"system","content": _PRO_SYS},
            {"role":"user","content": f"Token={token} TF={tf} FeaturesSummary={fs}\n"
                                      f"Devuelve SIEMPRE las 5 secciones pedidas."}
        ]
        try:
            txt = self.client.chat_sync(messages, model="deepseek-chat", temperature=0.6, max_tokens=700)
            return txt
        except Exception:
            return self._pro_mock(payload)

    # ---------- Público ----------
    def analyze(self, mode: Mode, payload: Dict[str, Any]) -> Dict[str, Any] | str:
        if mode == "LITE":
            return self._lite_deepseek(payload) if self.client else self._lite_mock(payload)
        elif mode == "PRO":
            return self._pro_deepseek(payload) if self.client else self._pro_mock(payload)
        else:
            return "Sugerencia general del asesor (mock)."
