from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, Dict, Any

Action = Literal["LONG","SHORT","ESPERAR"]

class FeaturesIn(BaseModel):
    token: str
    timeframe: str
    window: int = 120
    data: dict | None = None
    config: dict | None = None

class LiteSignalOut(BaseModel):
    ts: str
    token: str
    timeframe: str
    price: float | None = None
    action: Action
    confidence: int = Field(ge=0, le=100)
    risk: str | None = None
    tp: float | None = None
    sl: float | None = None
    meta: Dict[str, Any] = {}

class ProAnalysisOut(BaseModel):
    ts: str
    token: str
    timeframe: str
    price: float | None = None
    analysis_md: str
    meta: Dict[str, Any] = {}

    @field_validator("analysis_md")
    @classmethod
    def must_contain_sections(cls, v: str):
        required = ["#CTXT", "#TA", "#PLAN", "#INSIGHT", "#PARAMS"]
        missing = [k for k in required if k not in v]
        if missing:
            raise ValueError(f"Faltan secciones en analysis_md: {missing}")
        return v
