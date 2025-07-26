# backend/utils/retriever.py

import os

def retrieve_context(token: str) -> str:
    base_path = os.path.join(os.path.dirname(__file__), "..", "brain", token.lower())
    context = ""

    if not os.path.exists(base_path):
        return "Sin contexto disponible."

    for filename in os.listdir(base_path):
        filepath = os.path.join(base_path, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                context += f"--- {filename} ---\n"
                context += f.read().strip() + "\n\n"
        except Exception as e:
            context += f"(Error leyendo {filename}: {e})\n"

    print(f"[📚 CONTEXTO CARGADO PARA {token.upper()}]\n{context.strip()}")
    return context.strip()
