# Veri

Bu klasöre `MICRODADOS.csv` konur. Dosya 595 MB olduğu için git'e eklenmez (`.gitignore`).

## Kaynak

Espírito Santo eyaleti (Brezilya) COVID-19 paneli mikroverisi: 1.679.329 bildirim kaydı, Ocak 2020–Temmuz 2021 arası. Galo vd. (2022) bu dosyanın kopyasını Code Ocean kapsülünde yayımladı:

- Kapsül: https://codeocean.com/capsule/5590000
- DOI: 10.24433/CO.6430898.v1

## İndirme

1. Kapsül sayfasını aç (Code Ocean hesabı istenebilir).
2. Sol taraftaki dosya ağacında `data/MICRODADOS.csv` dosyasını seç.
3. **Download File**'a tıkla.
4. İnen dosyayı bu klasöre `data/MICRODADOS.csv` adıyla koy.

## Dosya biçimi

- Ayraç `;`, kodlama ISO-8859-1.
- Kullanılan sütunlar: `src/veri.py` içinde `OKUNACAK_SUTUNLAR`.
- Doğru dosyayı indirdiğini kontrol etmek için çalıştır:
  `python -m analiz.veri_ozeti`. Beklenen Febre dağılımı Não 1.134.433, Sim 540.919.
