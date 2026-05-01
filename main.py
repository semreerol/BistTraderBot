"""
main.py
-------
BIST Analiz Botu V2 — Ana akış.

Çalışma sırası:
  1. signals_history.csv performans analizi / güncelleme
  2. Piyasa rejimi analizi (BIST100, BIST30 vb.)
  3. BIST100 benchmark verisinin çekilmesi
  4. Hisse taraması, teknik analiz, relatif güç ve skor hesaplama
  5. Sinyallerin CSV'ye kaydedilmesi
  6. Raporun hazırlanıp Telegram'a gönderilmesi
"""

from __future__ import annotations

import json
import sys

from config import (
    MAX_REPORTED_STOCKS,
    MIN_SCORE_TO_REPORT,
    MIN_SIGNAL_SCORE_TO_SAVE,
    SYMBOLS_FILE,
    MARKET_SYMBOLS_FILE,
    SIGNALS_HISTORY_FILE,
    RELATIVE_STRENGTH_BENCHMARK,
    RELATIVE_STRENGTH_PERIOD
)
from modules.fundamentals import get_fundamental_analysis
from modules.news_fetcher import get_news_sentiment
from modules.price_fetcher import fetch_price_data
from modules.scorer import calculate_score
from modules.technicals import add_technical_indicators, analyze_technicals
from modules.telegram_sender import send_telegram_message

from modules.performance_tracker import ensure_signals_file_exists, update_signal_performance, get_performance_summary, save_signal
from modules.market_regime import analyze_market_regime
from modules.relative_strength import analyze_relative_strength
from modules.report_builder import build_full_report


def load_symbols(path: str) -> list[dict]:
    try:
        with open(path, encoding="utf-8") as f:
            symbols = json.load(f)
        print(f"[main] {len(symbols)} sembol yüklendi.")
        return symbols
    except Exception as exc:
        print(f"[main] HATA: {path} yüklenemedi -> {exc}")
        sys.exit(1)

def analyze_symbol(symbol_info: dict, benchmark_df, market_regime) -> dict | None:
    symbol: str = symbol_info["symbol"]
    name: str = symbol_info["name"]
    sector: str = symbol_info.get("sector", "—")

    print(f"\n[main] → Analiz ediliyor: {symbol} ({name})")

    df = fetch_price_data(symbol)
    if df is None:
        print(f"[main] ATLANDI: {symbol} için fiyat verisi alınamadı.")
        return None

    try:
        df = add_technical_indicators(df)
    except Exception as exc:
        print(f"[main] HATA: {symbol} indikatör hesaplaması başarısız → {exc}")
        return None

    technical = analyze_technicals(df)
    if technical is None:
        print(f"[main] ATLANDI: {symbol} için teknik analiz üretilemedi.")
        return None
        
    rs_analysis = analyze_relative_strength(df, benchmark_df, RELATIVE_STRENGTH_PERIOD)
    fundamental = get_fundamental_analysis(symbol)
    news = get_news_sentiment(symbol, name)

    score_result = calculate_score(technical, fundamental, news, market_regime, rs_analysis)

    return {
        "symbol": symbol,
        "name": name,
        "sector": sector,
        "technical": technical,
        "relative_strength": rs_analysis,
        "fundamental": fundamental,
        "news": news,
        "score": score_result["score"],
        "signal": score_result["signal"],
        "score_breakdown": score_result["score_breakdown"],
    }


def main() -> None:
    print("=" * 50)
    print(" BIST Analiz Botu V2 başlatıldı")
    print("=" * 50)

    # 1. Performance Tracker Updates
    print("[main] Geçmiş sinyaller güncelleniyor...")
    ensure_signals_file_exists(SIGNALS_HISTORY_FILE)
    update_signal_performance(SIGNALS_HISTORY_FILE, fetch_price_data)
    perf_summary = get_performance_summary(SIGNALS_HISTORY_FILE)

    # 2. Market Regime Analysis
    print("\n[main] Piyasa rejimi analiz ediliyor...")
    market_regime = analyze_market_regime(MARKET_SYMBOLS_FILE, fetch_price_data)

    # 3. Benchmark Data
    print(f"\n[main] Benchmark verisi çekiliyor ({RELATIVE_STRENGTH_BENCHMARK})...")
    benchmark_df = fetch_price_data(RELATIVE_STRENGTH_BENCHMARK)

    # 4. Hisse taraması
    symbols = load_symbols(SYMBOLS_FILE)
    results: list[dict] = []

    for symbol_info in symbols:
        try:
            result = analyze_symbol(symbol_info, benchmark_df, market_regime)
            if result is not None:
                results.append(result)
                
                # 5. Sinyal kaydetme
                if result["score"] >= MIN_SIGNAL_SCORE_TO_SAVE:
                    save_signal(SIGNALS_HISTORY_FILE, {
                        "symbol": result["symbol"],
                        "name": result["name"],
                        "sector": result["sector"],
                        "signal": result["signal"],
                        "score": result["score"],
                        "entry_price": result["technical"]["last_close"]
                    })
        except Exception as exc:
            print(f"[main] BEKLENMEDIK HATA: {symbol_info.get('symbol')} → {exc}")

    total_scanned = len(symbols)

    results.sort(key=lambda x: x["score"], reverse=True)
    filtered = [r for r in results if r["score"] >= MIN_SCORE_TO_REPORT]
    reported = filtered[:MAX_REPORTED_STOCKS]

    print(f"\n[main] Taranan: {total_scanned} | Filtrelenen: {len(filtered)} | Raporlanan: {len(reported)}")

    # 6. Raporlama
    message = build_full_report(reported, market_regime, perf_summary, total_scanned)
    print("\n[main] Telegram mesajı gönderiliyor...")
    success = send_telegram_message(message)

    if success:
        print("[main] ✅ Rapor başarıyla gönderildi.")
    else:
        print("[main] ❌ Rapor gönderilemedi veya kısmen gönderilemedi.")

    print("\n[main] Bot çalışması tamamlandı.")

if __name__ == "__main__":
    main()
