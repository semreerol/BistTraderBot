"""
modules/price_fetcher.py
------------------------
yfinance aracılığıyla hisse fiyat verisi çeker.
"""

from __future__ import annotations

import pandas as pd
import yfinance as yf

from config import DEFAULT_INTERVAL, DEFAULT_PERIOD


def fetch_price_data(
    symbol: str,
    period: str = DEFAULT_PERIOD,
    interval: str = DEFAULT_INTERVAL,
) -> pd.DataFrame | None:
    """
    Verilen sembol için yfinance'tan OHLCV verisi çeker.

    Parameters
    ----------
    symbol   : Yahoo Finance formatında sembol (örn. 'THYAO.IS')
    period   : Geçmişe dönük veri aralığı (örn. '6mo', '1y')
    interval : Veri frekansı (örn. '1d', '1h')

    Returns
    -------
    pd.DataFrame veya None (veri yoksa ya da hata oluşursa)
    """
    try:
        print(f"  [price_fetcher] Veri çekiliyor: {symbol} | period={period} | interval={interval}")

        ticker = yf.Ticker(symbol)
        df: pd.DataFrame = ticker.history(period=period, interval=interval)

        if df is None or df.empty:
            print(f"  [price_fetcher] UYARI: {symbol} için veri döndü ancak boş.")
            return None

        # Kolon isimlerini standartlaştır
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()

        # NaN satırlarını temizle
        df.dropna(subset=["Close"], inplace=True)

        if df.empty:
            print(f"  [price_fetcher] UYARI: {symbol} için NaN temizleme sonrası veri kalmadı.")
            return None

        print(f"  [price_fetcher] OK: {symbol} → {len(df)} satır veri alındı.")
        return df

    except Exception as exc:
        print(f"  [price_fetcher] HATA: {symbol} verisi çekilemedi → {exc}")
        return None
