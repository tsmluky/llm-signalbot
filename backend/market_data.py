import os
import requests
from dotenv import load_dotenv

load_dotenv()

CMC_API_KEY = os.getenv("COINMARKETCAP_API_KEY")

# Mapeo manual (símbolo → slug o ID)
SYMBOL_MAP = {
    "eth": {"cmc": "ETH", "cp": "eth-ethereum"},
    "btc": {"cmc": "BTC", "cp": "btc-bitcoin"},
    "sol": {"cmc": "SOL", "cp": "sol-solana"},
    "matic": {"cmc": "MATIC", "cp": "matic-polygon"},
    "doge": {"cmc": "DOGE", "cp": "doge-dogecoin"},
    "ada": {"cmc": "ADA", "cp": "ada-cardano"},
    "dot": {"cmc": "DOT", "cp": "dot-polkadot"},
    "bnb": {"cmc": "BNB", "cp": "bnb-binance-coin"},
    "shib": {"cmc": "SHIB", "cp": "shib-shiba-inu"},
    "link": {"cmc": "LINK", "cp": "link-chainlink"},
    "ltc": {"cmc": "LTC", "cp": "ltc-litecoin"},
    "uni": {"cmc": "UNI", "cp": "uni-uniswap"},
    "avax": {"cmc": "AVAX", "cp": "avax-avalanche"},
    "op": {"cmc": "OP", "cp": "op-optimism"},
    "arb": {"cmc": "ARB", "cp": "arb-arbitrum"},
}

def get_market_data(symbol: str) -> dict:
    symbol = symbol.lower()
    mapping = SYMBOL_MAP.get(symbol)

    if not mapping:
        print(f"[❌] Token '{symbol}' no está mapeado.")
        return error_response(f"Token '{symbol}' no está mapeado.")

    try:
        print(f"[📡] Intentando con CoinMarketCap: {mapping['cmc']}")
        return fetch_from_coinmarketcap(mapping["cmc"])
    except Exception as e:
        print(f"[⚠️] CMC falló: {e}")
        try:
            print(f"[🔁] Reintentando con CoinPaprika: {mapping['cp']}")
            return fetch_from_coinpaprika(mapping["cp"])
        except Exception as e2:
            print(f"[❌] Paprika también falló: {e2}")
            return error_response("Todas las fuentes fallaron.")

def fetch_from_coinmarketcap(cmc_symbol: str) -> dict:
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        "X-CMC_PRO_API_KEY": CMC_API_KEY,
        "Accepts": "application/json",
    }
    params = {
        "symbol": cmc_symbol,
        "convert": "USD"
    }

    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()["data"][cmc_symbol]["quote"]["USD"]
    return {
        "price": round(data["price"], 4),
        "change_24h": round(data["percent_change_24h"], 2),
        "market_cap": round(data["market_cap"], 2),
        "volume_24h": round(data["volume_24h"], 2),
        "sentiment": "neutral"
    }

def fetch_from_coinpaprika(paprika_id: str) -> dict:
    url = f"https://api.coinpaprika.com/v1/tickers/{paprika_id}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    return {
        "price": round(data["quotes"]["USD"]["price"], 4),
        "change_24h": round(data["quotes"]["USD"]["percent_change_24h"], 2),
        "market_cap": round(data["quotes"]["USD"]["market_cap"], 2),
        "volume_24h": round(data["quotes"]["USD"]["volume_24h"], 2),
        "sentiment": "neutral"
    }

def error_response(msg):
    return {
        "price": None,
        "change_24h": None,
        "market_cap": None,
        "volume_24h": None,
        "sentiment": "neutral",
        "error": msg
    }
