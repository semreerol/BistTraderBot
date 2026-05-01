"""
modules/scorer.py
-----------------
100 üzerinden skor hesaplar ve sinyal üretir. (V2)
"""

from __future__ import annotations

TREND_SCORES = {
    "Güçlü yükseliş trendi": 30,
    "Toparlanma eğilimi": 22,
    "Kararsız trend": 12,
    "Zayıf düşüş trendi": 3,
}

MOMENTUM_SCORES = {
    "Pozitif momentum": 20,
    "Zayıf momentum": 10,
    "Aşırı satım bölgesi": 12,
    "Aşırı alım bölgesi": 8,
}

VOLUME_SCORES = {
    "Güçlü hacim artışı": 15,
    "Ortalama üstü hacim": 10,
    "Zayıf hacim": 4,
}

RISK_SCORES = {
    "Düşük volatilite": 15,
    "Orta volatilite": 10,
    "Yüksek volatilite": 3,
}

def _signal(score: int) -> str:
    if score >= 80: return "Güçlü İzle"
    elif score >= 65: return "İzle"
    elif score >= 50: return "Nötr"
    return "Zayıf"

def calculate_score(
    technical_analysis: dict,
    fundamental_analysis: dict,
    news_analysis: dict,
    market_regime_analysis: dict | None = None,
    relative_strength_analysis: dict | None = None
) -> dict:
    
    trend_s = TREND_SCORES.get(technical_analysis.get("trend_status", ""), 0)
    mom_s = MOMENTUM_SCORES.get(technical_analysis.get("momentum_status", ""), 0)
    vol_s = VOLUME_SCORES.get(technical_analysis.get("volume_status", ""), 0)
    risk_s = RISK_SCORES.get(technical_analysis.get("risk_status", ""), 0)
    
    rs_s = relative_strength_analysis.get("relative_strength_score", 0) if relative_strength_analysis else 0
    mr_s = market_regime_analysis.get("overall_score_impact", 0) if market_regime_analysis else 0
    
    fund_s = 0 # Placeholder
    news_s = 0 # Placeholder
    
    total = trend_s + mom_s + vol_s + risk_s + rs_s + mr_s + fund_s + news_s
    
    # Clamp 0-100
    total = max(0, min(100, total))
    
    return {
        "score": total,
        "signal": _signal(total),
        "score_breakdown": {
            "trend": trend_s,
            "momentum": mom_s,
            "volume": vol_s,
            "risk": risk_s,
            "relative_strength": rs_s,
            "market_regime": mr_s,
            "fundamental": fund_s,
            "news": news_s
        }
    }
