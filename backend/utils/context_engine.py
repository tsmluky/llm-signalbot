# backend/utils/context_engine.py

import os

def compile_context(token: str) -> str:
    """
    Compila todo el contexto disponible para el token:
    - insights.md
    - news.txt
    - onchain.txt
    - sentiment.txt
    """
    base_path = os.path.join(os.path.dirname(__file__), "..", "brain", token.lower())
    context = ""

    if not os.path.exists(base_path):
        return "Sin contexto disponible."

    files = ["insights.md", "news.txt", "onchain.txt", "sentiment.txt"]
    for filename in files:
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    section = f"\n## {filename.replace('.txt','').replace('.md','').capitalize()}\n{f.read().strip()}\n"
                    context += section
            except Exception as e:
                context += f"\n[Error leyendo {filename}: {e}]\n"
    
    return context.strip() or "Sin contexto disponible."

def compile_sentiment(token: str) -> str:
    return _read_single_file(token, "sentiment.txt")

def compile_onchain(token: str) -> str:
    return _read_single_file(token, "onchain.txt")

def _read_single_file(token: str, filename: str) -> str:
    base_path = os.path.join(os.path.dirname(__file__), "..", "brain", token.lower(), filename)
    try:
        with open(base_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""

def embed_context(prompt: str, token: str) -> str:
    """
    Inserta el bloque de contexto completo al principio del prompt.
    """
    context = compile_context(token)
    return f"{context}\n\n{prompt}"
