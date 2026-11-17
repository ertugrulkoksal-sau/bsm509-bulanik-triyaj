"""Aynı 36 kuralın kesin (crisp) sürümü: karşılaştırma için.

Bulanık modelden tek farkı: her girdi yalnız BİR terime atanır (üyelik 0 ya
da 1). Sınırlar, bulanık modelde en yüksek üyelikli terimin değiştiği
noktalardır (iki ÜF'nin kesiştiği yer). Böylece tek bir kural çalışır ve
çıktı o kuralın çıktı kümesinin ağırlık merkezidir (0,1 / 0,5 / 0,9).
"""

from src.mamdani import agirlik_merkezi, kirp
from src.model import CIKTI_EVRENI, KURALLAR

# (sınır, terim): değer sınırdan KÜÇÜKSE o terim; son terim geri kalan her şey
SINIRLAR = {
    "VS": [(4.5, "low"), (6.5, "medium")],        # 4,5'te low = medium = 0,5
    "BD": [(0.25, "minimal"), (0.75, "high")],    # bulanık modelde bu iki nokta boşluk
    "RF": [(0.5, "minimal")],                     # 0,5'te iki terim de 0,5
    "RS": [(0.5, "minimal")],
}
SON_TERIM = {"VS": "high", "BD": "veryhigh", "RF": "meaningful", "RS": "meaningful"}


def kesin_terim(degisken, x):
    """Girdiyi tek bir terime atar."""
    for sinir, terim in SINIRLAR[degisken]:
        if x < sinir:
            return terim
    return SON_TERIM[degisken]


def kesin_kural(vs, bd, rf, rs):
    """Girdilere uyan tek kuralın numarasını (1-36) bulur."""
    terimler = (kesin_terim("VS", vs), kesin_terim("BD", bd),
                kesin_terim("RF", rf), kesin_terim("RS", rs))
    for i, kural in enumerate(KURALLAR):
        if kural[:4] == terimler:
            return i + 1
    raise ValueError(f"Kural bulunamadı: {terimler}")


def kesin_siddet(vs, bd, rf, rs):
    """Kesin modelin çıktısı: çalışan kuralın çıktı kümesinin ağırlık merkezi."""
    cikti_terimi = KURALLAR[kesin_kural(vs, bd, rf, rs) - 1][4]
    return agirlik_merkezi(CIKTI_EVRENI, kirp(cikti_terimi, 1.0))
