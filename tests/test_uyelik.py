"""Üyelik fonksiyonlarının elle bilinen noktalarda kontrolü."""

import numpy as np
import pytest

from src.uyelik import trapmf, trimf


def test_yamuk_kenarlar_ve_tepe():
    # trapmf[4, 5, 6, 7]: 4'te 0, 4,5'te 0,5, 5..6 arası 1, 6,5'te 0,5, 7'de 0
    x = np.array([3, 4, 4.5, 5, 5.5, 6, 6.5, 7, 8])
    beklenen = [0, 0, 0.5, 1, 1, 1, 0.5, 0, 0]
    assert trapmf(x, 4, 5, 6, 7) == pytest.approx(beklenen)


def test_yamuk_dikey_sol_kenar():
    # VS low = trapmf[0, 0, 4, 5]: 0'da 1 olmalı (sol kenar dikey)
    assert trapmf(0, 0, 0, 4, 5) == pytest.approx(1.0)
    assert trapmf(4.5, 0, 0, 4, 5) == pytest.approx(0.5)


def test_yamuk_dikey_sag_kenar():
    # VS high = trapmf[6, 7, 18, 18]: 18'de 1 olmalı (sağ kenar dikey)
    assert trapmf(18, 6, 7, 18, 18) == pytest.approx(1.0)
    assert trapmf(6.5, 6, 7, 18, 18) == pytest.approx(0.5)


def test_ucgen():
    # SV moderate = trimf[0,2, 0,5, 0,8]
    x = np.array([0.2, 0.35, 0.5, 0.65, 0.8])
    assert trimf(x, 0.2, 0.5, 0.8) == pytest.approx([0, 0.5, 1, 0.5, 0])


def test_ucgen_dikey_kenarlar():
    # SV mild = trimf[0, 0, 0,3] ve severe = trimf[0,7, 1, 1]
    assert trimf(0, 0, 0, 0.3) == pytest.approx(1.0)
    assert trimf(0.15, 0, 0, 0.3) == pytest.approx(0.5)
    assert trimf(1, 0.7, 1, 1) == pytest.approx(1.0)
    assert trimf(0.85, 0.7, 1, 1) == pytest.approx(0.5)
