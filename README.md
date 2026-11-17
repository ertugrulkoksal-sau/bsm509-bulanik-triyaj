# Bulanık COVID-19 triyaj modelinin yeniden üretimi

BSM509 Bulanık Sistemler dönem projesi.

Gerçeklenen çalışma:

> Galo, N. R., Roriz Junior, M. P., Pereira, R. P. T. (2022). A fuzzy approach to support decision-making in the triage process for suspected COVID-19 patients in Brazil. *Applied Soft Computing*, 129, 109626. https://doi.org/10.1016/j.asoc.2022.109626

- Tam metin: https://pmc.ncbi.nlm.nih.gov/articles/PMC9487152/
- Yazarların kapsülü (ÜF parametreleri, veri): https://codeocean.com/capsule/5590000, DOI 10.24433/CO.6430898.v1

Model, dört girdiden (yaşamsal bulgular VS, nefes darlığı BD, risk faktörleri RF, diğer belirtiler RS) hastalığın şiddetini (SV, 0–1) hesaplayan 36 kurallı bir Mamdani sistemi. SV ≥ 0,75 ise hastaneye yatış önerilir. Bu depoda:

- Mamdani motoru sıfırdan, yalnız NumPy ile yazıldı. scikit-fuzzy yalnız testlerde, doğrulama için kullanılıyor.
- Makaledeki sonuçlar Espírito Santo eyaletinin 1,68 milyon kayıtlık gerçek verisiyle yeniden üretildi.
- Uyuşmayan değerler ve modelin sınırları `sonuclar/bulgular.md` içinde (B0–B7).
- Canlı demo: Streamlit.

Yazarların not defteri kopyalanmadı. Kurallar makaleden (Tablo 3), ÜF parametreleri ve veri kapsülden alındı, kod sıfırdan yazıldı.

## Kurulum

Python 3.11 ya da üstü gerekir. Önce depoyu indir:

```bash
git clone https://github.com/ertugrulkoksal-sau/bsm509-bulanik-triyaj.git
```

### macOS

```bash
cd bsm509-bulanik-triyaj
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
cd bsm509-bulanik-triyaj
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Windows konsolunda Türkçe karakterler bozuk görünürse önce `$env:PYTHONIOENCODING = "utf-8"` çalıştır.

## Veri

`data/MICRODADOS.csv` (595 MB) git'e eklenmez. İndirme adımları [data/README.md](data/README.md)'de:

1. https://codeocean.com/capsule/5590000 sayfasını aç.
2. `data/MICRODADOS.csv` dosyasını seç, **Download File**'a tıkla.
3. İnen dosyayı `data/MICRODADOS.csv` olarak kaydet.

Kontrol: `python -m analiz.veri_ozeti` ön işleme sonrası Febre dağılımını Não 1.134.433 / Sim 540.919 olarak vermeli. Bu sayılar kapsülle aynı.

## Çalıştırma

Bütün komutlar proje klasöründen, sanal ortam etkinken çalıştırılır.

| Ne | Komut | Süre (yaklaşık) |
|---|---|---|
| Testler | `pytest` | 1 dk |
| Canlı demo | `streamlit run app.py` | — |
| Veri özeti, kapsül kontrolü | `python -m analiz.veri_ozeti` | 20 sn |
| Tablo 5'in 15 vakası | `python -m analiz.tablo5` | 1 sn |
| SV dağılımı, yatış oranı, ölüm vakaları | `python -m analiz.yeniden_uretim` | 30 sn |
| Kural ateşlenme sayımı (B3) | `python -m analiz.kural_ateslenme` | 20 sn |
| Yüzey ve duyarlılık grafikleri (B5) | `python -m analiz.yuzey_duyarlilik` | 20 sn |
| Bulanık ve kesin model karşılaştırması (B6) | `python -m analiz.bulanik_kesin` | 2 dk |
| Eşik analizi (B7) | `python -m analiz.esik_analizi` | 30 sn |

Analiz betiklerinin çıktıları (csv, png, txt) `sonuclar/` klasörüne yazılır. Veri dosyası olmadan yalnız testler, `tablo5`, `yuzey_duyarlilik` ve demo çalışır.

## Sonuçlar: makale ve bizim değerler

| Ölçü | Makale / kapsül | Bizim |
|---|---|---|
| Toplam kayıt | 1.679.329 | 1.679.329 |
| Ön işleme sonrası Febre, Não / Sim | 1.134.433 / 540.919 | 1.134.433 / 540.919 |
| SV değerleri | 0,1 / 0,5 / 0,9 | 0,1 / 0,5 / 0,9 |
| Yatış önerilen kayıt, eşik 0,75 | %26,8 | %26,84 |
| Yatış önerilen kayıt, eşik 0,50 | "biraz artıyor" | %27,39 |
| COVID-19 / diğer nedenli ölüm | 11.510 / 3.432 | 11.510 / 3.432 |
| Ölümlerde fiili yatış, COVID / diğer | %63,29 / %47,15 | %63,29 / %47,15 |
| Yatırılmayan COVID ölümü, fiili | %37 | %36,7 |
| Yatırılmayan COVID ölümü, model (0,75) | %18 | %17,5 |
| Tablo 5, 15 vaka | — | 12 uyumlu, 3 çelişkili (B2) |

Öne çıkan bulgular (ayrıntı ve kaynak çıktılar: [sonuclar/bulgular.md](sonuclar/bulgular.md)):

- **B0:** Kapsülün sayıları, `-` filtresine sigara sütunu katılmadığında birebir tutuyor.
- **B1, B2:** Tablo 5'teki 0,163 / 0,873 değerleri kapsülün ÜF'leriyle elde edilemiyor. 5, 13 ve 15. vakaların sonucu Tablo 3'teki kurallarla çelişiyor.
- **B3:** Gerçek veride girdiler ikili. Ateş (VS = 2) "düşük" kümesinde kaldığı için sonucu hiç değiştirmiyor. 36 kuralın yalnız 1–8'i ateşleniyor.
- **B4:** Makaledeki ölüm oranları yalnız yatış bilgisi bilinen kayıtlara göre hesaplanmış.
- **B5:** BD terimleri örtüşmüyor. BD = 0,25 ve 0,75'te hiçbir kural ateşlenmiyor.
- **B6:** Gerçek veride bulanık model, aynı kuralların kesin sürümüyle 1.675.352 kaydın hepsinde aynı sonucu veriyor.
- **B7:** Gerçek veride yalnız üç anlamlı eşik var. Model kayıtların %33,65'ine yatış öneriyor; fiili oran %2,30.

## Klasör yapısı

```
src/            model ve motor
  uyelik.py       trapmf, trimf
  model.py        değişkenler, ÜF parametreleri, 36 kural
  mamdani.py      bulanıklaştır → ateşle → kırp → birleştir → durulaştır
  kesin_model.py  aynı kuralların kesin sürümü
  veri.py         CSV okuma ve ön işleme
  makale_degerleri.py  makaledeki sayılar (karşılaştırma için)
analiz/         sonuçları üreten betikler
tests/          pytest testleri (scikit-fuzzy karşılaştırması dahil)
sonuclar/       tablolar, grafikler, bulgular.md
docs/           kod anlatım rehberi
app.py          Streamlit demo
data/           MICRODADOS.csv buraya (git'e girmez)
```

Kodun satır satır açıklaması, bir vakanın elle hesabı ve sunumda sorulabilecek sorular: [docs/kod-anlatim-rehberi.md](docs/kod-anlatim-rehberi.md).

## Lisans ve kaynak

- Veri: Espírito Santo eyaleti COVID-19 paneli, yazarların kapsülündeki kopya.
- Yazarların kodu Apache 2.0 lisanslı. Bu depodaki kod onun kopyası değil; yalnız model parametreleri ve veri kaynak gösterilerek kullanıldı.
