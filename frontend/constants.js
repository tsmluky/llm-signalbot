// constants.js

// 🧪 LOCALHOST para desarrollo
//export const API_BASE = "http://localhost:8000";
export const API_BASE = "https://signalbot-api.onrender.com"

// ✅ ENDPOINTS corregidos
export const API_ANALYZE = `${API_BASE}/analyze`;
export const API_SIGNALS = `${API_BASE}/logs`;  // esto generará: /logs/lite/eth, etc.
export const API_STATS = `${API_BASE}/stats_lite`;       // ← correcto para StatsScreen
