# Bulgular (ara sürüm)

Makaleyle uyuşmayan değerler. Her birinde kural tabanına (Tablo 3) göre ne çıkması gerektiği yazıldı. Veri dosyası gelince bölümler genişletilecek.

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

Kaynak: `python -c` ile `src.mamdani.cikarim` her vakada çalıştırıldı. Ayrıntılı tablo `analiz/tablo5.py` ile üretilecek.
