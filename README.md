# 📊 SignalBot — Analista Financiero Cripto con IA

**SignalBot** es un sistema de análisis técnico automatizado para criptomonedas, potenciado por modelos de lenguaje (LLM) y datos en tiempo real.  
Ofrece **señales de trading cuantificables**, análisis estructurados y **asesoramiento profesional** a través de una interfaz móvil multiplataforma.

---

## 🚀 Estado actual: `v0.4` — MVP funcional y sólido

El proyecto ya cuenta con:

✅ Backend en producción (`FastAPI` + `Render`)  
✅ App móvil funcional (Expo / React Native)  
✅ Análisis inteligente en 3 modos (Lite / Pro / Advisor)  
✅ Contextualización por token (BTC, ETH, SOL...)  
✅ Registro de señales y estadísticas automáticas  
✅ Historial de conversación en modo Asesor  
✅ API conectada a DeepSeek (modelo LLM)

---

## 🧠 ¿Qué hace SignalBot?

> “No todos los usuarios necesitan leer gráficos. Algunos solo necesitan una respuesta clara.”

SignalBot resuelve eso.  
Puedes preguntarle sobre un token, y elige cómo te responde según el **modo**:

### 🟢 Modo LITE
> Señales rápidas, simples y accionables. Ideal para principiantes.  
Incluye: `LONG / SHORT / ESPERAR`, % de confianza, riesgo y timeframe.

### 🧠 Modo PRO
> Análisis técnico detallado y estructurado con secciones:
- Contexto del mercado
- Indicadores (RSI, EMAs, Volumen...)
- Estrategia sugerida
- Parámetros (TP, SL, Confianza, etc.)

### 👨‍🏫 Modo Asesor
> Un mentor financiero personalizado.  
Te responde con tono humano, empatía y claridad, usando contexto actual y noticias del token.

---

## 🛠️ Tecnologías utilizadas

| Capa        | Tecnologías                                     |
|-------------|-------------------------------------------------|
| Backend     | Python · FastAPI · DeepSeek API · CSV Logging  |
| Frontend    | React Native · Expo · AsyncStorage             |
| Hosting     | Render (backend)                               |
| Datos       | CoinMarketCap · CoinPaprika                    |
| Persistencia| Archivos `.csv` para señales, logs y sesiones  |

---

## 📦 Estructura del proyecto

llm-signalbot/

├── backend/

│ ├── main.py ← Endpoint /analyze + /logs

│ ├── logs/ ← Señales y sesiones registradas

│ ├── utils/tokens/ ← Contexto experto por token (btc.py, eth.py...)

│ └── deepseek_client.py ← Cliente LLM

├── frontend/

│ ├── screens/ ← ChatScreen, StatsScreen, LogsScreen, etc.

│ └── services/llmService.js ← Conexión con backend


---

## 📈 Estadísticas y trazabilidad

Cada análisis generado queda registrado en:
- `signals_lite.csv`
- `signals_pro.csv`
- `interactions_advisor.csv`

Además, la app muestra:
- 📜 Historial de señales
- 📊 Estadísticas globales: % confianza media, riesgo medio, tipo de señales

---

## 🧭 Roadmap versión `v0.5`

- 🎨 Mejora visual del chat (cards estructuradas, colores de estado)
- 🔄 Selector de token dinámico por análisis
- 🗞️ Integración de noticias y sentimiento por token
- 🔔 Notificaciones push (recordatorios, señales nuevas)
- 💰 Modo freemium o suscripción
- 🎓 Modo didáctico o tutoriales guiados

---

## 🤖 ¿Por qué SignalBot?

✔ Evita decisiones impulsivas  
✔ Reduce la complejidad de análisis técnico  
✔ Ofrece un sistema validable y cuantificable  
✔ Accesible, rápido y educativo

---

## 👨‍💻 Autor

**Desarrollado por [@tsmluky](https://github.com/tsmluky)**  
Un proyecto Indie Hacker creado desde cero con foco en funcionalidad real y automatización del análisis técnico.

---

> “SignalBot no es un oráculo. Es tu copiloto técnico, listo para ayudarte a ver mejor el mercado.”
