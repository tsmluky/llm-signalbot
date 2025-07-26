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

    const analysis = data.analysis;
    if (!analysis || typeof analysis !== "string" || analysis.trim() === "") {
      console.warn("⚠️ El campo 'analysis' está vacío o malformado.");
      return {
        status: "error",
        analysis: "❌ El modelo no devolvió contenido útil.",
        token,
        mode,
        prompt,
        timestamp: new Date().toISOString(),
      };
    }

    return {
      status: "ok",
      analysis,
      token: data.token || token,
      mode: data.mode || mode,
      prompt: data.prompt || prompt,
      timestamp: data.timestamp || new Date().toISOString(),
    };
  } catch (error) {
    console.error("❌ Error en getLLMResponse:", error);
    return {
      status: "error",
      analysis: "❌ Error inesperado al generar el análisis.",
      token,
      mode,
      prompt,
      timestamp: new Date().toISOString(),
    };
  }
}
