"""
main.py
-------
BIST Analiz Botu — Ana akış.

Çalışma sırası:
  1. symbols.json oku
  2. Her sembol için fiyat ver, teknik/temel/haber analizi yap, skor hesapla
  3. Sonuçları filtrele ve sırala
  4. Telegram'a rapor gönder
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

from config import (
    MAX_REPORTED_STOCKS,
    MIN_SCORE_TO_REPORT,
    SYMBOLS_FILE,
)
from modules.fundamentals import get_fundamental_analysis
from modules.news_fetcher import get_news_sentiment
from modules.price_fetcher import fetch_price_data
from modules.scorer import calculate_score
from modules.technicals import add_technical_indicators, analyze_technicals
from modules.telegram_sender import send_telegram_message


# ── Yardımcı fonksiyonlar ─────────────────────────────────────────────────────

def load_symbols(path: str) -> list[dict]:
    """symbols.json dosyasını okur ve döndürür."""
    try:
        with open(path, encoding="utf-8") as f:
            symbols = json.load(f)
        print(f"[main] {len(symbols)} sembol yüklendi.")
        return symbols
    except FileNotFoundError:
        print(f"[main] HATA: {path} bulunamadı.")
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"[main] HATA: symbols.json geçersiz JSON → {exc}")
        sys.exit(1)


def analyze_symbol(symbol_info: dict) -> dict | None:
    """
    Tek bir hisse için tam analiz pipeline'ını çalıştırır.

    Returns
    -------
    dict veya None (herhangi bir adımda kritik hata oluşursa)
    """
    symbol: str = symbol_info["symbol"]
    name: str = symbol_info["name"]
    sector: str = symbol_info.get("sector", "—")

    print(f"\n[main] → Analiz ediliyor: {symbol} ({name})")

    # 1. Fiyat verisi
    df = fetch_price_data(symbol)
    if df is None:
        print(f"[main] ATLANDI: {symbol} için fiyat verisi alınamadı.")
        return None

    # 2. Teknik indikatörler
    try:
        df = add_technical_indicators(df)
    except Exception as exc:
        print(f"[main] HATA: {symbol} indikatör hesaplaması başarısız → {exc}")
        return None

    # 3. Teknik analiz
    technical = analyze_technicals(df)
    if technical is None:
        print(f"[main] ATLANDI: {symbol} için teknik analiz üretilemedi.")
        return None

    # 4. Temel analiz (placeholder)
    fundamental = get_fundamental_analysis(symbol)

    # 5. Haber analizi (yfinance + Google News RSS)
    news = get_news_sentiment(symbol, name)

    # 6. Skor hesapla
    score_result = calculate_score(technical, fundamental, news)

    return {
        "symbol": symbol,
        "name": name,
        "sector": sector,
        "technical": technical,
        "fundamental": fundamental,
        "news": news,
        "score": score_result["score"],
        "signal": score_result["signal"],
        "score_breakdown": score_result["score_breakdown"],
    }


# ── Telegram mesaj formatlama ─────────────────────────────────────────────────

def format_report(results: list[dict], total_scanned: int) -> str:
    """
    Analiz sonuçlarını okunabilir Telegram mesajına dönüştürür.
    """
    now_str = datetime.now(tz=timezone.utc).strftime("%d.%m.%Y %H:%M UTC")

    header = (
        f"📊 <b>BIST Analiz Botu — Günlük Tarama</b>\n"
        f"🕐 {now_str}\n\n"
        f"Toplam taranan hisse: {total_scanned}\n"
        f"Raporlanan hisse: {len(results)}\n"
        f"{'─' * 30}\n\n"
    )

    if not results:
        return header + "Bugünkü taramada raporlanacak güçlü aday bulunamadı."

    body_parts: list[str] = []
    for i, r in enumerate(results, start=1):
        sym_short = r["symbol"].replace(".IS", "")
        price = r["technical"]["last_close"]
        news = r["news"]
        news_line = f"   Haberler    : {news['news_status']} ({news['news_score']}/100)\n"
        headlines = ""
        for h in news.get("latest_news", []):
            headlines += f"   📰 {h['title'][:90]} <i>({h['source']})</i>\n"

        block = (
            f"<b>{i}) {sym_short} — {r['name']}</b>\n"
            f"   Sektör      : {r['sector']}\n"
            f"   Skor        : {r['score']}/100\n"
            f"   Sinyal      : {r['signal']}\n"
            f"   Son Fiyat   : {price:.2f} TL\n"
            f"   Trend       : {r['technical']['trend_status']}\n"
            f"   Momentum    : {r['technical']['momentum_status']}\n"
            f"   Hacim       : {r['technical']['volume_status']}\n"
            f"   Risk        : {r['technical']['risk_status']}\n"
            + news_line
            + (headlines if headlines else "")
        )
        body_parts.append(block)

    footer = (
        "\n" + "─" * 30 + "\n"
        "⚠️ <i>Bu çıktı yatırım tavsiyesi değildir. "
        "Sadece otomatik analiz ve takip amaçlıdır.</i>"
    )

    return header + "\n".join(body_parts) + footer


# ── Ana akış ──────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 50)
    print(" BIST Analiz Botu başlatıldı")
    print("=" * 50)

    symbols = load_symbols(SYMBOLS_FILE)
    results: list[dict] = []

    for symbol_info in symbols:
        try:
            result = analyze_symbol(symbol_info)
            if result is not None:
                results.append(result)
        except Exception as exc:
            # Tek hisse hatası diğerlerini durdurmasın
            print(f"[main] BEKLENMEDIK HATA: {symbol_info.get('symbol')} → {exc}")

    total_scanned = len(symbols)

    # Sırala ve filtrele
    results.sort(key=lambda x: x["score"], reverse=True)
    filtered = [r for r in results if r["score"] >= MIN_SCORE_TO_REPORT]
    reported = filtered[:MAX_REPORTED_STOCKS]

    print(f"\n[main] Taranan: {total_scanned} | Filtrelenen: {len(filtered)} | Raporlanan: {len(reported)}")

    # Raporu oluştur ve gönder
    message = format_report(reported, total_scanned)
    print("\n[main] Telegram mesajı gönderiliyor...")
    success = send_telegram_message(message)

    if success:
        print("[main] ✅ Rapor başarıyla gönderildi.")
    else:
        print("[main] ❌ Rapor gönderilemedi veya kısmen gönderilemedi.")

    print("\n[main] Bot çalışması tamamlandı.")


if __name__ == "__main__":
    main()
