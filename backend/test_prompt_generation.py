from utils.format_prompt_lite import build_prompt as build_prompt_lite
from utils.format_prompt import build_prompt as build_prompt_pro
from utils.format_prompt_assist import build_prompt as build_prompt_assist

def simulate_prompt(mode="lite", token="ETH", message="¿Es buen momento para entrar?", market_data=None):
    if market_data is None:
        market_data = {
            "price": "3120.50",
            "volume_24h": "25M",
            "change_24h": "+2.4",
            "market_cap": "190B",
            "sentiment": "neutral"
        }

    if mode == "lite":
        prompt = build_prompt_lite(token, message, market_data)
    elif mode == "pro":
        prompt = build_prompt_pro(token, message, market_data)
    elif mode == "advisor":
        prompt = build_prompt_assist(token, message, market_data)
    else:
        raise ValueError(f"Modo desconocido: {mode}")

    print(f"\n--- Prompt generado ({mode.upper()}) ---\n")
    print(prompt)

if __name__ == "__main__":
    # Cambia estos valores para probar diferentes escenarios
    simulate_prompt(
        mode="advisor",  # lite / pro / advisor
        token="ETH",
        message="¿Qué opinás sobre ETH? Estoy viendo buen volumen pero no sé si holdear.",
        market_data={
            "price": "3178.20",
            "volume_24h": "37M",
            "change_24h": "+4.1",
            "market_cap": "205B",
            "sentiment": "alcista"
        }
    )
