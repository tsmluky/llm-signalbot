// frontend/services/llmService.js

const API_URL = "https://signalbot-api.onrender.com";

export async function getLLMResponse(prompt, token, mode = "lite") {
  try {
    const response = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, message: prompt, mode }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Respuesta del servidor:", errorText);
      throw new Error("Fallo de red o error en el servidor.");
    }

    const data = await response.json();
    return data.analysis;
  } catch (error) {
    console.error("Error en getLLMResponse:", error);
    throw error;
  }
}
