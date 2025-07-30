import { API_ANALYZE, API_SIGNALS } from "../constants";

/**
 * Realiza una petición al backend para generar un análisis con LLM.
 * @param {string} prompt - El mensaje del usuario.
 * @param {string} token - El token a analizar (ej. ETH).
 * @param {string} mode - El modo de análisis: 'lite', 'pro' o 'advisor'.
 */
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

/**
 * Obtiene el historial de señales para un token y modo específico desde el backend.
 * @param {string} token - El token (ej. ETH).
 * @param {string} mode - El modo ('lite' o 'pro').
 */
export async function fetchSignalsByTokenAndMode(token, mode) {
  try {
    const url = `${API_SIGNALS}/${mode.toLowerCase()}/${token.toLowerCase()}`;
    const res = await fetch(url);
    const data = await res.json();

    if (data.status === "ok" && Array.isArray(data.signals)) {
      return data.signals.reverse(); // más recientes primero
    } else {
      console.warn("⚠️ No se encontraron señales para", token, mode);
      return [];
    }
  } catch (error) {
    console.error("❌ Error al cargar señales:", error);
    return [];
  }
}
