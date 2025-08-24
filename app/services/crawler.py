from __future__ import annotations

import asyncio
import re
from typing import Dict, List, Any

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import trafilatura


async def _auto_scroll(page, steps: int = 12, delay_sec: float = 0.8) -> None:
    for _ in range(steps):
        await page.mouse.wheel(0, 12000)
        await asyncio.sleep(delay_sec)


def _extract_with_heuristics(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    raw_text = soup.get_text(" ", strip=True)

    headings = [h.get_text(" ", strip=True) for h in soup.select("h1,h2,h3,h4,h5,h6")]
    items = [li.get_text(" ", strip=True) for li in soup.select("li")[:200]]

    name_like = re.compile(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+){1,3}\b")

    party_candidates: List[Dict[str, Any]] = []
    for h in headings:
        if any(k in h.lower() for k in ("party", "alliance", "front", "league")) and len(h) <= 80:
            party_candidates.append({"name": h, "abbrev": None, "logo_url": None, "description": None})

    candidate_candidates: List[Dict[str, Any]] = []
    for text in set(headings + items):
        if name_like.search(text) and 3 <= len(text) <= 80:
            candidate_candidates.append({"full_name": text, "party_guess": None, "constituency_guess": None, "photo_url": None, "bio": None})

    seen = set()
    dedup_parties = []
    for p in party_candidates:
        key = p["name"]
        if key and key not in seen:
            seen.add(key)
            dedup_parties.append(p)

    seen = set()
    dedup_candidates = []
    for c in candidate_candidates:
        key = c["full_name"]
        if key and key not in seen:
            seen.add(key)
            dedup_candidates.append(c)

    cleaned = trafilatura.extract(html) or ""

    return {
        "parties": dedup_parties[:100],
        "candidates": dedup_candidates[:250],
        "raw_text_sample": cleaned[:5000] if cleaned else raw_text[:5000],
    }


async def crawl_and_extract(url: str) -> Dict[str, Any]:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        await _auto_scroll(page, steps=14, delay_sec=0.7)
        await page.wait_for_timeout(1200)
        html = await page.content()
        await browser.close()

    entities = _extract_with_heuristics(html)
    return {"html": html, "entities": entities}
