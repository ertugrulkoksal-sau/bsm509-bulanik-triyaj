# Kod anlatım rehberi

Bu belge sunumda kodu açıklamak için hazırlandı. Üç bölümden oluşuyor: dosyaların ve fonksiyonların ne yaptığı, Mamdani adımlarının iki örnek vaka üzerinden elle hesabı ve sorulabilecek 10 soru.

---

## 1. Dosyalar ve fonksiyonlar

Veri akışı tek yönlü:

```
model.py (parametreler, kurallar)
    │
uyelik.py ──► mamdani.py ──► veri.py ──► analiz/*.py ──► sonuclar/
                  │
                  ├──► kesin_model.py (karşılaştırma)
                  └──► app.py (demo)
```

### `src/uyelik.py`: üyelik fonksiyonları

| Fonksiyon | Ne yapar |
|---|---|
| `yukselen_kenar(x, a, b)` | a'dan b'ye 0'dan 1'e çıkan doğru: `(x - a) / (b - a)`, 0–1 arasına kırpılır. `a == b` ise kenar dikeydir: x ≥ a için 1. |
| `dusen_kenar(x, c, d)` | c'den d'ye 1'den 0'a inen doğru: `(d - x) / (d - c)`. `c == d` ise x ≤ c için 1. |
| `trapmf(x, a, b, c, d)` | Yamuk = iki kenarın küçüğü (`np.minimum`). Kenarlar 0–1 arasında kırpıldığı için ortası kendiliğinden 1 olur. |
| `trimf(x, a, b, c)` | Üçgen = tepesi tek noktaya inmiş yamuk: `trapmf(x, a, b, b, c)`. |
| `uyelik_hesapla(x, tip, parametreler)` | Model tablosundaki `("trap", [...])` / `("tri", [...])` kaydını doğru fonksiyona yönlendirir. |

Dikey kenar neden ayrı ele alınıyor: `trapmf[0, 0, 4, 5]`'te a = b = 0 olduğu için `(x - a) / (b - a)` sıfıra bölme olurdu.

### `src/model.py`: modelin tanımı (kod değil, veri)

| Ad | İçerik |
|---|---|
| `GIRDILER` | Dört girdi; her birinin evreni ve terimleri (ÜF tipi + parametreler). Parametreler kapsülden. |
| `CIKTI` | SV'nin üç terimi: mild trimf[0, 0, 0,3], moderate trimf[0,2, 0,5, 0,8], severe trimf[0,7, 1, 1]. |
| `CIKTI_EVRENI` | 0–1 arası 1001 nokta (0,001 adım). Çıktı kümeleri bu noktalarda hesaplanır. |
| `KURALLAR` | Makale Tablo 3: 36 satır, her satır `(VS, BD, RF, RS, SV)` terimleri. 3 × 3 × 2 × 2 = 36. |
| `GIRDI_SIRASI` | `["VS", "BD", "RF", "RS"]`: kurallardaki sütun sırası. |
| `YATIS_ESIGI` | 0,75. |

### `src/mamdani.py`: motor

| Fonksiyon | Mamdani adımı | Ne yapar |
|---|---|---|
| `bulaniklastir(girdiler)` | 1. Bulanıklaştırma | Her girdinin her terimdeki üyelik derecesini sözlük olarak döndürür. |
| `kural_gucu(kural, dereceler)` | 2. Kural ateşleme | Kuralın dört koşulunun derecelerinin **en küçüğü** (VE = min). |
| `kirp(cikti_terimi, guc)` | 3. Çıkarım | Kuralın çıktı kümesini güç yüksekliğinde keser: `np.minimum(küme, güç)`. |
| `birlestir(kirpilmis_kumeler)` | 4. Birleştirme | Kırpılmış kümelerin nokta nokta **en büyüğü** (max). |
| `agirlik_merkezi(evren, kume)` | 5. Durulaştırma | `∫x·μ(x)dx / ∫μ(x)dx`, integraller `np.trapezoid` (yamuk kuralı) ile. Alan 0 ise NaN. |
| `cikarim(vs, bd, rf, rs)` | hepsi | 1–5'i sırayla çağırır; ara sonuçları da döndürür (demo bunları çizer). Gücü 0 olan kural kırpılmaz, çünkü sonuca katkısı yok. |
| `siddet(vs, bd, rf, rs)` | — | Yalnız SV'yi döndürür. |

### `src/kesin_model.py`: aynı kuralların kesin sürümü

| Ad | Ne yapar |
|---|---|
| `SINIRLAR` | Her girdinin terimler arası sınırı: VS 4,5 ve 6,5; BD 0,25 ve 0,75; RF/RS 0,5. Bunlar bulanık modelde en yüksek üyelikli terimin değiştiği noktalar. |
| `kesin_terim(degisken, x)` | Girdiyi tek bir terime atar (üyelik 0 ya da 1). |
| `kesin_kural(vs, bd, rf, rs)` | Dört terimle eşleşen tek kuralın numarası. |
| `kesin_siddet(...)` | O kuralın çıktı kümesinin ağırlık merkezi: 0,1 / 0,5 / 0,9. |

### `src/veri.py`: veri hattı

| Fonksiyon | Ne yapar |
|---|---|
| `oku(dosya_yolu)` | CSV'den yalnız gereken 17 sütunu okur (`;` ayraç, ISO-8859-1, hepsi metin). |
| `bos_yanitlari_at(df)` | `FILTRE_SUTUNLARI`'ndan birinde `-` olan satırları atar. Sigara bu listede yok (B0). |
| `yas_yil(...)` | "43 anos, 3 meses, 19 dias" → 43 (ilk sayı, düzenli ifade `\d+`). |
| `girdileri_hesapla(df)` | VS = ateş varsa 2; BD = nefes darlığı varsa 0,5; RF = 60+ yaş, komorbidite ya da gebelik varsa 1; RS = beş belirtiden biri varsa 1. |
| `siddet_ekle(df)` | En fazla 16 farklı girdi kombinasyonu var. Her birinde `siddet` bir kez çağrılır, sonuç `merge` ile 1,67 milyon satıra eşlenir. |
| `karar_ekle(df, esik)` | `ModelYatis = SV ≥ eşik`, `FiiliYatis = FicouInternado == "Sim"`. |
| `hazirla(dosya_yolu)` | Hepsini sırayla çalıştırır. |

### `src/makale_degerleri.py`

Makaleden elle aktarılan sayılar: Tablo 5'in 15 vakası, ölüm sayıları, %63,29 gibi oranlar, kapsülün Febre sayıları. Kod değil, karşılaştırma için sabitler.

### `analiz/`: sonuç üreten betikler

| Betik | Ürettiği | Bulgu |
|---|---|---|
| `veri_ozeti.py` | Kayıt sayısı, Febre ve Gestante dağılımı, 16 kombinasyon | B0 |
| `tablo5.py` | 15 vakanın ateşlenen kuralı, SV'si, makaleyle farkı | B1, B2 |
| `yeniden_uretim.py` | SV dağılımı, yatış oranları, ölüm karşılaştırması (iki taban) | B4 |
| `kural_ateslenme.py` | Veride görülen girdilerin üyelikleri, ateşin etkisi, kural başına kayıt | B3 |
| `yuzey_duyarlilik.py` | VS × BD yüzeyleri, 3B yüzey, tek girdili duyarlılık eğrileri | B5 |
| `bulanik_kesin.py` | Bulanık ve kesin modelin gerçek veride ve ızgarada farkı, örtüşme bölgeleri | B5, B6 |
| `esik_analizi.py` | Eşik 0–1 arası: öneri oranları, yakalanan ölüm başına öneri | B7 |

### `app.py`: Streamlit demo

| Fonksiyon | Ne yapar |
|---|---|
| `vaka_yukle(vaka)` | Tablo 5 butonuna basınca kaydırıcıları o vakaya ayarlar (`st.session_state`). |
| `uyelik_grafigi(...)` | Bir girdinin ÜF'leri, girdi çizgisi, dereceler. |
| `ateslenen_kurallar_tablosu(sonuc)` | Gücü > 0 olan kurallar, dört koşul derecesi ve güç. |
| `cikti_grafigi(sonuc, esik)` | Çıktı kümeleri (kesikli), kırpılmış kümeler, birleşik küme (mor), ağırlık merkezi (siyah çizgi). |
| `sonuc_ozeti(...)` | SV, karar, ateşlenen kural sayısı; hiçbir kural ateşlenmezse açıklama. |
| `makale_karsilastirmasi(...)` | Seçili vakada makaledeki değeri gösterir, 5/13/15'te uyarı verir. |
| `main()` | Sayfayı yukarıdan aşağı kurar. Streamlit her etkileşimde betiği baştan çalıştırır. |

### `tests/`

| Dosya | Neyi kontrol eder |
|---|---|
| `test_uyelik.py` | ÜF'lerin elle bilinen noktaları (kenarlar, tepe, dikey kenarlar). |
| `test_mamdani_skfuzzy.py` | Aynı model scikit-fuzzy ile kurulur. 16 ikili girdi, 15 Tablo 5 vakası ve 2.025 noktalık ızgarada fark < 0,001. |
| `test_veri.py` | Elle yazılmış 6 satırlık **test kaydıyla** ön işleme kuralları. Bu kayıtlar analizde kullanılmıyor. |
| `test_kesin_model.py` | Kesin modelin sınırları; 16 ikili kombinasyonda bulanıkla aynı sonuç. |

---

## 2. Elle hesap

### Örnek A: gerçek veriden bir vaka (Tablo 5, vaka 1)

Girdi: ateş var (VS = 2), nefes darlığı var (BD = 0,5), risk faktörü var (RF = 1), diğer belirti var (RS = 1).

**1. Bulanıklaştırma**

| Girdi | Hesap | Sonuç |
|---|---|---|
| VS = 2 | low trapmf[0, 0, 4, 5]: 0 ≤ 2 ≤ 4, düz kısım | low = 1, medium = 0, high = 0 |
| BD = 0,5 | high trimf[0,25, 0,5, 0,75]: tepe noktası | minimal = 0, high = 1, veryhigh = 0 |
| RF = 1 | meaningful trapmf[0,4, 0,6, 1, 1]: düz kısım | minimal = 0, meaningful = 1 |
| RS = 1 | aynı | minimal = 0, meaningful = 1 |

**2. Kural ateşleme.** Gücü 0'dan büyük tek kural, bütün koşulları 1 olan kural 8: EĞER VS = low VE BD = high VE RF = meaningful VE RS = meaningful İSE SV = severe. Güç = min(1, 1, 1, 1) = **1**. Diğer 35 kuralın en az bir koşulu 0, güçleri 0.

**3. Kırpma.** severe trimf[0,7, 1, 1], 1 yüksekliğinde kesilir, yani hiç değişmez.

**4. Birleştirme.** Tek küme var; birleşik küme = severe üçgeni.

**5. Durulaştırma.** Üçgenin ağırlık merkezi köşelerin ortalaması: (0,7 + 1 + 1) / 3 = **0,9**. Kod: alan 0,15, moment 0,135, 0,135 / 0,15 = 0,9.

**Karar:** 0,9 ≥ 0,75 → yatış önerilir. Makale bu vakaya 0,873 yazıyor; terim ve karar aynı (B1).

Gerçek verideki her kayıt böyle: tek kural, güç 1, sonuç 0,1 / 0,5 / 0,9. Bu, bulanık yapının veride devreye girmediğini gösteriyor (B3).

### Örnek B: kısmi üyelik (sürekli girdi)

Bulanık çıkarımın gerçekten çalıştığı bir vaka: VS = 4,3, BD = 0,1, RF = 0,45, RS = 1. Gerçek veride böyle bir girdi yok; demo ile gösterilebilir.

**1. Bulanıklaştırma**

| Girdi | Hesap | Sonuç |
|---|---|---|
| VS = 4,3 | low: düşen kenar (5 − 4,3) / (5 − 4) = 0,7; medium: yükselen kenar (4,3 − 4) / (5 − 4) = 0,3 | low = **0,7**, medium = **0,3** |
| BD = 0,1 | minimal trapmf[0, 0, 0,2, 0,25] düz kısım | minimal = 1 |
| RF = 0,45 | minimal: (0,6 − 0,45) / 0,2 = 0,75; meaningful: (0,45 − 0,4) / 0,2 = 0,25 | minimal = **0,75**, meaningful = **0,25** |
| RS = 1 | | meaningful = 1 |

**2. Kural ateşleme** (VE = min). BD yalnız minimal, RS yalnız meaningful olduğu için VS ve RF'nin 2 × 2 = 4 kombinasyonu ateşlenir:

| Kural | VS | RF | Güç = min(VS, BD, RF, RS) | Çıktı |
|---|---|---|---|---|
| 2 | low 0,7 | minimal 0,75 | min(0,7, 1, 0,75, 1) = **0,7** | mild |
| 4 | low 0,7 | meaningful 0,25 | min(0,7, 1, 0,25, 1) = **0,25** | severe |
| 14 | medium 0,3 | minimal 0,75 | min(0,3, 1, 0,75, 1) = **0,3** | moderate |
| 16 | medium 0,3 | meaningful 0,25 | min(0,3, 1, 0,25, 1) = **0,25** | moderate |

**3. Kırpma.** mild üçgeni 0,7'de, severe üçgeni 0,25'te, moderate üçgeni bir kez 0,3'te, bir kez 0,25'te kesilir.

**4. Birleştirme** (max). İki moderate kümesinden büyüğü (0,3) kalır. Birleşik küme: mild 0,7 + moderate 0,3 + severe 0,25 yüksekliğinde üç kesik üçgen.

**5. Durulaştırma.** Kesik üçgenin alanı (taban w, kesme yüksekliği h): taban w, üst kenar w(1 − h) olan yamuk, alan = h · (2 − h) · w / 2.

| Parça | w | h | Alan | Kendi merkezi |
|---|---|---|---|---|
| mild | 0,3 | 0,7 | 0,7 · 1,3 · 0,3 / 2 = 0,1365 | 0,107 |
| moderate | 0,6 | 0,3 | 0,3 · 1,7 · 0,6 / 2 = 0,1530 | 0,500 (simetrik) |
| severe | 0,3 | 0,25 | 0,25 · 1,75 · 0,3 / 2 = 0,0656 | 0,868 |

Parçalar örtüşmeseydi: SV ≈ (0,1365 · 0,107 + 0,1530 · 0,5 + 0,0656 · 0,868) / (0,1365 + 0,1530 + 0,0656) = **0,417**.

Gerçekte parçalar 0,2–0,3 ve 0,7–0,8 aralıklarında üst üste biniyor ve birleştirme max aldığı için bu bölgeler bir kez sayılıyor. Kodun tam hesabı: alan 0,3385, moment 0,1397, **SV = 0,413**. El hesabı ile fark 0,004.

**Karar:** 0,413 < 0,75 → ayaktan izlem.

**Kesin modelle karşılaştırma:** Kesin sürümde VS = 4,3 → low, RF = 0,45 → minimal; yalnız kural 2 çalışır ve SV = **0,1** olur. Bulanık model ise VS'nin "orta"ya, RF'nin "anlamlı"ya kısmen yaklaştığını hesaba katıp 0,413 veriyor. Bulanık yapının bu modeldeki katkısı tam olarak bu: geçiş bölgelerinde kademeli sonuç (B6).

---

## 3. Sunumda sorulabilecek 10 soru

**1. Bunun neresi bulanık?**
Gerçek veride hiçbir yeri. Girdiler ikili olduğu için her kayıtta tek bir kural tam güçle ateşleniyor ve çıktı yalnız 0,1 / 0,5 / 0,9 oluyor. Aynı kuralların kesin sürümü 1.675.352 kaydın hepsinde aynı sonucu veriyor (B3, B6). Bulanık yapı ancak sürekli girdilerde fark yaratıyor: VS 4–7 ve RF/RS 0,4–0,6 aralıklarında. Örnek B'de kesin model 0,1, bulanık model 0,413 veriyor. Model sürekli ölçümlerle (NEWS puanı, oksijen satürasyonu) beslenseydi bu fark işe yarardı.

**2. Veri nereden geldi?**
Espírito Santo eyaletinin (Brezilya) COVID-19 paneli: 1.679.329 bildirim kaydı, Ocak 2020–Temmuz 2021. Yazarların Code Ocean kapsülündeki kopyayı indirdim. Makaledeki kayıt sayısı ve kapsüldeki ateş dağılımı birebir tutuyor. Rastgele veri yok; testlerdeki 6 satırlık kayıt yalnız ön işleme kurallarını denemek için elle yazıldı.

**3. VE için neden min, birleştirme için neden max?**
Mamdani'nin standart seçimleri. min: zincir en zayıf halkası kadar güçlüdür; bir koşul 0,3 sağlanıyorsa kural en fazla 0,3 güçle ateşlenebilir. max: birden çok kural aynı çıktıyı öneriyorsa en güçlü öneri geçerli olur, güçler toplanmaz. scikit-fuzzy ve MATLAB'ın Mamdani varsayılanları da bunlar.

**4. Ağırlık merkezi nasıl hesaplanıyor?**
`SV = ∫x·μ(x)dx / ∫μ(x)dx`. Birleşik kümenin "denge noktası". 0–1 aralığını 1001 noktaya bölüp integralleri yamuk kuralıyla (`np.trapezoid`) alıyorum. Tek bir üçgende sonuç köşelerin ortalaması: severe için (0,7 + 1 + 1) / 3 = 0,9.

**5. Kendi motorunun doğru olduğunu nereden biliyorsun?**
Aynı modeli scikit-fuzzy ile kurup karşılaştırdım. 16 gerçek girdi kombinasyonunda, Tablo 5'in 15 vakasında ve 2.025 noktalık sürekli ızgarada fark 0,001'in altında. Bunlar `pytest` ile her seferinde yeniden kontrol ediliyor. Ayrıca kapsülün sonuçlarını (SV değerleri, %26,8) aynen üretiyor.

**6. Makale Tablo 5'te 0,163 ve 0,873 diyor, sen 0,1 ve 0,9 buluyorsun. Neden?**
Kapsüldeki ÜF'lerle tek kural tam ateşlenince sonuç çıktı üçgeninin ağırlık merkezi oluyor: mild (0 + 0 + 0,3) / 3 = 0,1, severe 0,9. Kapsülün kendi çıktısı da 0,1 / 0,5 / 0,9. Makaledeki sayılar büyük olasılıkla farklı çıktı ÜF'leriyle hesaplanmış; örneğin trimf[0, 0, 0,49] 0,163 verir. Makale parametreleri yazmadığı için bu bir tahmin. 0,75 eşiğinde karar değişmiyor (B1).

**7. Tablo 5'te üç vaka neden farklı?**
5. vakanın girdileri 3. vakayla birebir aynı, ama makale birine "ağır", diğerine "orta" yazıyor; deterministik bir sistemde bu olamaz. 13 ve 15. vakalarda nefes darlığı var ve diğer belirti var; Tablo 3'te bu durumun tek kuralı (kural 6) "ağır" diyor, makale "hafif" yazıyor. Bu üçünde karar da değişiyor. Tablo 5'te aktarım hatası olması muhtemel (B2).

**8. Ateşin modelde etkisi var mı?**
Gerçek veride yok. Veride yalnız "ateş var/yok" bilgisi var ve ateş VS = 2 olarak kodlanıyor. VS = 2 "düşük" kümesinin düz kısmında (0–4) kalıyor; "orta"ya geçmek için VS > 4 gerekir. Ateşli 540.919 kaydın hiçbirinde sonuç ateşsiz olandan farklı değil (B3).

**9. BD = 0,25'te ne oluyor?**
BD'nin üç teriminin üyeliği de 0: minimal tam 0,25'te bitiyor, high tam 0,25'te başlıyor. Hiçbir kural ateşlenmiyor, birleşik küme boş, ağırlık merkezi 0/0. Benim motor NaN döndürüyor, scikit-fuzzy çıktı üretmiyor. Aynı şey 0,75'te de var. Gerçek veride BD yalnız 0 ve 0,5 olduğu için görünmüyor. Demo'da gösterilebilir (B5).

**10. %26,8 iyi bir sonuç mu? Model ölümleri daha iyi yakalıyor mu?**
Model, ölen COVID-19 hastalarının %82,5'ine yatış önerirdi; fiili yatış %63,3. Ama aynı model bütün kayıtların %26,8'ine, iyileşenlerin %29'una da yatış öneriyor; fiili yatış oranı %2,3. Yani yakalama oranını yaklaşık 15 kat fazla yatış önererek artırıyor: yakalanan her ölüm başına yaklaşık 65 kayda yatış önerisi. Makale bu maliyeti göstermiyor. Eşik de pratikte seçilemiyor: SV üç değer aldığı için 0,51–0,90 arasındaki her eşik aynı sonucu veriyor (B4, B7).

---

## Ek: hızlı sayılar

| | |
|---|---|
| Toplam kayıt / ön işleme sonrası | 1.679.329 / 1.675.352 |
| Ateşlenen kural (gerçek veri) | 36'nın 8'i; en sık kural 2 (%46,0) |
| SV dağılımı | 0,1: %72,6 · 0,5: %0,5 · 0,9: %26,8 |
| COVID-19 ölümü (yatış bilgisi bilinen) | 8.412; fiili yatış %63,3; model %82,5 |
| Test sayısı | 58 |
