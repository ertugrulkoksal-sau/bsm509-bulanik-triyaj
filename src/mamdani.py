"""Mamdani bulanık çıkarım motoru (yalnız NumPy).

Adımlar, her biri ayrı fonksiyon:
    1. bulaniklastir  : kesin girdi -> her terimin üyelik derecesi
    2. kural_gucu     : kuralın EĞER kısmı, VE = min
    3. kirp           : kuralın İSE kısmı, çıktı kümesini güçle kırpma (min)
    4. birlestir      : kırpılmış kümeleri tek kümede toplama (max)
    5. agirlik_merkezi: birleşik kümeden tek sayı (durulaştırma)
`cikarim` bu adımları sırayla çağırır.
"""

import numpy as np

from src.model import CIKTI, CIKTI_EVRENI, GIRDI_SIRASI, GIRDILER, KURALLAR
from src.uyelik import uyelik_hesapla


def bulaniklastir(girdiler):
    """Adım 1: her girdinin her terimdeki üyelik derecesini bulur.

    girdiler: {"VS": 2, "BD": 0.5, "RF": 1, "RS": 1}
    dönüş   : {"VS": {"low": 1.0, "medium": 0.0, "high": 0.0}, "BD": {...}, ...}
    """
    dereceler = {}
    for degisken in GIRDI_SIRASI:
        x = girdiler[degisken]
        dereceler[degisken] = {}
        for terim, (tip, parametreler) in GIRDILER[degisken]["terimler"].items():
            dereceler[degisken][terim] = float(uyelik_hesapla(x, tip, parametreler))
    return dereceler


def kural_gucu(kural, dereceler):
    """Adım 2: bir kuralın ateşlenme gücü = dört koşulun en küçüğü (VE = min)."""
    kosul_dereceleri = []
    for degisken, terim in zip(GIRDI_SIRASI, kural[:4]):
        kosul_dereceleri.append(dereceler[degisken][terim])
    return min(kosul_dereceleri)


def kirp(cikti_terimi, guc):
    """Adım 3: kuralın çıktı kümesini gücü kadar yükseklikte keser (min)."""
    tip, parametreler = CIKTI["terimler"][cikti_terimi]
    kume = uyelik_hesapla(CIKTI_EVRENI, tip, parametreler)
    return np.minimum(kume, guc)


def birlestir(kirpilmis_kumeler):
    """Adım 4: tüm kırpılmış kümelerin nokta nokta en büyüğü (max)."""
    birlesik = np.zeros_like(CIKTI_EVRENI)
    for kume in kirpilmis_kumeler:
        birlesik = np.maximum(birlesik, kume)
    return birlesik


def agirlik_merkezi(evren, kume):
    """Adım 5: ağırlık merkezi = ∫x·μ(x)dx / ∫μ(x)dx.

    İntegraller yamuk kuralıyla (np.trapezoid) hesaplanır.
    Hiç kural ateşlenmezse alan 0 olur; bu durumda NaN döner.
    """
    alan = np.trapezoid(kume, evren)
    if alan == 0:
        return float("nan")
    moment = np.trapezoid(evren * kume, evren)
    return float(moment / alan)


def cikarim(vs, bd, rf, rs):
    """Tüm adımları çalıştırır; ara sonuçları da döndürür (demo için).

    dönüş: {"dereceler", "kural_gucleri", "birlesik", "sv"}
    """
    girdiler = {"VS": vs, "BD": bd, "RF": rf, "RS": rs}

    # 1. Bulanıklaştırma
    dereceler = bulaniklastir(girdiler)

    # 2-3. Her kuralı ateşle ve çıktı kümesini kırp
    kural_gucleri = []
    kirpilmis_kumeler = []
    for kural in KURALLAR:
        guc = kural_gucu(kural, dereceler)
        kural_gucleri.append(guc)
        if guc > 0:  # gücü 0 olan kural sonuca katkı vermez
            kirpilmis_kumeler.append(kirp(kural[4], guc))

    # 4. Birleştirme
    birlesik = birlestir(kirpilmis_kumeler)

    # 5. Durulaştırma
    sv = agirlik_merkezi(CIKTI_EVRENI, birlesik)

    return {
        "dereceler": dereceler,
        "kural_gucleri": kural_gucleri,
        "birlesik": birlesik,
        "sv": sv,
    }


def siddet(vs, bd, rf, rs):
    """Yalnız durulaştırılmış şiddet değerini (SV) döndürür."""
    return cikarim(vs, bd, rf, rs)["sv"]
