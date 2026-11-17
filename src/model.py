"""Galo vd. (2022) triyaj modelinin tanımı: değişkenler, ÜF'ler, 36 kural.

Kaynaklar
- Kurallar: Galo, Roriz Junior, Pereira (2022), Applied Soft Computing 129,
  109626, Tablo 3. https://doi.org/10.1016/j.asoc.2022.109626
- ÜF parametreleri: makalede sayı olarak verilmiyor; yazarların Code Ocean
  kapsülündeki değerler kullanıldı (DOI 10.24433/CO.6430898.v1).

Kısaltmalar
    VS: yaşamsal bulgular (NEWS puanına dayalı, 0-18)
    BD: nefes darlığı (0-1)
    RF: risk faktörleri (0-1)
    RS: diğer belirtiler (0-1)
    SV: şiddet, çıktı (0-1)
"""

import numpy as np

# --- Girdi değişkenleri: her terim için (ÜF tipi, parametreler) ---
GIRDILER = {
    "VS": {
        "evren": (0, 18),
        "terimler": {
            "low": ("trap", [0, 0, 4, 5]),
            "medium": ("trap", [4, 5, 6, 7]),
            "high": ("trap", [6, 7, 18, 18]),
        },
    },
    "BD": {
        "evren": (0, 1),
        "terimler": {
            "minimal": ("trap", [0, 0, 0.2, 0.25]),
            "high": ("tri", [0.25, 0.5, 0.75]),
            "veryhigh": ("trap", [0.75, 0.8, 1, 1]),
        },
    },
    "RF": {
        "evren": (0, 1),
        "terimler": {
            "minimal": ("trap", [0, 0, 0.4, 0.6]),
            "meaningful": ("trap", [0.4, 0.6, 1, 1]),
        },
    },
    "RS": {
        "evren": (0, 1),
        "terimler": {
            "minimal": ("trap", [0, 0, 0.4, 0.6]),
            "meaningful": ("trap", [0.4, 0.6, 1, 1]),
        },
    },
}

# --- Çıktı değişkeni ---
CIKTI = {
    "evren": (0, 1),
    "terimler": {
        "mild": ("tri", [0, 0, 0.3]),
        "moderate": ("tri", [0.2, 0.5, 0.8]),
        "severe": ("tri", [0.7, 1, 1]),
    },
}

# Durulaştırmada kullanılan ayrık çıktı evreni (0,001 adım, 1001 nokta)
CIKTI_EVRENI = np.linspace(0, 1, 1001)

# --- Kural tabanı (makale Tablo 3) ---
# Her satır: (VS, BD, RF, RS) -> SV
# Okunuşu: EĞER VS=... VE BD=... VE RF=... VE RS=... İSE SV=...
KURALLAR = [
    # VS = low
    ("low", "minimal", "minimal", "minimal", "mild"),             # 1
    ("low", "minimal", "minimal", "meaningful", "mild"),          # 2
    ("low", "minimal", "meaningful", "minimal", "mild"),          # 3
    ("low", "minimal", "meaningful", "meaningful", "severe"),     # 4
    ("low", "high", "minimal", "minimal", "moderate"),            # 5
    ("low", "high", "minimal", "meaningful", "severe"),           # 6
    ("low", "high", "meaningful", "minimal", "severe"),           # 7
    ("low", "high", "meaningful", "meaningful", "severe"),        # 8
    ("low", "veryhigh", "minimal", "minimal", "severe"),          # 9
    ("low", "veryhigh", "minimal", "meaningful", "severe"),       # 10
    ("low", "veryhigh", "meaningful", "minimal", "severe"),       # 11
    ("low", "veryhigh", "meaningful", "meaningful", "severe"),    # 12
    # VS = medium
    ("medium", "minimal", "minimal", "minimal", "mild"),          # 13
    ("medium", "minimal", "minimal", "meaningful", "moderate"),   # 14
    ("medium", "minimal", "meaningful", "minimal", "moderate"),   # 15
    ("medium", "minimal", "meaningful", "meaningful", "moderate"),  # 16
    ("medium", "high", "minimal", "minimal", "moderate"),         # 17
    ("medium", "high", "minimal", "meaningful", "severe"),        # 18
    ("medium", "high", "meaningful", "minimal", "severe"),        # 19
    ("medium", "high", "meaningful", "meaningful", "severe"),     # 20
    ("medium", "veryhigh", "minimal", "minimal", "severe"),       # 21
    ("medium", "veryhigh", "minimal", "meaningful", "severe"),    # 22
    ("medium", "veryhigh", "meaningful", "minimal", "severe"),    # 23
    ("medium", "veryhigh", "meaningful", "meaningful", "severe"),  # 24
    # VS = high
    ("high", "minimal", "minimal", "minimal", "moderate"),        # 25
    ("high", "minimal", "minimal", "meaningful", "severe"),       # 26
    ("high", "minimal", "meaningful", "minimal", "severe"),       # 27
    ("high", "minimal", "meaningful", "meaningful", "severe"),    # 28
    ("high", "high", "minimal", "minimal", "severe"),             # 29
    ("high", "high", "minimal", "meaningful", "severe"),          # 30
    ("high", "high", "meaningful", "minimal", "severe"),          # 31
    ("high", "high", "meaningful", "meaningful", "severe"),       # 32
    ("high", "veryhigh", "minimal", "minimal", "severe"),         # 33
    ("high", "veryhigh", "minimal", "meaningful", "severe"),      # 34
    ("high", "veryhigh", "meaningful", "minimal", "severe"),      # 35
    ("high", "veryhigh", "meaningful", "meaningful", "severe"),   # 36
]

# Girdi sırası kurallardaki sütun sırasıyla aynı
GIRDI_SIRASI = ["VS", "BD", "RF", "RS"]

# Hastaneye yatış kararı için eşik (makalede 0,75; 0,50 de denenmiş)
YATIS_ESIGI = 0.75
