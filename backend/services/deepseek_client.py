from __future__ import annotations
import httpx, asyncio
from typing import List, Dict

DEEPSEEK_API = "https://api.deepseek.com/v1/chat/completions"

class DeepSeekClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def chat(self, messages: List[Dict[str, str]], model: str = "deepseek-chat", temperature: float = 0.6, max_tokens: int = 800) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        timeout = httpx.Timeout(20.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(DEEPSEEK_API, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]

    def chat_sync(self, messages: List[Dict[str, str]], **kw) -> str:
        return asyncio.run(self.chat(messages, **kw))
