"""Kesin modelin kontrolü."""

import itertools

import pytest

from src.kesin_model import kesin_kural, kesin_siddet
from src.mamdani import siddet


@pytest.mark.parametrize("vs, bd, rf, rs",
                         list(itertools.product([0, 2], [0, 0.5], [0, 1], [0, 1])))
def test_ikili_girdilerde_bulanikla_ayni(vs, bd, rf, rs):
    # Gerçek verideki 16 kombinasyonda iki model aynı sonucu vermeli
    assert kesin_siddet(vs, bd, rf, rs) == pytest.approx(siddet(vs, bd, rf, rs), abs=0.001)


def test_sinirlar():
    assert kesin_kural(4.4, 0, 0, 0) == 1      # low
    assert kesin_kural(4.5, 0, 0, 0) == 13     # medium
    assert kesin_kural(6.5, 0, 0, 0) == 25     # high
    assert kesin_kural(0, 0.25, 0, 0) == 5     # BD high
    assert kesin_kural(0, 0.75, 0, 0) == 9     # BD veryhigh
    assert kesin_kural(0, 0, 0.5, 0.5) == 4    # RF, RS meaningful


def test_cikti_uc_degerden_biri():
    for girdi in [(0, 0, 0, 0), (5, 0.1, 0.3, 0.9), (10, 0.9, 1, 1)]:
        assert round(kesin_siddet(*girdi), 3) in (0.1, 0.5, 0.9)
