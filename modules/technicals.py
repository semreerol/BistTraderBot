"""
modules/technicals.py
---------------------
Teknik analiz modülü.
EMA, RSI, MACD, ATR indikatörlerini hesaplar ve analiz üretir.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# ── Yardımcı hesaplama fonksiyonları ─────────────────────────────────────────

def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential Moving Average hesaplar."""
    return series.ewm(span=period, adjust=False).mean()


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index (RSI) hesaplar.
    Wilder'ın düzeltilmiş EMA yöntemi kullanılır.
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(close: pd.Series) -> tuple[pd.Series, pd.Series]:
    """
    MACD ve Signal Line hesaplar.

    Returns
    -------
    (macd_line, signal_line)
    """
    ema12 = calculate_ema(close, 12)
    ema26 = calculate_ema(close, 26)
    macd_line = ema12 - ema26
    signal_line = calculate_ema(macd_line, 9)
    return macd_line, signal_line


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Average True Range (ATR) hesaplar.
    True Range = max(High-Low, |High-PrevClose|, |Low-PrevClose|)
    """
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    prev_close = close.shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    atr = tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    return atr


# ── Tüm indikatörleri DataFrame'e ekle ───────────────────────────────────────

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verilen OHLCV DataFrame'ine tüm teknik indikatörleri ekler.

    Eklenen kolonlar:
        EMA20, EMA50, RSI14, MACD, MACD_Signal,
        ATR14, Volume_MA20, High_20, Low_20
    """
    df = df.copy()

    df["EMA20"] = calculate_ema(df["Close"], 20)
    df["EMA50"] = calculate_ema(df["Close"], 50)
    df["RSI14"] = calculate_rsi(df["Close"], 14)

    macd_line, signal_line = calculate_macd(df["Close"])
    df["MACD"] = macd_line
    df["MACD_Signal"] = signal_line

    df["ATR14"] = calculate_atr(df, 14)
    df["Volume_MA20"] = df["Volume"].rolling(window=20).mean()
    df["High_20"] = df["High"].rolling(window=20).max()
    df["Low_20"] = df["Low"].rolling(window=20).min()

    return df


# ── Ana analiz fonksiyonu ─────────────────────────────────────────────────────

def analyze_technicals(df: pd.DataFrame) -> dict | None:
    """
    İndikatörler eklenmiş DataFrame'den teknik analiz sonucu üretir.

    Parameters
    ----------
    df : add_technical_indicators() çıktısı

    Returns
    -------
    dict veya None (veri yetersizse)
    """
    if df is None or df.empty:
        return None

    # İndikatörlerin hesaplanmış olması için yeterli satır kontrolü
    if len(df) < 50:
        print("  [technicals] UYARI: Yeterli veri yok (min 50 satır gerekli).")
        return None

    last = df.iloc[-1]

    # Zorunlu alanların NaN kontrolü
    required_fields = ["Close", "EMA20", "EMA50", "RSI14", "MACD", "MACD_Signal", "ATR14", "Volume", "Volume_MA20"]
    for field in required_fields:
        if pd.isna(last.get(field)):
            print(f"  [technicals] UYARI: '{field}' değeri NaN, hisse atlanıyor.")
            return None

    last_close: float = float(last["Close"])
    ema20: float = float(last["EMA20"])
    ema50: float = float(last["EMA50"])
    rsi: float = float(last["RSI14"])
    macd: float = float(last["MACD"])
    macd_signal: float = float(last["MACD_Signal"])
    atr: float = float(last["ATR14"])
    volume: float = float(last["Volume"])
    volume_ma20: float = float(last["Volume_MA20"])

    # ── Trend durumu ──────────────────────────────────────────────────────────
    if last_close > ema20 and ema20 > ema50:
        trend_status = "Güçlü yükseliş trendi"
    elif last_close > ema20 and ema20 <= ema50:
        trend_status = "Toparlanma eğilimi"
    elif last_close < ema20 and ema20 < ema50:
        trend_status = "Zayıf düşüş trendi"
    else:
        trend_status = "Kararsız trend"

    # ── Momentum durumu ───────────────────────────────────────────────────────
    if rsi < 30:
        momentum_status = "Aşırı satım bölgesi"
    elif rsi < 50:
        momentum_status = "Zayıf momentum"
    elif rsi < 70:
        momentum_status = "Pozitif momentum"
    else:
        momentum_status = "Aşırı alım bölgesi"

    # ── Hacim durumu ──────────────────────────────────────────────────────────
    if volume > volume_ma20 * 1.5:
        volume_status = "Güçlü hacim artışı"
    elif volume > volume_ma20:
        volume_status = "Ortalama üstü hacim"
    else:
        volume_status = "Zayıf hacim"

    # ── Risk / Volatilite durumu ──────────────────────────────────────────────
    volatility_ratio = atr / last_close if last_close > 0 else 0
    if volatility_ratio > 0.05:
        risk_status = "Yüksek volatilite"
    elif volatility_ratio > 0.03:
        risk_status = "Orta volatilite"
    else:
        risk_status = "Düşük volatilite"

    return {
        "last_close": round(last_close, 2),
        "ema20": round(ema20, 2),
        "ema50": round(ema50, 2),
        "rsi": round(rsi, 2),
        "macd": round(macd, 4),
        "macd_signal": round(macd_signal, 4),
        "atr": round(atr, 2),
        "volume": volume,
        "volume_ma20": round(volume_ma20, 0),
        "trend_status": trend_status,
        "momentum_status": momentum_status,
        "volume_status": volume_status,
        "risk_status": risk_status,
    }
