// frontend/services/llmService.js
const API_URL = "http://192.168.1.227:8000"; // usa tu IP local real

export async function getLLMResponse(prompt, token) {
  try {
    const response = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, message: prompt }),
    });

    if (!response.ok) throw new Error("Fallo de red");

    const data = await response.json();
    return data.analysis;
  } catch (error) {
    console.error("Error en getLLMResponse:", error);
    throw error;
  }
}
