"""
modules/telegram_sender.py
--------------------------
Telegram Bot API üzerinden mesaj gönderir.
Uzun mesajları otomatik olarak böler.
"""

from __future__ import annotations

import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def split_message_if_needed(message: str, max_length: int = 3900) -> list[str]:
    """
    Verilen mesajı Telegram mesaj sınırına göre parçalara böler.

    Parameters
    ----------
    message    : Gönderilecek mesaj metni
    max_length : Parça başına maksimum karakter sayısı (varsayılan 3900)

    Returns
    -------
    list[str] : Mesaj parçaları
    """
    if len(message) <= max_length:
        return [message]

    parts: list[str] = []
    while message:
        if len(message) <= max_length:
            parts.append(message)
            break

        # Satır sınırında kesmek için geriye doğru newline ara
        split_at = message.rfind("\n", 0, max_length)
        if split_at == -1:
            split_at = max_length

        parts.append(message[:split_at].rstrip())
        message = message[split_at:].lstrip()

    return parts


def send_telegram_message(message: str) -> bool:
    """
    Telegram kanalına/grubuna mesaj gönderir.

    Token veya chat_id eksikse uyarı verir ama uygulamayı çökertmez.

    Parameters
    ----------
    message : Gönderilecek mesaj

    Returns
    -------
    bool : En az bir parça başarıyla gönderilebildiyse True
    """
    if not TELEGRAM_BOT_TOKEN:
        print("  [telegram] HATA: TELEGRAM_BOT_TOKEN ayarlanmamış.")
        return False

    if not TELEGRAM_CHAT_ID:
        print("  [telegram] HATA: TELEGRAM_CHAT_ID ayarlanmamış.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    parts = split_message_if_needed(message)
    all_success = True

    for i, part in enumerate(parts, start=1):
        try:
            print(f"  [telegram] Mesaj gönderiliyor ({i}/{len(parts)})...")
            response = requests.post(
                url,
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": part,
                    "parse_mode": "HTML",
                },
                timeout=15,
            )

            if response.status_code == 200:
                print(f"  [telegram] OK: Parça {i}/{len(parts)} gönderildi.")
            else:
                print(
                    f"  [telegram] HATA: Parça {i} gönderilemedi. "
                    f"Status={response.status_code}, Body={response.text[:200]}"
                )
                all_success = False

        except requests.exceptions.Timeout:
            print(f"  [telegram] HATA: Parça {i} için bağlantı zaman aşımına uğradı.")
            all_success = False
        except Exception as exc:
            print(f"  [telegram] HATA: Parça {i} gönderilemedi → {exc}")
            all_success = False

    return all_success
