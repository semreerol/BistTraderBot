"""
modules/fundamentals.py
-----------------------
Temel analiz modülü — şimdilik iskelet (placeholder).
İleride KAP, finansal tablolar ve değerleme rasyoları eklenecek.
"""

from __future__ import annotations


def get_fundamental_analysis(symbol: str) -> dict:
    """
    Verilen sembol için temel analiz sonuçlarını döndürür.

    Bu modül henüz aktif değil; placeholder veriler döndürür.

    Parameters
    ----------
    symbol : Yahoo Finance formatında sembol (örn. 'THYAO.IS')

    Returns
    -------
    dict : Temel analiz sonuçları
    """
    # TODO: KAP finansalları, F/K, PD/DD, büyüme oranları vb. eklenecek
    return {
        "valuation_status": "Temel analiz modülü henüz aktif değil",
        "fundamental_score": 0,
        "details": [],
    }
