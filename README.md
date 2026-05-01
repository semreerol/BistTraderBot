# BIST Analiz Botu

Türkiye Borsası (BIST) hisseleri için teknik analiz yapan, sunucusuz ve tamamen GitHub Actions üzerinde çalışan bir Telegram botu.

---

## 🎯 Amaç

Bu bot, belirlenen BIST hisselerini yfinance üzerinden günlük olarak analiz eder.  
Teknik indikatörlere (EMA, RSI, MACD, ATR) dayalı bir skor hesaplar ve sonuçları Telegram'a raporlar.

> ⚠️ **Bu proje yatırım tavsiyesi değildir.** Sadece otomatik analiz ve takip amaçlıdır.

---

## 📁 Proje Yapısı

```
bist/
├── main.py                    # Ana akış
├── config.py                  # Konfigürasyon
├── requirements.txt
├── README.md
├── data/
│   └── symbols.json           # Takip edilen hisseler
├── modules/
│   ├── price_fetcher.py       # yfinance veri çekme
│   ├── technicals.py          # Teknik analiz (EMA, RSI, MACD, ATR)
│   ├── fundamentals.py        # Temel analiz (placeholder)
│   ├── news_fetcher.py        # Haber/KAP analizi (placeholder)
│   ├── scorer.py              # Skor hesaplama
│   └── telegram_sender.py     # Telegram mesaj gönderme
└── .github/
    └── workflows/
        └── run-bot.yml        # GitHub Actions zamanlama
```

---

## 🤖 Telegram Bot Oluşturma

### 1. BotFather'dan Token Al

1. Telegram'da [@BotFather](https://t.me/BotFather) botuna git.
2. `/newbot` komutunu gönder.
3. Bot için bir isim ve kullanıcı adı belirle (`...Bot` ile bitmeli).
4. BotFather'ın verdiği **HTTP API Token**'ı kopyala.  
   Örnek: `7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 2. Chat ID'ni Bul

**Kişisel mesajlaşma için:**
1. [@userinfobot](https://t.me/userinfobot) botuna `/start` gönder.
2. Sana kendi Chat ID'ni verecektir. Örnek: `123456789`

**Grup/Kanal için:**
1. Botu gruba/kanala ekle ve admin yap.
2. Tarayıcıda şu URL'yi ziyaret et:  
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. JSON çıktısında `"chat": {"id": -XXXXXXXXXX}` değerini bul.  
   Grup ID'leri genellikle negatiftir: `-1001234567890`

---

## 🔐 GitHub Secrets Ayarlama

1. GitHub'da repoyu aç → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** butonuna tıkla.
3. Aşağıdaki iki secret'ı ekle:

| Secret Adı            | Değer                        |
|-----------------------|------------------------------|
| `TELEGRAM_BOT_TOKEN`  | BotFather'dan aldığın token  |
| `TELEGRAM_CHAT_ID`    | Telegram Chat/Grup ID'in     |

---

## ▶️ GitHub Actions — Manuel Çalıştırma

1. GitHub'da repoyu aç → **Actions** sekmesine git.
2. Sol menüden **BIST Analiz Botu** workflow'unu seç.
3. **Run workflow** butonuna tıkla.
4. `Run workflow` ile başlat.

---

## ⏰ Otomatik Zamanlama

Bot her hafta içi aşağıdaki saatlerde otomatik çalışır:

| Türkiye Saati | UTC       |
|---------------|-----------|
| ~10:00        | 07:00     |
| ~18:30        | 15:30     |

> Not: GitHub Actions cron'u UTC üzerinden çalışır.  
> Türkiye UTC+3 olduğu için değerler buna göre ayarlanmıştır.

---

## ➕ Yeni Hisse Ekleme

`data/symbols.json` dosyasına aşağıdaki formatta yeni bir satır ekle:

```json
{"symbol": "SASA.IS", "name": "Sasa Polyester", "sector": "Kimya"}
```

Semboller Yahoo Finance formatında olmalıdır: `HISSEADI.IS`

---

## 🔧 Lokal Test

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# .env dosyası oluştur (lokal için)
echo "TELEGRAM_BOT_TOKEN=senin_tokenin" > .env
echo "TELEGRAM_CHAT_ID=senin_chat_idin" >> .env

# Botu çalıştır
python main.py
```

---

## 📊 Skor Sistemi (100 puan)

| Kategori  | Ağırlık |
|-----------|---------|
| Trend     | 35 puan |
| Momentum  | 25 puan |
| Hacim     | 20 puan |
| Risk      | 20 puan |

| Sinyal      | Skor Aralığı |
|-------------|--------------|
| Güçlü İzle | ≥ 80         |
| İzle        | ≥ 65         |
| Nötr        | ≥ 50         |
| Zayıf       | < 50         |

---

## 🔮 Gelecek Planlar

- [ ] Temel analiz modülü (KAP finansalları, F/K, PD/DD)
- [ ] Haber/KAP duyuru sentiment analizi
- [ ] Daha fazla BIST hissesi
- [ ] Haftalık özet rapor
- [ ] Hisse detay komutu (Telegram inline sorgu)
