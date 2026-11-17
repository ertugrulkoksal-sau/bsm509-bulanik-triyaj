"""Üyelik fonksiyonları (ÜF): yamuk (trapmf) ve üçgen (trimf).

Parametre sırası MATLAB / scikit-fuzzy ile aynıdır:
    trapmf(x, a, b, c, d) -> a'da 0, b..c arası 1, d'de 0
    trimf(x, a, b, c)     -> a'da 0, b'de 1, c'de 0
"""

import numpy as np


def yukselen_kenar(x, a, b):
    """a'dan b'ye 0'dan 1'e doğrusal çıkan kenar.

    a == b ise kenar dikeydir: x >= a olan her nokta 1 olur
    (ör. trapmf[0, 0, 4, 5] sol kenarı).
    """
    if b == a:
        return np.where(x >= a, 1.0, 0.0)
    return np.clip((x - a) / (b - a), 0.0, 1.0)


def dusen_kenar(x, c, d):
    """c'den d'ye 1'den 0'a doğrusal inen kenar.

    c == d ise kenar dikeydir: x <= c olan her nokta 1 olur
    (ör. trapmf[6, 7, 18, 18] sağ kenarı).
    """
    if d == c:
        return np.where(x <= c, 1.0, 0.0)
    return np.clip((d - x) / (d - c), 0.0, 1.0)


def trapmf(x, a, b, c, d):
    """Yamuk ÜF: iki kenarın küçüğü (min) yamuğu verir."""
    x = np.asarray(x, dtype=float)
    return np.minimum(yukselen_kenar(x, a, b), dusen_kenar(x, c, d))


def trimf(x, a, b, c):
    """Üçgen ÜF: tepesi tek noktaya inmiş yamuktur (b == c)."""
    return trapmf(x, a, b, b, c)


def uyelik_hesapla(x, tip, parametreler):
    """Model tablosundaki ('trap', [...]) / ('tri', [...]) kaydını hesaplar."""
    if tip == "trap":
        return trapmf(x, *parametreler)
    if tip == "tri":
        return trimf(x, *parametreler)
    raise ValueError(f"Bilinmeyen ÜF tipi: {tip}")
