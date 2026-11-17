"""Makalede yazılı değerler (karşılaştırma için, elle aktarıldı).

Kaynak: Galo vd. (2022), Applied Soft Computing 129, 109626.
PMC tam metni: https://pmc.ncbi.nlm.nih.gov/articles/PMC9487152/
"""

# Tablo 5: 15 vaka. (vaka no, VS, BD, RF, RS, makaledeki terim, makaledeki SV)
# Not: 3. vakada BD için sayı basılmamış, terim "Minimal or absent" -> 0 alındı.
TABLO5 = [
    (1, 2, 0.5, 1, 1, "severe", 0.873),
    (2, 0, 0.0, 1, 0, "mild", 0.163),
    (3, 2, 0.0, 1, 1, "severe", 0.8737),
    (4, 2, 0.5, 1, 1, "severe", 0.8737),
    (5, 2, 0.0, 1, 1, "moderate", 0.500),
    (6, 0, 0.0, 0, 1, "mild", 0.163),
    (7, 2, 0.0, 0, 1, "mild", 0.163),
    (8, 0, 0.0, 0, 1, "mild", 0.163),
    (9, 2, 0.0, 0, 1, "mild", 0.163),
    (10, 0, 0.0, 0, 1, "mild", 0.163),
    (11, 0, 0.0, 0, 1, "mild", 0.163),
    (12, 0, 0.0, 0, 1, "mild", 0.163),
    (13, 0, 0.5, 0, 1, "mild", 0.163),
    (14, 0, 0.0, 0, 1, "mild", 0.163),
    (15, 0, 0.5, 0, 1, "mild", 0.163),
]

# Sonuçlar bölümündeki sayılar (Espírito Santo verisi)
TOPLAM_KAYIT = 1_679_329
COVID_OLUM = 11_510
DIGER_OLUM = 3_432
# Mevcut triyajda yatırılan ölüm oranı
FIILI_YATIS_COVID_OLUM = 0.6329
FIILI_YATIS_DIGER_OLUM = 0.4715
# 0,75 eşiğinde yatırılmayan COVID ölümü oranı
YATIRILMAYAN_FIILI = 0.37
YATIRILMAYAN_MODEL = 0.18

# Kapsül çıktısı (proje brifinden): 0,75 eşiğinde yatış önerilen kayıt oranı
KAPSUL_YATIS_ORANI = 0.268
KAPSUL_SV_DEGERLERI = (0.1, 0.5, 0.9)
# Kapsüldeki Febre dağılımı (ön işleme öncesi)
KAPSUL_FEBRE = {"Não": 1_134_433, "Sim": 540_919}
