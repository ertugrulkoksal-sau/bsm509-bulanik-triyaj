# Bulgular (ara sürüm)

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
