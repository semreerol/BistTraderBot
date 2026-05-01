"""
modules/market_regime.py
------------------------
Piyasa rejimi analizi yapar (örn. BIST100 endeksi üzerinden).
"""

from __future__ import annotations
import json
from typing import Callable

from modules.technicals import calculate_ema, calculate_rsi
from config import MARKET_REGIME_SCORE_POSITIVE, MARKET_REGIME_SCORE_NEUTRAL, MARKET_REGIME_SCORE_NEGATIVE, MARKET_REGIME_SYMBOL

def analyze_single_market_symbol(symbol: str, name: str, price_fetcher_func: Callable) -> dict | None:
    df = price_fetcher_func(symbol, period="3mo")
    if df is None or df.empty or len(df) < 50:
        return None
        
    df = df.copy()
    df["EMA20"] = calculate_ema(df["Close"], 20)
    df["EMA50"] = calculate_ema(df["Close"], 50)
    df["RSI14"] = calculate_rsi(df["Close"], 14)
    df["Volume_MA20"] = df["Volume"].rolling(window=20).mean()
    
    last = df.iloc[-1]
    last_close = float(last["Close"])
    ema20 = float(last["EMA20"])
    ema50 = float(last["EMA50"])
    rsi = float(last["RSI14"])
    volume = float(last["Volume"])
    vol_ma = float(last["Volume_MA20"])
    
    # Trend
    if last_close > ema20 and ema20 > ema50:
        trend = "positive"
        trend_label = "Pozitif piyasa"
    elif last_close > ema20 and ema20 <= ema50:
        trend = "neutral"
        trend_label = "Toparlanma eğilimi"
    elif last_close < ema20 and ema20 < ema50:
        trend = "negative"
        trend_label = "Negatif piyasa"
    else:
        trend = "neutral"
        trend_label = "Kararsız piyasa"
        
    if trend == "positive":
        score_impact = MARKET_REGIME_SCORE_POSITIVE
    elif trend == "negative":
        score_impact = MARKET_REGIME_SCORE_NEGATIVE
    else:
        score_impact = MARKET_REGIME_SCORE_NEUTRAL
        
    if volume > vol_ma * 1.2:
        volume_status = "Hacimli"
    else:
        volume_status = "Ortalama hacim"
        
    return {
        "symbol": symbol,
        "name": name,
        "last_close": last_close,
        "trend": trend,
        "trend_label": trend_label,
        "rsi": rsi,
        "volume_status": volume_status,
        "score_impact": score_impact
    }

def analyze_market_regime(market_symbols_file: str, price_fetcher_func: Callable) -> dict:
    try:
        with open(market_symbols_file, encoding="utf-8") as f:
            market_symbols = json.load(f)
    except Exception as exc:
        print(f"  [market_regime] HATA: market_symbols.json okunamadı -> {exc}")
        return {"overall_label": "Piyasa analizi başarısız", "overall_score_impact": 0, "main_regime": None, "all_markets": []}
        
    all_markets = []
    main_regime = None
    
    for item in market_symbols:
        res = analyze_single_market_symbol(item["symbol"], item["name"], price_fetcher_func)
        if res:
            all_markets.append(res)
            if item["symbol"] == MARKET_REGIME_SYMBOL:
                main_regime = res
                
    if main_regime:
        if main_regime["trend"] == "positive":
            overall_label = "Risk iştahı pozitif"
        elif main_regime["trend"] == "negative":
            overall_label = "Risk iştahı zayıf"
        else:
            overall_label = "Piyasa kararsız"
        overall_score_impact = main_regime["score_impact"]
    else:
        overall_label = "Piyasa kararsız"
        overall_score_impact = 0

    return {
        "main_regime": main_regime,
        "all_markets": all_markets,
        "overall_label": overall_label,
        "overall_score_impact": overall_score_impact
    }
