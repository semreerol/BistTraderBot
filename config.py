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

# ── Sembol dosyası ────────────────────────────────────────────────────────────
SYMBOLS_FILE: str = os.path.join(os.path.dirname(__file__), "data", "symbols.json")
