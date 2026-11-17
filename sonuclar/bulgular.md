# Bulgular (ara sürüm)

## Özet: makale/kapsül ve bizim değerler

| Ölçü | Makale / kapsül | Bizim | Durum |
|---|---|---|---|
| Toplam kayıt | 1.679.329 | 1.679.329 | aynı |
| Febre (ön işleme sonrası) Não / Sim | 1.134.433 / 540.919 | 1.134.433 / 540.919 | aynı (B0) |
| SV değerleri | 0,1 / 0,5 / 0,9 | 0,1 / 0,5 / 0,9 | aynı |
| Yatış önerilen kayıt, 0,75 | %26,8 | %26,84 (449.685 / 1.675.352) | aynı |
| Yatış önerilen kayıt, 0,50 | "biraz artıyor" | %27,39 (458.817) | uyumlu |
| COVID-19 / diğer nedenli ölüm | 11.510 / 3.432 | 11.510 / 3.432 | aynı |
| Ölümlerde fiili yatış, COVID / diğer | %63,29 / %47,15 | %63,29 / %47,15 (bilinen taban) | aynı (B4) |
| COVID ölümünde yatırılmayan, fiili | %37 | %36,7 | aynı (yuvarlama) |
| COVID ölümünde yatırılmayan, model 0,75 | %18 | %17,5 | aynı (yuvarlama) |
| Tablo 5, 15 vaka | — | 12 uyumlu, 3 çelişkili | B1, B2 |
| Gerçek veride ateşlenen kural | — | 36'nın 8'i (1–8); ateşin etkisi 0 | B3 |

Kaynak çıktılar: `sonuclar/veri_ozeti.txt`, `sonuclar/yeniden_uretim.txt`, `sonuclar/*.csv`, `sonuclar/*.png`.

Makaleyle uyuşmayan değerler. Her birinde kural tabanına (Tablo 3) göre ne çıkması gerektiği yazıldı. Veri dosyası gelince bölümler genişletilecek.

## B0: Kapsülün "-" filtresinde sigara sütunu yok

`MICRODADOS.csv` 1.679.329 kayıt içeriyor; makaledeki sayıyla aynı. Ham Febre dağılımı Não 1.135.946 / Sim 541.830 / "-" 1.553. Kapsüldeki Não 1.134.433 / Sim 540.919 ham veriye ait değil, ön işlemeden sonraki sayılar.

Brifteki filtre listesiyle (6 komorbiditenin hepsi) sonuç Não 1.134.397 / Sim 540.899 çıkıyor, kapsülden 56 kayıt eksik. Filtre listesinden sütunları birer birer çıkarıp denedim. **Yalnız `ComorbidadeTabagismo` (sigara) çıkarıldığında** sayılar kapsülle birebir tutuyor:

| Filtre | Não | Sim | Kalan kayıt |
|---|---|---|---|
| 6 komorbiditenin hepsi | 1.134.397 | 540.899 | 1.675.296 |
| Sigara hariç (kullanılan) | **1.134.433** | **540.919** | **1.675.352** |
| Kapsül | 1.134.433 | 540.919 | — |

`src/veri.py` buna göre düzeltildi. Sigara RF hesabında yine kullanılıyor; "-" yanıtı "Sim" olmadığı için risk sayılmıyor. Fark yüzde birin çok altında (56 kayıt) ve sonuçları değiştirmiyor; ama sayılar kapsülle birebir tuttuğu için bu filtre seçildi.

Diğer kontroller:
- Yaş (`IdadeNaDataNotificacao`, "43 anos, 3 meses, 19 dias" biçiminde) her kayıtta okunabildi, aralığı 0–117.
- `Gestante` yanıtları: Não, Não se aplica, Ignorado (gebe değil); 1º/2º/3º "trimeste" (veride bu yazımla) ve "Idade gestacional ignorada" (gebe). `GEBE_DEGIL` kümesi buna göre doğru.
- `FicouInternado` sütununda "-" yok; yanıtlar Sim / Não / Não Informado / Ignorado. Fiili yatış yalnız "Sim" sayıldı.

## B1: Tablo 5'teki SV sayıları kapsülün ÜF'leriyle elde edilemiyor

İkili girdilerde her vakada tek kural tam güçle (1,0) ateşlenir. Bu yüzden çıktı, o kuralın çıktı üçgeninin ağırlık merkezidir:

| Çıktı terimi | ÜF (kapsül) | Ağırlık merkezi | Makale Tablo 5 |
|---|---|---|---|
| mild | trimf[0, 0, 0,3] | (0+0+0,3)/3 = **0,100** | 0,163 |
| moderate | trimf[0,2, 0,5, 0,8] | **0,500** | 0,500 |
| severe | trimf[0,7, 1, 1] | (0,7+1+1)/3 = **0,900** | 0,873 / 0,8737 |

Kendi motorumuz ve scikit-fuzzy aynı sonucu veriyor (0,1 / 0,5 / 0,9; fark < 0,001). Kapsül çıktısı da 0,1 / 0,5 / 0,9. Tablo 5'teki sayılar başka ÜF parametreleriyle hesaplanmış olmalı. Örneğin trimf[0, 0, 0,49] ağırlık merkezi 0,163, trimf[0,62, 1, 1] ağırlık merkezi 0,873 verir. Bu yalnız bir **olasılık**: makale ÜF parametrelerini sayı olarak vermiyor ve hangi aracın (MATLAB / scikit-fuzzy) kullanıldığını belirtmiyor.

Karara etkisi yok: 0,163 < 0,75 ≤ 0,873, aynı eşikte aynı karar çıkar.

## B2: Tablo 5'te üç vaka kural tablosuyla çelişiyor

| Vaka | Girdi (VS, BD, RF, RS) | Terimler | Tablo 3'e göre | Makale Tablo 5 |
|---|---|---|---|---|
| 5 | (2, 0, 1, 1) | low, minimal, meaningful, meaningful | Kural 4 → **severe (0,9)** | moderate (0,500) |
| 13 | (0, 0,5, 0, 1) | low, high, minimal, meaningful | Kural 6 → **severe (0,9)** | mild (0,163) |
| 15 | (0, 0,5, 0, 1) | low, high, minimal, meaningful | Kural 6 → **severe (0,9)** | mild (0,163) |

- Vaka 5'in girdileri vaka 3 ile birebir aynı, ama makale vaka 3'e "severe 0,8737", vaka 5'e "moderate 0,500" yazıyor. Aynı girdiye iki farklı çıktı deterministik bir sistemde olamaz. Tablo 5'te bir aktarım hatası olması muhtemel.
- Vaka 13 ve 15'te BD = 0,5 (nefes darlığı var), RS = 1. Tablo 3'te bu durum için tek kural var (kural 6) ve sonucu severe. "Mild" çıkması için BD'nin minimal (0) olması gerekirdi. O zaman kural 2 çalışır: mild, 0,1.
- Diğer 12 vaka Tablo 3 ile uyumlu.

- B1'den farklı olarak bu üç vakada **0,75 eşiğindeki karar da değişiyor**. Kural tablosu üçüne de yatış öneriyor (0,9); makaledeki sayılarla (0,500 ve 0,163) yatış önerilmiyor.

Kaynak: `python -m analiz.tablo5` → `sonuclar/tablo5.csv` (her vaka için ateşlenen kural, bizim SV, makale SV, iki eşik kararı).

## B3: Gerçek veride ateşin etkisi yok, 36 kuralın yalnız 1–8'i çalışıyor

Veride her girdi yalnız iki değer alıyor. Bu değerler üyelik fonksiyonlarına şöyle düşüyor (`sonuclar/girdi_uyelikleri.csv`):

| Girdi | Değer | Tam üyelik (1,0) | Diğer terimler |
|---|---|---|---|
| VS | 0 (ateş yok) | low | medium 0, high 0 |
| VS | 2 (ateş var) | **low** | medium 0, high 0 |
| BD | 0 | minimal | high 0, veryhigh 0 |
| BD | 0,5 | high | minimal 0, **veryhigh 0** |
| RF / RS | 0 | minimal | meaningful 0 |
| RF / RS | 1 | meaningful | minimal 0 |

**Ateşin etkisi yok.** VS = 2, low kümesinin düz kısmında (trapmf[0, 0, 4, 5] için 0–4 arası 1) kalıyor. Medium kümesine geçmek için VS > 4 gerekir; VS = 4,5'te bile medium yalnız 0,5 olur. Bu yüzden ateşli ve ateşsiz iki hasta, diğer girdileri aynıysa, birebir aynı SV'yi alıyor. 8 kombinasyonun hepsinde fark 0. Veride ateşi olan 540.919 kaydın hiçbirinde ateş sonucu değiştirmiyor.

**"veryhigh" hiç ateşlenmiyor.** BD = 0,5 yalnız "high" üçgeninin tepesine düşüyor. veryhigh için BD > 0,75 gerekir, veride böyle bir değer yok.

**36 kuralın 8'i çalışıyor.** VS hep low ve BD hiç veryhigh olmadığı için yalnız kural 1–8 ateşlenebiliyor. Her kayıtta tam olarak bir kural tam güçle (1,0) ateşleniyor; toplam ateşlenme 1.675.352 ve kayıt sayısına eşit.

| Kural | VS | BD | RF | RS | SV | Ateşlendiği kayıt | % |
|---|---|---|---|---|---|---|---|
| 1 | low | minimal | minimal | minimal | mild | 370.644 | 22,12 |
| 2 | low | minimal | minimal | meaningful | mild | 770.615 | 46,00 |
| 3 | low | minimal | meaningful | minimal | mild | 75.276 | 4,49 |
| 4 | low | minimal | meaningful | meaningful | severe | 240.454 | 14,35 |
| 5 | low | high | minimal | minimal | moderate | 9.132 | 0,55 |
| 6 | low | high | minimal | meaningful | severe | 129.377 | 7,72 |
| 7 | low | high | meaningful | minimal | severe | 10.533 | 0,63 |
| 8 | low | high | meaningful | meaningful | severe | 69.321 | 4,14 |
| 9–36 | — | — | — | — | — | 0 | 0 |

**Sonuç:** Gerçek veride sistem fiilen 8 satırlık bir karar tablosu gibi çalışıyor. Çıktı yalnız üç değer alıyor (0,1 / 0,5 / 0,9), kural güçleri hep 0 ya da 1. Bulanık çıkarımın kısmi üyelik, birden çok kuralın birlikte ateşlenmesi gibi özellikleri bu veride hiç devreye girmiyor. Makale de VS için bu durumu kısaca not ediyor: kayıtlarda yalnız ateşin varlığı olduğu için VS ağırlıkla düşük çıkıyor. Bulanık yapının katkısı ancak sürekli girdilerle (NEWS puanı, ölçülmüş solunum sıkıntısı) görülebilir. Bu, 4. aşamada yüzey ve duyarlılık grafikleriyle ölçülecek.

Kaynak: `python -m analiz.kural_ateslenme` → `sonuclar/kural_ateslenme.csv`, `sonuclar/kural_ateslenme.txt`.

## B4: Makaledeki ölüm oranları yalnız yatış bilgisi bilinen kayıtlara göre

Ölüm sayıları makaleyle birebir aynı (11.510 COVID-19, 3.432 diğer). Ancak bu ölümlerin önemli bir kısmında `FicouInternado` "Não Informado" ya da "Ignorado":

| Grup | Sim | Não | Não Informado | Ignorado |
|---|---|---|---|---|
| COVID-19 ölümü | 5.324 | 3.088 | 2.821 | 277 |
| Diğer nedenli ölüm | 1.143 | 1.281 | 879 | 129 |

Makaledeki %63,29 = 5.324 / (5.324 + 3.088). Yani payda yalnız yatış bilgisi bilinen 8.412 kayıt; bütün ölümler (11.510) değil. Aynı tabanda:

| Grup (bilinen taban) | n | Fiili yatış | Model, SV ≥ 0,75 | Model, SV ≥ 0,50 |
|---|---|---|---|---|
| COVID-19 ölümü | 8.412 | %63,3 | %82,5 | %83,9 |
| Diğer nedenli ölüm | 2.424 | %47,2 | %72,1 | %75,1 |

Bütün ölümler tabana alınırsa fiili yatış %46,3 (COVID) ve %33,3 (diğer), model 0,75 eşiğinde %80,3 ve %70,4 olur. Makale bu tercihi açıkça yazmıyor. Tabanı bilerek seçmek gerekiyor: "Não Informado" kayıtların yatırılmadığını varsaymak fiili oranı düşük gösterir.

Yorum (abartmadan): Model, ölen hastaların daha büyük kısmına yatış öneriyor. Ama aynı model **bütün kayıtların %26,8'ine** yatış öneriyor. Ölümlerde yakalama oranının yükselmesi, kaç kişinin gereksiz yatırılacağı (yanlış pozitif) bilinmeden "daha iyi" diye okunmamalı. Bu, eşik analizinde (4. aşama) ele alınacak.

## B5: BD terimleri örtüşmüyor; 0,25 ve 0,75'te hiçbir kural ateşlenmiyor

Sürekli girdilerle (`python -m analiz.yuzey_duyarlilik`) bakınca nefes darlığının (BD) üyelik fonksiyonlarında bir tasarım sorunu görünüyor:

| Komşu terimler | Biri bittiği yer | Diğeri başladığı yer | Örtüşme |
|---|---|---|---|
| minimal → high | trapmf[0, 0, 0,2, **0,25**] | trimf[**0,25**, 0,5, 0,75] | yok |
| high → veryhigh | trimf[0,25, 0,5, **0,75**] | trapmf[**0,75**, 0,8, 1, 1] | yok |

- **BD = 0,25 ve BD = 0,75'te üç terimin üyeliği de 0.** Hiçbir kural ateşlenmiyor, birleşik çıktı kümesi boş kalıyor ve ağırlık merkezi tanımsız (0/0). Motorumuz bu durumda NaN döndürüyor; scikit-fuzzy aynı girdide çıktı üretmiyor (`output["SV"]` boş kalıyor, KeyError). Yüzey grafiğinde (`sonuclar/yuzey_vs_bd.png`) kırmızı çizgiler bu iki nokta.
- **BD'de yumuşak geçiş yok.** VS = 0, RF = 0, RS = 1 iken BD = 0,24'te SV 0,14, BD = 0,26'da SV 0,85. Arada tek bir kural bile iki terimle birlikte ateşlenmiyor; geçiş kesin modeldeki gibi bir sıçrama (`sonuclar/duyarlilik.png`, orta panel).
- Karşılaştırma için: VS'de terimler 4–5 ve 6–7 aralıklarında, RF ve RS'de 0,4–0,6 aralığında örtüşüyor. Bu girdilerde çıktı eşikten eşiğe sürekli değişiyor (duyarlılık grafiği, sol ve sağ panel).

| Girdi | Evrenin yüzde kaçında iki terim birlikte > 0 | Hiçbir terimin olmadığı nokta |
|---|---|---|
| VS | %11,1 | 0 |
| BD | **%0** | **2 (0,25 ve 0,75)** |
| RF | %20,0 | 0 |
| RS | %20,0 | 0 |

Gerçek veride bu sorun görünmüyor, çünkü BD yalnız 0 ve 0,5 değerlerini alıyor. Ama model sürekli bir BD ölçüsüyle (örneğin bir dispne skalası) kullanılsaydı 0,25 ve 0,75'teki hastalar için karar üretemezdi. Basit bir düzeltme, minimal'in sağ ayağını ve veryhigh'ın sol ayağını high üçgeninin içine uzatmak olurdu (ör. minimal trapmf[0, 0, 0,2, 0,35]). Biz modeli değiştirmedik, makaledeki haliyle bıraktık.

Kaynak: `sonuclar/yuzey_vs_bd.png`, `sonuclar/yuzey_3b.png`, `sonuclar/duyarlilik.png`, `sonuclar/ortusme_bolgeleri.csv`.

## B6: Bulanık model ile aynı kuralların kesin sürümü

Kesin sürüm (`src/kesin_model.py`): her girdi yalnız tek bir terime atanır. Sınırlar, bulanık modelde en yüksek üyelikli terimin değiştiği noktalar: VS 4,5 ve 6,5; BD 0,25 ve 0,75; RF ve RS 0,5. Böylece tek kural çalışır ve çıktı 0,1 / 0,5 / 0,9 olur. Karşılaştırma `python -m analiz.bulanik_kesin` ile yapıldı.

**Gerçek veride fark yok.** 1.675.352 kaydın **hiçbirinde** iki model farklı SV vermiyor. B3'teki gibi her kayıtta tek kural tam güçle ateşleniyor; bu durumda bulanık çıkarım kesin bir tablo okumasına indirgeniyor.

**Sürekli girdilerde fark yalnız kısmi üyelik bölgelerinde.** Izgara: VS 0,5 adım, BD 0,02 adım, RF ve RS 0,1 adım, toplam 228.327 nokta, her girdinin evreni eşit aralıklı.

| Nokta grubu | Nokta | SV aynı (fark < 0,001) | 0,75 kararı farklı | En büyük fark |
|---|---|---|---|---|
| Bütün girdiler tek terime tam üye | 80.500 | %100 | %0 | 0,000 |
| En az bir girdi kısmi üye | 147.827 | %11,1 | %7,0 | 0,400 |
| Hepsi | 228.327 | %42,4 | %4,5 | 0,400 |

Ortalama mutlak fark 0,026. Kararın değiştiği noktaların hepsi kısmi üyelik bölgesinde.

**Yorum (abartmadan):** Bulanık yapının bu modeldeki tek katkısı, VS'nin 4–7 ve RF/RS'nin 0,4–0,6 aralığındaki geçişleri yumuşatmak. Bu bölgelerde karar, sınırın hangi tarafında olunduğuna göre değil, kademeli olarak değişiyor. BD'de bu katkı yok (B5). Bu bölgeler ızgaranın yaklaşık üçte ikisini kaplıyor, ama gerçek veride hiçbir kayıt bu bölgelere düşmüyor. Izgaradaki yüzdeler ızgaranın nasıl seçildiğine bağlı; gerçek hasta dağılımını temsil etmiyor.

Kaynak: `sonuclar/bulanik_kesin.csv`, `sonuclar/bulanik_kesin.txt`, `sonuclar/ortusme_bolgeleri.csv`.
