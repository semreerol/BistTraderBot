"""
modules/performance_tracker.py
------------------------------
Sinyal geçmişini CSV olarak kaydeder ve açık sinyallerin performansını takip eder.
"""

from __future__ import annotations

import os
import csv
from datetime import datetime, date
import pandas as pd
from typing import Callable, Any

from config import PERFORMANCE_WINDOWS

CSV_FIELDNAMES = [
    "date", "symbol", "name", "sector", "signal", "score", "entry_price",
    "price_after_3d", "return_after_3d",
    "price_after_7d", "return_after_7d",
    "price_after_14d", "return_after_14d",
    "price_after_30d", "return_after_30d",
    "max_return_30d", "max_drawdown_30d",
    "status"
]

def ensure_signals_file_exists(file_path: str) -> None:
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()
        print(f"  [performance] {file_path} oluşturuldu.")

def load_signals_history(file_path: str) -> pd.DataFrame:
    if not os.path.exists(file_path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path, parse_dates=["date"])
        return df
    except Exception as exc:
        print(f"  [performance] CSV okuma hatası: {exc}")
        return pd.DataFrame()

def save_signal(file_path: str, signal_data: dict) -> None:
    ensure_signals_file_exists(file_path)
    today_str = date.today().strftime("%Y-%m-%d")
    symbol = signal_data["symbol"]

    try:
        df = load_signals_history(file_path)
        if not df.empty and "date" in df.columns and "symbol" in df.columns:
            if not df[(df["date"].dt.strftime("%Y-%m-%d") == today_str) & (df["symbol"] == symbol)].empty:
                print(f"  [performance] Sinyal zaten var, atlanıyor: {symbol}")
                return

        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            row = {
                "date": today_str,
                "symbol": symbol,
                "name": signal_data.get("name", ""),
                "sector": signal_data.get("sector", ""),
                "signal": signal_data.get("signal", ""),
                "score": signal_data.get("score", 0),
                "entry_price": signal_data.get("entry_price", 0.0),
                "status": "open"
            }
            writer.writerow(row)
            print(f"  [performance] Yeni sinyal kaydedildi: {symbol} - {signal_data.get('signal')}")
    except Exception as exc:
        print(f"  [performance] CSV yazma hatası: {exc}")

def update_signal_performance(file_path: str, price_fetcher_func: Callable) -> None:
    df = load_signals_history(file_path)
    if df.empty:
        return

    open_signals = df[df["status"] == "open"]
    if open_signals.empty:
        return

    print(f"  [performance] Açık sinyaller güncelleniyor: {len(open_signals)} adet.")
    
    updated_any = False
    
    for idx in open_signals.index:
        symbol = df.at[idx, "symbol"]
        entry_date = pd.to_datetime(df.at[idx, "date"]).date()
        entry_price = float(df.at[idx, "entry_price"])
        
        today = date.today()
        days_passed = (today - entry_date).days
        
        price_df = price_fetcher_func(symbol, period="3mo")
        if price_df is None or price_df.empty:
            continue
            
        price_df_after_entry = price_df[price_df.index.date > entry_date]
        
        for w in PERFORMANCE_WINDOWS:
            if days_passed >= w and pd.isna(df.at[idx, f"price_after_{w}d"]):
                target_date = entry_date + pd.Timedelta(days=w)
                valid_prices = price_df[(price_df.index.date >= target_date) & (price_df.index.date <= today)]
                if not valid_prices.empty:
                    p = valid_prices.iloc[0]["Close"]
                    df.at[idx, f"price_after_{w}d"] = round(float(p), 2)
                    df.at[idx, f"return_after_{w}d"] = round(((p - entry_price) / entry_price) * 100, 2)
                    updated_any = True
                else:
                    valid_before = price_df[(price_df.index.date <= target_date) & (price_df.index.date > entry_date)]
                    if not valid_before.empty:
                        p = valid_before.iloc[-1]["Close"]
                        df.at[idx, f"price_after_{w}d"] = round(float(p), 2)
                        df.at[idx, f"return_after_{w}d"] = round(((p - entry_price) / entry_price) * 100, 2)
                        updated_any = True
        
        if days_passed >= 30:
            if not price_df_after_entry.empty:
                max_p = price_df_after_entry["High"].max()
                min_p = price_df_after_entry["Low"].min()
                df.at[idx, "max_return_30d"] = round(((max_p - entry_price) / entry_price) * 100, 2)
                df.at[idx, "max_drawdown_30d"] = round(((min_p - entry_price) / entry_price) * 100, 2)
            df.at[idx, "status"] = "closed"
            updated_any = True

    if updated_any:
        df.to_csv(file_path, index=False)
        print("  [performance] CSV güncellendi.")

def get_performance_summary(file_path: str, recent_limit: int = 30) -> dict:
    df = load_signals_history(file_path)
    if df.empty:
        return {
            "total_signals": 0, "closed_signals": 0,
            "avg_return_7d": None, "avg_return_14d": None,
            "win_rate_7d": None, "win_rate_14d": None,
            "best_signal": None, "worst_signal": None
        }

    total_signals = len(df)
    closed_signals = len(df[df["status"] == "closed"])
    
    df_recent = df.tail(recent_limit)
    
    avg_7 = df_recent["return_after_7d"].mean() if "return_after_7d" in df_recent and not df_recent["return_after_7d"].dropna().empty else None
    avg_14 = df_recent["return_after_14d"].mean() if "return_after_14d" in df_recent and not df_recent["return_after_14d"].dropna().empty else None
    
    def calc_win_rate(col):
        if col not in df_recent: return None
        s = df_recent[col].dropna()
        if s.empty: return None
        return round((len(s[s > 0]) / len(s)) * 100, 2)
        
    wr_7 = calc_win_rate("return_after_7d")
    wr_14 = calc_win_rate("return_after_14d")
    
    returns_cols = ["return_after_30d", "return_after_14d", "return_after_7d", "return_after_3d"]
    best_val, worst_val = -float('inf'), float('inf')
    best_sym, worst_sym = "", ""
    
    for idx, row in df_recent.iterrows():
        for col in returns_cols:
            if col in df_recent and not pd.isna(row[col]):
                val = row[col]
                if val > best_val:
                    best_val = val
                    best_sym = row["symbol"]
                if val < worst_val:
                    worst_val = val
                    worst_sym = row["symbol"]
                break
                
    if best_val != -float('inf'):
        best_signal = {"symbol": best_sym, "return": round(best_val, 2)}
    else:
        best_signal = None
        
    if worst_val != float('inf'):
        worst_signal = {"symbol": worst_sym, "return": round(worst_val, 2)}
    else:
        worst_signal = None

    return {
        "total_signals": total_signals,
        "closed_signals": closed_signals,
        "avg_return_7d": round(avg_7, 2) if avg_7 is not None else None,
        "avg_return_14d": round(avg_14, 2) if avg_14 is not None else None,
        "win_rate_7d": wr_7,
        "win_rate_14d": wr_14,
        "best_signal": best_signal,
        "worst_signal": worst_signal
    }
