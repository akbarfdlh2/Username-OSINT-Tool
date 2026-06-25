"""
Core checker — async HTTP requests pakai httpx + semaphore buat rate limiting.
"""

import asyncio
from typing import AsyncIterator

import httpx

from .platforms import PLATFORMS

# User-agent biar gak kena block basic
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Akses diblokir / tak bisa dipastikan — BUKAN berarti user tidak ada.
BLOCKED_CODES = {401, 403, 429}
# User dipastikan tidak ada.
ABSENT_CODES = {404, 410}


class UsernameChecker:
    def __init__(self, timeout: int = 10, concurrency: int = 50):
        self.timeout = timeout
        self.concurrency = concurrency
        self.platforms = PLATFORMS

    async def check_all(self, username: str) -> AsyncIterator[dict]:
        """Yield hasil satu per satu saat tiap platform selesai dicek."""
        semaphore = asyncio.Semaphore(self.concurrency)
        limits = httpx.Limits(
            max_connections=self.concurrency,
            max_keepalive_connections=self.concurrency,
        )

        async with httpx.AsyncClient(
            headers=HEADERS,
            timeout=self.timeout,
            follow_redirects=True,
            verify=False,  # skip SSL errors biar gak banyak gagal
            limits=limits,
        ) as client:
            tasks = [
                asyncio.ensure_future(
                    self._check_one(client, semaphore, username, platform, config)
                )
                for platform, config in self.platforms.items()
            ]
            for coro in asyncio.as_completed(tasks):
                yield await coro

    async def _check_one(
        self,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        username: str,
        platform: str,
        config: dict,
    ) -> dict:
        url = config["url"].format(username)
        result = {
            "platform": platform,
            "url": url,
            "category": config.get("category", "Other"),
            "found": False,
            "status": "not_found",  # found | not_found | blocked | error
            "status_code": None,
            "error": None,
        }

        async with semaphore:
            try:
                resp = await client.get(url)
                result["status_code"] = resp.status_code
                result["found"] = self._evaluate(resp, config)
                if result["found"]:
                    result["status"] = "found"
                elif resp.status_code in BLOCKED_CODES:
                    result["status"] = "blocked"
                else:
                    result["status"] = "not_found"
            except httpx.TimeoutException:
                result["error"], result["status"] = "timeout", "error"
            except httpx.ConnectError:
                result["error"], result["status"] = "connection_error", "error"
            except Exception as e:
                result["error"], result["status"] = str(e)[:80], "error"

        return result

    @staticmethod
    def _evaluate(resp: httpx.Response, config: dict) -> bool:
        """True kalau username kemungkinan ADA di platform ini."""
        code = resp.status_code
        method = config.get("check", "status_code")

        if method == "content":
            if code in ABSENT_CODES:
                return False
            text = resp.text
            if "content_present" in config and config["content_present"] not in text:
                return False
            if "content_absent" in config and config["content_absent"] in text:
                return False
            return code < 400

        # method == "status_code"
        not_found_code = config.get("not_found_code", 404)
        if code == not_found_code or code in ABSENT_CODES or code in BLOCKED_CODES:
            return False
        if 300 <= code < 400:  # redirect biasanya ke login/home → anggap tidak ada
            return False
        return code < 400
