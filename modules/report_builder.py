"""
modules/report_builder.py
-------------------------
Telegram rapor mesajını formatlar.
"""

from __future__ import annotations

def format_float(value: float | None, decimals: int = 2) -> str:
    if value is None:
        return "-"
    try:
        if isinstance(value, float) and value != value: # check NaN
            return "-"
        return f"{value:.{decimals}f}"
    except:
        return "-"

def build_market_regime_section(market_regime_analysis: dict | None) -> str:
    if not market_regime_analysis or not market_regime_analysis.get("all_markets"):
        return "🌍 Piyasa Rejimi: Analiz yapılamadı\n"
        
    overall = market_regime_analysis.get("overall_label", "-")
    sec = f"🌍 <b>Piyasa Rejimi</b>\nGenel Durum: {overall}\n\n"
    
    for m in market_regime_analysis.get("all_markets", []):
        sec += f"{m['name']}: {m['trend_label']}\n"
        
    return sec + "\n"

def build_performance_section(performance_summary: dict | None) -> str:
    if not performance_summary or performance_summary.get("total_signals", 0) == 0:
        return "📈 <b>Sinyal Performansı</b>\nHenüz yeterli sinyal geçmişi yok.\n\n"
        
    tot = performance_summary.get("total_signals", 0)
    cls = performance_summary.get("closed_signals", 0)
    avg_7 = format_float(performance_summary.get("avg_return_7d"))
    wr_7 = format_float(performance_summary.get("win_rate_7d"), 1)
    
    best = performance_summary.get("best_signal")
    worst = performance_summary.get("worst_signal")
    
    best_str = f"{best['symbol']} %{format_float(best['return'])}" if best else "-"
    worst_str = f"{worst['symbol']} %{format_float(worst['return'])}" if worst else "-"
    
    sec = (
        f"📈 <b>Sinyal Performansı</b>\n"
        f"Toplam sinyal: {tot}\n"
        f"Kapanmış sinyal: {cls}\n"
        f"Ortalama 7g getiri: %{avg_7}\n"
        f"7g başarı oranı: %{wr_7}\n"
        f"En iyi: {best_str}\n"
        f"En kötü: {worst_str}\n\n"
    )
    return sec

def build_stock_report_section(results: list[dict]) -> str:
    if not results:
        return "Bugünkü taramada raporlanacak güçlü aday bulunamadı.\n"
        
    body_parts = []
    for i, r in enumerate(results, start=1):
        sym_short = r["symbol"].replace(".IS", "")
        price = r["technical"]["last_close"]
        rs_lbl = r.get("relative_strength", {}).get("relative_strength_label", "-")
        rs_val = format_float(r.get("relative_strength", {}).get("relative_strength", 0))
        
        block = (
            f"<b>{i}) {sym_short} - {r['name']}</b>\n"
            f"Skor: {r['score']}/100 | Sinyal: {r['signal']}\n"
            f"Son Fiyat: {price:.2f} TL\n"
            f"Trend: {r['technical']['trend_status']}\n"
            f"Momentum: {r['technical']['momentum_status']}\n"
            f"Hacim: {r['technical']['volume_status']}\n"
            f"Risk: {r['technical']['risk_status']}\n"
            f"Relatif Güç: {rs_lbl} (%{rs_val})\n"
        )
        body_parts.append(block)
        
    return "🟢 <b>Güçlü Adaylar</b>\n\n" + "\n".join(body_parts)

def build_full_report(results: list[dict], market_regime_analysis: dict, performance_summary: dict, total_scanned: int) -> str:
    from datetime import datetime, timezone
    now_str = datetime.now(tz=timezone.utc).strftime("%d.%m.%Y %H:%M UTC")
    
    header = (
        f"📊 <b>BIST Analiz Botu - V2 Günlük Radar</b>\n"
        f"🕐 {now_str}\n\n"
        f"Taranan hisse: {total_scanned}\n"
        f"Raporlanan hisse: {len(results)}\n"
        f"{'─' * 30}\n\n"
    )
    
    regime_sec = build_market_regime_section(market_regime_analysis)
    perf_sec = build_performance_section(performance_summary)
    stocks_sec = build_stock_report_section(results)
    
    footer = (
        "\n" + "─" * 30 + "\n"
        "⚠️ <i>Bu çıktı yatırım tavsiyesi değildir. "
        "Sadece otomatik analiz ve takip amaçlıdır.</i>"
    )
    
    return header + regime_sec + perf_sec + stocks_sec + footer
