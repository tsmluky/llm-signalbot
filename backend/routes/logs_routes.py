from fastapi import APIRouter, HTTPException
from pathlib import Path
import csv

router = APIRouter()

@router.get("/logs/lite")
def get_lite_signals():
    filepath = Path("logs/signals_lite.csv")
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="No hay señales registradas todavía.")

    try:
        with filepath.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            signals = list(reader)
            signals.sort(key=lambda x: x["timestamp"], reverse=True)  # más recientes primero
            return signals
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer logs: {str(e)}")
