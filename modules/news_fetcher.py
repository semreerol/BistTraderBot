"""
modules/news_fetcher.py
-----------------------
Gerçek haber analizi modülü.
Kaynaklar:
  1. yfinance ticker.news  — Yahoo Finance haberleri
  2. Google News RSS        — Türkçe finans haberleri
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus

import requests
import yfinance as yf

# ── Sentiment anahtar kelimeleri ──────────────────────────────────────────────

POSITIVE_TR = [
    "artış", "yükseldi", "yükseliş", "rekor", "kâr", "kar", "kazanç",
    "büyüme", "güçlü", "anlaşma", "ihracat", "sipariş", "temettü",
    "ihale kazandı", "sözleşme", "al önerisi", "pozitif", "toparlanma",
]

NEGATIVE_TR = [
    "düşüş", "geriledi", "zarar", "kayıp", "kriz", "dava", "soruşturma",
    "ceza", "zayıf", "uyarı", "risk", "endişe", "borç", "temerrüt",
    "satış baskısı", "değer kaybı", "çöküş",
]

POSITIVE_EN = [
    "rise", "gain", "profit", "record", "strong", "deal", "agreement",
    "growth", "beat", "exceed", "dividend", "upgrade", "outperform",
    "surge", "rally", "boost", "award", "contract", "win",
]

NEGATIVE_EN = [
    "fall", "loss", "decline", "weak", "warning", "risk", "lawsuit",
    "investigation", "penalty", "drop", "downgrade", "crash", "plunge",
    "debt", "default", "concern",
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


# ── Yardımcı fonksiyonlar ─────────────────────────────────────────────────────

def _score_headline(title: str) -> int:
    """Başlığı anahtar kelime eşleşmesiyle puanlar. -1, 0 veya +1 döner."""
    t = title.lower()
    pos = sum(1 for kw in POSITIVE_TR + POSITIVE_EN if kw in t)
    neg = sum(1 for kw in NEGATIVE_TR + NEGATIVE_EN if kw in t)
    if pos > neg:
        return 1
    if neg > pos:
        return -1
    return 0


def _fetch_yfinance_news(symbol: str, days: int = 7) -> list[dict]:
    """yfinance üzerinden Yahoo Finance haberlerini çeker."""
    try:
        ticker = yf.Ticker(symbol)
        raw_news = ticker.news or []
        cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days)
        results = []
        for item in raw_news:
            pub_ts = item.get("providerPublishTime", 0)
            if pub_ts and datetime.fromtimestamp(pub_ts, tz=timezone.utc) < cutoff:
                continue
            title = item.get("title", "").strip()
            if title:
                results.append({
                    "title": title,
                    "publisher": item.get("publisher", "Yahoo Finance"),
                    "sentiment": _score_headline(title),
                })
        return results
    except Exception as exc:
        print(f"  [news] yfinance haber hatası: {exc}")
        return []


def _fetch_google_news_rss(query: str, max_items: int = 5) -> list[dict]:
    """Google News RSS üzerinden Türkçe haber çeker."""
    try:
        url = (
            f"https://news.google.com/rss/search"
            f"?q={quote_plus(query)}&hl=tr&gl=TR&ceid=TR:tr"
        )
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        if resp.status_code != 200:
            return []
        root = ET.fromstring(resp.content)
        channel = root.find("channel")
        if channel is None:
            return []
        results = []
        for item in channel.findall("item")[:max_items]:
            title_el = item.find("title")
            source_el = item.find("source")
            title = (title_el.text or "").strip()
            source = (source_el.text or "Google News").strip() if source_el is not None else "Google News"
            if title:
                results.append({
                    "title": title,
                    "publisher": source,
                    "sentiment": _score_headline(title),
                })
        return results
    except Exception as exc:
        print(f"  [news] Google News RSS hatası: {exc}")
        return []


def _compute_score(news_items: list[dict]) -> int:
    """Haber listesinden 0–100 arası sentiment skoru üretir."""
    if not news_items:
        return 50
    avg = sum(i["sentiment"] for i in news_items) / len(news_items)
    return max(10, min(90, int(50 + avg * 40)))


def _sentiment_label(score: int) -> str:
    if score >= 70:
        return "Olumlu haber akışı"
    elif score >= 55:
        return "Hafif olumlu haberler"
    elif score >= 45:
        return "Nötr haber akışı"
    elif score >= 30:
        return "Hafif olumsuz haberler"
    else:
        return "Olumsuz haber akışı"


# ── Ana fonksiyon ─────────────────────────────────────────────────────────────

def get_news_sentiment(symbol: str, name: str = "") -> dict:
    """
    Verilen sembol için haber sentiment analizi yapar.

    Kaynaklar: yfinance (İngilizce) + Google News RSS (Türkçe)

    Returns
    -------
    dict : {news_status, news_score, is_active, latest_news}
    """
    print(f"  [news] Haberler çekiliyor: {symbol}")

    yf_news = _fetch_yfinance_news(symbol, days=7)

    search_query = f"{name} hisse" if name else symbol.replace(".IS", "") + " borsa"
    gn_news = _fetch_google_news_rss(search_query, max_items=5)

    # Tekrar eden başlıkları filtrele
    seen: set[str] = set()
    unique: list[dict] = []
    for item in yf_news + gn_news:
        key = item["title"][:60].lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)

    score = _compute_score(unique)
    status = _sentiment_label(score)

    print(f"  [news] {len(unique)} haber | Skor: {score} | {status}")

    return {
        "news_status": status,
        "news_score": score,
        "is_active": True,
        "latest_news": [
            {"title": i["title"][:120], "source": i["publisher"]}
            for i in unique[:3]
        ],
    }
