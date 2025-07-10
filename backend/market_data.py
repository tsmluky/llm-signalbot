# backend/market_data.py

import requests

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
COINGECKO_VOLUME_URL = "https://api.coingecko.com/api/v3/coins/{}"

# Mapeo de símbolos → IDs oficiales de CoinGecko
SYMBOL_TO_ID = {
    "eth": "ethereum",
    "btc": "bitcoin",
    "sol": "solana",
    "doge": "dogecoin",
    "ada": "cardano",
    "dot": "polkadot",
    "matic": "polygon",
    "bnb": "binancecoin",
    "shib": "shiba-inu",
    "link": "chainlink",
    "ltc": "litecoin",
    "uni": "uniswap",
    "avax": "avalanche-2",
    "op": "optimism",
    "arb": "arbitrum",
}

def get_market_data(token_symbol: str) -> dict:
    """
    Obtiene precio, cambio 24h, market cap y volumen desde CoinGecko.
    Usa el ID oficial del token.
    """
    coingecko_id = SYMBOL_TO_ID.get(token_symbol.lower())
    if not coingecko_id:
        raise ValueError(f"Token '{token_symbol}' no está mapeado a un ID de CoinGecko")

    try:
        # Precio, cambio 24h y market cap
        price_resp = requests.get(
            COINGECKO_URL,
            params={
                "ids": coingecko_id,
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_change": "true"
            },
            timeout=10
        )
        price_resp.raise_for_status()
        price_data = price_resp.json().get(coingecko_id, {})

        # Volumen 24h desde el endpoint extendido
        volume_resp = requests.get(
            COINGECKO_VOLUME_URL.format(coingecko_id),
            params={"localization": "false", "tickers": "false", "market_data": "true"},
            timeout=10
        )
        volume_resp.raise_for_status()
        volume_data = volume_resp.json()
        volume_24h = volume_data.get("market_data", {}).get("total_volume", {}).get("usd", None)

        return {
            "price": round(price_data.get("usd", 0), 4),
            "change_24h": round(price_data.get("usd_24h_change", 0), 2),
            "market_cap": round(price_data.get("usd_market_cap", 0), 2),
            "volume_24h": round(volume_24h, 2) if volume_24h else None
        }

    except Exception as e:
        print(f"[❌] Error al obtener datos de CoinGecko: {e}")
        return {
            "price": None,
            "change_24h": None,
            "market_cap": None,
            "volume_24h": None,
            "error": str(e)
        }
