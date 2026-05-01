"""
config.py
---------
Merkezi konfigürasyon modülü.
Tüm ayarlar environment variable'lardan veya sabit değerlerden okunur.
"""

import os
from dotenv import load_dotenv

# .env dosyası varsa yükle (lokal geliştirme için)
load_dotenv()

# ── Telegram ──────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

# ── yfinance veri ayarları ────────────────────────────────────────────────────
DEFAULT_PERIOD: str = "6mo"    # Geçmişe dönük veri aralığı
DEFAULT_INTERVAL: str = "1d"   # Veri frekansı

# ── Raporlama filtreleri ──────────────────────────────────────────────────────
MIN_SCORE_TO_REPORT: int = 60   # Bu skorun altındaki hisseler rapora dahil edilmez
MAX_REPORTED_STOCKS: int = 10   # Raporda gösterilecek maksimum hisse sayısı

# ── Sembol dosyaları ──────────────────────────────────────────────────────────
SYMBOLS_FILE: str = os.path.join(os.path.dirname(__file__), "data", "symbols.json")
MARKET_SYMBOLS_FILE: str = os.path.join(os.path.dirname(__file__), "data", "market_symbols.json")
SIGNALS_HISTORY_FILE: str = os.path.join(os.path.dirname(__file__), "data", "signals_history.csv")

# ── Performans Takibi ve Analiz ───────────────────────────────────────────────
PERFORMANCE_WINDOWS: list[int] = [3, 7, 14, 30]
MIN_SIGNAL_SCORE_TO_SAVE: int = 65

# ── Piyasa Rejimi ─────────────────────────────────────────────────────────────
MARKET_REGIME_SYMBOL: str = "XU100.IS"
MARKET_REGIME_SCORE_POSITIVE: int = 10
MARKET_REGIME_SCORE_NEUTRAL: int = 0
MARKET_REGIME_SCORE_NEGATIVE: int = -15

# ── Relatif Güç ───────────────────────────────────────────────────────────────
RELATIVE_STRENGTH_BENCHMARK: str = "XU100.IS"
RELATIVE_STRENGTH_PERIOD: int = 20
