"""
modules/relative_strength.py
----------------------------
Hisselerin endekse göre relatif gücünü hesaplar.
"""

from __future__ import annotations
import pandas as pd

def calculate_period_return(df: pd.DataFrame, period: int = 20) -> float | None:
    if df is None or df.empty or len(df) <= period:
        return None
    try:
        last_close = float(df.iloc[-1]["Close"])
        old_close = float(df.iloc[-(period+1)]["Close"])
        if old_close == 0: return None
        return ((last_close - old_close) / old_close) * 100
    except:
        return None

def analyze_relative_strength(stock_df: pd.DataFrame, benchmark_df: pd.DataFrame, period: int = 20) -> dict:
    stock_return = calculate_period_return(stock_df, period)
    benchmark_return = calculate_period_return(benchmark_df, period)
    
    if stock_return is None or benchmark_return is None:
        return {
            "stock_return": None,
            "benchmark_return": None,
            "relative_strength": None,
            "relative_strength_label": "Relatif güç hesaplanamadı",
            "relative_strength_score": 0
        }
        
    rs = stock_return - benchmark_return
    
    if rs >= 10:
        label = "Endekse göre çok güçlü"
        score = 15
    elif rs >= 5:
        label = "Endekse göre güçlü"
        score = 10
    elif rs >= 0:
        label = "Endekse paralel / hafif güçlü"
        score = 5
    elif rs >= -5:
        label = "Endeksten zayıf"
        score = -5
    else:
        label = "Endekse göre çok zayıf"
        score = -10
        
    return {
        "stock_return": round(stock_return, 2),
        "benchmark_return": round(benchmark_return, 2),
        "relative_strength": round(rs, 2),
        "relative_strength_label": label,
        "relative_strength_score": score
    }
