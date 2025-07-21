// frontend/services/llmService.js
import { API_ANALYZE } from "../constants";

export async function getLLMResponse(prompt, token, mode = "lite") {
  try {
    const response = await fetch(API_ANALYZE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, message: prompt, mode }),
    });

    const data = await response.json();
    console.log("[🔍 DATA RAW]:", data);

    if (!response.ok || data.status !== "ok") {
      const msg = data.message || "Fallo desconocido.";
      throw new Error(`❌ No se pudo generar el análisis. ${msg}`);
    }

    return data.analysis;
  } catch (error) {
    console.error("Error en getLLMResponse:", error);
    throw error;
  }
}
