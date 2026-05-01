"""
modules/scorer.py
-----------------
100 üzerinden skor hesaplar ve sinyal üretir.

Haber modülü aktif olduğunda ağırlıklar yeniden dağıtılır:
  - Aktif   : Trend 28 + Momentum 20 + Hacim 16 + Risk 16 + Haberler 20 = 100
  - Pasif   : Trend 35 + Momentum 25 + Hacim 20 + Risk 20              = 100
"""

from __future__ import annotations

# ── Teknik ağırlık tabloları (haber modülü PASIF) ────────────────────────────

TREND_SCORES: dict[str, int] = {
    "Güçlü yükseliş trendi": 35,
    "Toparlanma eğilimi": 25,
    "Kararsız trend": 15,
    "Zayıf düşüş trendi": 5,
}

MOMENTUM_SCORES: dict[str, int] = {
    "Pozitif momentum": 25,
    "Zayıf momentum": 12,
    "Aşırı satım bölgesi": 15,
    "Aşırı alım bölgesi": 10,
}

VOLUME_SCORES: dict[str, int] = {
    "Güçlü hacim artışı": 20,
    "Ortalama üstü hacim": 14,
    "Zayıf hacim": 6,
}

RISK_SCORES: dict[str, int] = {
    "Düşük volatilite": 20,
    "Orta volatilite": 12,
    "Yüksek volatilite": 5,
}

# ── Teknik ağırlık tabloları (haber modülü AKTİF) ───────────────────────────

TREND_SCORES_N: dict[str, int] = {
    "Güçlü yükseliş trendi": 28,
    "Toparlanma eğilimi": 20,
    "Kararsız trend": 12,
    "Zayıf düşüş trendi": 4,
}

MOMENTUM_SCORES_N: dict[str, int] = {
    "Pozitif momentum": 20,
    "Zayıf momentum": 10,
    "Aşırı satım bölgesi": 12,
    "Aşırı alım bölgesi": 8,
}

VOLUME_SCORES_N: dict[str, int] = {
    "Güçlü hacim artışı": 16,
    "Ortalama üstü hacim": 11,
    "Zayıf hacim": 5,
}

RISK_SCORES_N: dict[str, int] = {
    "Düşük volatilite": 16,
    "Orta volatilite": 10,
    "Yüksek volatilite": 4,
}


def _signal(score: int) -> str:
    if score >= 80:
        return "Güçlü İzle"
    elif score >= 65:
        return "İzle"
    elif score >= 50:
        return "Nötr"
    return "Zayıf"


def calculate_score(
    technical_analysis: dict,
    fundamental_analysis: dict,
    news_analysis: dict,
) -> dict:
    """
    Teknik + haber analizlerini birleştirerek toplam skor üretir.

    Returns
    -------
    dict : {score, signal, score_breakdown}
    """
    trend_key = technical_analysis.get("trend_status", "")
    mom_key = technical_analysis.get("momentum_status", "")
    vol_key = technical_analysis.get("volume_status", "")
    risk_key = technical_analysis.get("risk_status", "")

    news_active: bool = news_analysis.get("is_active", False)

    if news_active:
        trend_s = TREND_SCORES_N.get(trend_key, 0)
        mom_s = MOMENTUM_SCORES_N.get(mom_key, 0)
        vol_s = VOLUME_SCORES_N.get(vol_key, 0)
        risk_s = RISK_SCORES_N.get(risk_key, 0)
        # news_score (0-100) → 0-20 puan
        news_raw = news_analysis.get("news_score", 50)
        news_s = int(round(news_raw * 0.20))
    else:
        trend_s = TREND_SCORES.get(trend_key, 0)
        mom_s = MOMENTUM_SCORES.get(mom_key, 0)
        vol_s = VOLUME_SCORES.get(vol_key, 0)
        risk_s = RISK_SCORES.get(risk_key, 0)
        news_s = 0

    total = trend_s + mom_s + vol_s + risk_s + news_s

    return {
        "score": total,
        "signal": _signal(total),
        "score_breakdown": {
            "trend": trend_s,
            "momentum": mom_s,
            "volume": vol_s,
            "risk": risk_s,
            "news": news_s,
        },
    }
