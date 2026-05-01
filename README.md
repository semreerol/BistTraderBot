# BIST Analiz Botu V2

Türkiye Borsası (BIST) hisseleri için teknik analiz yapan, piyasa rejimini yorumlayan ve tamamen GitHub Actions üzerinde çalışan bir Telegram botu.

---

## 🎯 Amaç

Bu bot, belirlenen BIST hisselerini yfinance üzerinden günlük olarak analiz eder.  
Teknik indikatörlere (EMA, RSI, MACD, ATR) ve piyasa rejimine dayalı bir skor hesaplar ve sonuçları Telegram'a raporlar.

> ⚠️ **Bu proje yatırım tavsiyesi değildir.** Sadece otomatik analiz ve takip amaçlıdır.

---

## 🚀 V2 Özellikleri Neler?

V2 ile beraber bota çok önemli özellikler eklendi:

1. **Piyasa Rejimi Analizi:** BIST100, BIST30 ve sektörel endekslerin teknik durumunu ölçer. Örneğin piyasa kötüyse hisselerin skorları da düşer (risk iştahı ölçümü).
2. **Relatif Güç (RS):** Hisselerin son 20 gündeki getirisini BIST100 ile karşılaştırarak "Endekse göre çok güçlü" gibi çıkarımlar yapar.
3. **Sinyal Geçmişi & Performans Takibi:** Botun ürettiği güçlü sinyaller (`score >= 65`) `data/signals_history.csv` dosyasına kaydedilir. Bot her çalıştığında, geçmiş sinyallerin 3, 7, 14 ve 30 günlük getirilerini ölçerek "Win Rate (Başarı Oranı)" ve ortalama getiri gibi verileri hesaplar.
4. **Otomatik Kayıt (GitHub Actions):** Her analiz sonrası oluşan yeni sinyaller ve performans verileri GitHub repo'ya otomatik olarak commit/push edilir.

---

## 📁 Proje Yapısı

```
bist/
├── main.py                    # Ana akış
├── config.py                  # Konfigürasyon
├── requirements.txt
├── README.md
├── data/
│   ├── symbols.json           # Takip edilen hisseler
│   ├── market_symbols.json    # Piyasa analizi için endeksler
│   └── signals_history.csv    # Otomatik oluşan sinyal/performans geçmişi
├── modules/
│   ├── price_fetcher.py       # yfinance veri çekme
│   ├── technicals.py          # Teknik analiz
│   ├── relative_strength.py   # Endekse göre rölatif güç
│   ├── market_regime.py       # Piyasa rejimi analizi
│   ├── performance_tracker.py # Sinyal geçmişi ve getiri hesaplama
│   ├── scorer.py              # Skor hesaplama
│   ├── report_builder.py      # Gelişmiş Telegram raporu formatlayıcı
│   └── telegram_sender.py     # Telegram mesaj gönderme
└── .github/
    └── workflows/
        └── run-bot.yml        # GitHub Actions zamanlama ve commit sistemi
```

---

## 🤖 Kurulum ve Kullanım

### 1. Telegram Bot Token & Chat ID
1. BotFather'dan token alın.
2. userinfobot ile Chat ID'nizi öğrenin.
3. GitHub reponuzda `Settings` > `Secrets and variables` > `Actions` kısmından şu secret'ları ekleyin:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

### 2. GitHub Actions İzinleri (ÖNEMLİ!)
Botun CSV dosyasını güncelleyip pushlayabilmesi için repo ayarlarından yazma izni vermeniz gerekir:
- Repo sayfasında **Settings** > Sol menüden **Actions** > **General**
- Sayfanın en altındaki **Workflow permissions** bölümünde:
- **`Read and write permissions`** seçeneğini işaretleyin ve kaydedin.

---

## ⏰ Otomatik Zamanlama

Bot her hafta içi aşağıdaki saatlerde otomatik çalışır (veya manuel çalıştırabilirsiniz):

| Türkiye Saati | UTC       |
|---------------|-----------|
| ~10:00        | 07:00     |
| ~18:30        | 15:30     |

---

## ➕ Yeni Hisse Ekleme

`data/symbols.json` dosyasına aşağıdaki formatta yeni bir satır ekleyebilirsiniz:

```json
{"symbol": "SASA.IS", "name": "Sasa Polyester", "sector": "Kimya"}
```

---

## 📊 V2 Skor Sistemi (100 Puan)

V2'de skorlar piyasa durumu ve hissenin gücüyle entegre edilmiştir.

| Kategori            | Max Puan |
|---------------------|----------|
| Trend               | 30       |
| Momentum            | 20       |
| Hacim               | 15       |
| Risk (Volatilite)   | 15       |
| Relatif Güç         | 15       |
| Piyasa Rejimi (Ek)  | -15 ile +10 arası|

| Sinyal      | Skor Aralığı |
|-------------|--------------|
| Güçlü İzle  | ≥ 80         |
| İzle        | ≥ 65         |
| Nötr        | ≥ 50         |
| Zayıf       | < 50         |

---

## 📝 Sinyal Geçmişi ve Performans Ölçümü Nasıl Çalışır?

Bot "İzle" veya "Güçlü İzle" (`score >= 65`) sinyali verdiği hisseleri aynı gün içinde `data/signals_history.csv` dosyasına `status="open"` olarak kaydeder.
Sonraki her çalışmasında bu açık sinyallerin giriş tarihinden bu yana ne kadar gün geçtiğine bakar (3, 7, 14, 30 gün) ve getiri/zarar yüzdelerini yazar.
30 gün sonunda sinyalin `status` değerini `"closed"` yapar ve maksimum getiri/düşüş oranlarını hesaplar. Böylece botun algoritmasının gerçekten çalışıp çalışmadığını somut verilerle Telegram üzerinden görebilirsiniz.
