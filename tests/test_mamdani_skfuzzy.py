"""Kendi motorumuzu scikit-fuzzy ile karşılaştırır.

scikit-fuzzy yalnız burada, doğrulama için kullanılır. Aynı ÜF'ler ve aynı
36 kuralla kurulan iki sistem aynı girdide en fazla 0,001 farklı sonuç vermeli.
"""

import itertools

import numpy as np
import pytest
import skfuzzy as fuzz
from skfuzzy import control as ctrl

from src.makale_degerleri import TABLO5
from src.mamdani import siddet
from src.model import CIKTI, CIKTI_EVRENI, GIRDI_SIRASI, GIRDILER, KURALLAR

TOLERANS = 0.001


def skfuzzy_uf(evren, tip, parametreler):
    """Model tablosundaki ÜF'yi scikit-fuzzy fonksiyonuyla üretir."""
    if tip == "trap":
        return fuzz.trapmf(evren, parametreler)
    return fuzz.trimf(evren, parametreler)


def skfuzzy_sistemi_kur():
    """Aynı modeli scikit-fuzzy ile kurar."""
    degiskenler = {}
    for ad in GIRDI_SIRASI:
        alt, ust = GIRDILER[ad]["evren"]
        # 0-1 evrende 0,001; 0-18 evrende 0,01 adım
        adim = 0.01 if ust > 1 else 0.001
        evren = np.round(np.arange(alt, ust + adim / 2, adim), 6)
        degisken = ctrl.Antecedent(evren, ad)
        for terim, (tip, p) in GIRDILER[ad]["terimler"].items():
            degisken[terim] = skfuzzy_uf(evren, tip, p)
        degiskenler[ad] = degisken

    sv = ctrl.Consequent(CIKTI_EVRENI, "SV")  # varsayılan durulaştırma: centroid
    for terim, (tip, p) in CIKTI["terimler"].items():
        sv[terim] = skfuzzy_uf(CIKTI_EVRENI, tip, p)

    kurallar = []
    for vs, bd, rf, rs, cikti in KURALLAR:
        kosul = (degiskenler["VS"][vs] & degiskenler["BD"][bd]
                 & degiskenler["RF"][rf] & degiskenler["RS"][rs])
        kurallar.append(ctrl.Rule(kosul, sv[cikti]))

    return ctrl.ControlSystemSimulation(ctrl.ControlSystem(kurallar))


@pytest.fixture(scope="module")
def simulasyon():
    return skfuzzy_sistemi_kur()


def skfuzzy_siddet(simulasyon, vs, bd, rf, rs):
    simulasyon.input["VS"] = vs
    simulasyon.input["BD"] = bd
    simulasyon.input["RF"] = rf
    simulasyon.input["RS"] = rs
    simulasyon.compute()
    return simulasyon.output["SV"]


# Gerçek veride görülen 16 ikili girdi kombinasyonu (VS 0/2, BD 0/0,5, RF, RS 0/1)
IKILI_GIRDILER = list(itertools.product([0, 2], [0, 0.5], [0, 1], [0, 1]))


@pytest.mark.parametrize("vs, bd, rf, rs", IKILI_GIRDILER)
def test_ikili_girdiler(simulasyon, vs, bd, rf, rs):
    assert siddet(vs, bd, rf, rs) == pytest.approx(
        skfuzzy_siddet(simulasyon, vs, bd, rf, rs), abs=TOLERANS)


@pytest.mark.parametrize("vaka", TABLO5, ids=lambda v: f"vaka{v[0]}")
def test_tablo5_vakalari(simulasyon, vaka):
    _, vs, bd, rf, rs, _, _ = vaka
    assert siddet(vs, bd, rf, rs) == pytest.approx(
        skfuzzy_siddet(simulasyon, vs, bd, rf, rs), abs=TOLERANS)


def test_surekli_izgara(simulasyon):
    """Kenar geçişlerini de kapsayan sürekli girdi ızgarası."""
    vs_degerleri = [0, 3, 4.5, 5, 5.5, 6.5, 7, 10, 18]
    bd_degerleri = [0, 0.1, 0.22, 0.3, 0.5, 0.7, 0.77, 0.9, 1]
    rf_rs_degerleri = [0, 0.45, 0.5, 0.55, 1]
    farklar = []
    for vs, bd, rf, rs in itertools.product(
            vs_degerleri, bd_degerleri, rf_rs_degerleri, rf_rs_degerleri):
        fark = abs(siddet(vs, bd, rf, rs) - skfuzzy_siddet(simulasyon, vs, bd, rf, rs))
        farklar.append(((vs, bd, rf, rs), fark))
    en_kotu_girdi, en_buyuk_fark = max(farklar, key=lambda f: f[1])
    assert en_buyuk_fark < TOLERANS, f"{en_kotu_girdi}: fark {en_buyuk_fark:.5f}"
