"""Veri hattı: MICRODADOS.csv -> modelin dört girdisi -> şiddet (SV).

Veri kaynağı: Espírito Santo eyaleti COVID-19 paneli mikroverisi
(MICRODADOS.csv), yazarların Code Ocean kapsülündeki kopya
(DOI 10.24433/CO.6430898.v1). Dosya `;` ayraçlı, ISO-8859-1 kodlamalı.

Girdi kodlaması (kapsüldeki ön işlemeyle aynı kurallar):
    VS = 2   ateş (Febre) varsa, yoksa 0
    BD = 0,5 nefes darlığı varsa, yoksa 0
    RF = 1   60 yaş ve üstü, komorbidite ya da gebelik varsa, yoksa 0
    RS = 1   öksürük, burun akıntısı, boğaz ağrısı, ishal ya da baş ağrısı varsa
"""

import pandas as pd

from src.mamdani import siddet
from src.model import YATIS_ESIGI

BELIRTI_SUTUNLARI = ["Tosse", "Coriza", "DorGarganta", "Diarreia", "Cefaleia"]
KOMORBIDITE_SUTUNLARI = [
    "ComorbidadePulmao", "ComorbidadeCardio", "ComorbidadeRenal",
    "ComorbidadeDiabetes", "ComorbidadeTabagismo", "ComorbidadeObesidade",
]
# "-" (boş yanıt) içeren satırlar bu sütunlara göre atılır.
# ComorbidadeTabagismo (sigara) bu listede YOK: kapsüldeki Febre sayıları
# (Não 1.134.433 / Sim 540.919) yalnız sigara sütunu filtreye katılmadığında
# tam tutuyor (bkz. sonuclar/bulgular.md, B0). Sigara RF hesabında yine kullanılır;
# "-" yanıtı "Sim" olmadığı için risk sayılmaz.
FILTRE_SUTUNLARI = (["Febre", "DificuldadeRespiratoria"] + BELIRTI_SUTUNLARI
                    + [s for s in KOMORBIDITE_SUTUNLARI if s != "ComorbidadeTabagismo"]
                    + ["FicouInternado"])
# Okunacak tüm sütunlar (595 MB'lık dosyanın yalnız gereken kısmı)
OKUNACAK_SUTUNLAR = (["Febre", "DificuldadeRespiratoria"] + BELIRTI_SUTUNLARI
                     + KOMORBIDITE_SUTUNLARI + ["FicouInternado",
                     "IdadeNaDataNotificacao", "Gestante", "Evolucao"])

# Gestante sütununda gebelik OLMADIĞINI gösteren yanıtlar. Veride görülen
# diğer yanıtlar gebelik sayılır: "1º trimeste", "2º trimeste", "3º trimeste"
# (veride "trimeste" diye yazılmış) ve "Idade gestacional ignorada"
# (gebe, haftası bilinmiyor).
GEBE_DEGIL = {"Não", "Ignorado", "Não se aplica"}


def oku(dosya_yolu):
    """CSV'den yalnız gereken sütunları metin olarak okur."""
    return pd.read_csv(dosya_yolu, sep=";", encoding="ISO-8859-1",
                       usecols=OKUNACAK_SUTUNLAR, dtype=str, keep_default_na=False)


def bos_yanitlari_at(df):
    """FILTRE_SUTUNLARI'ndan herhangi birinde "-" olan satırları atar."""
    bos_var = (df[FILTRE_SUTUNLARI] == "-").any(axis=1)
    return df[~bos_var].copy()


def yas_yil(idade_sutunu):
    """"45 anos, 3 meses, 2 dias" gibi metinden yılı (45) çıkarır.

    Sayı bulunamazsa NaN olur; bu kayıtlar 60 yaş koşulunu sağlamaz.
    """
    return pd.to_numeric(idade_sutunu.str.extract(r"(\d+)")[0], errors="coerce")


def girdileri_hesapla(df):
    """Dört model girdisini (VS, BD, RF, RS) yeni sütun olarak ekler."""
    df["VS"] = (df["Febre"] == "Sim") * 2.0
    df["BD"] = (df["DificuldadeRespiratoria"] == "Sim") * 0.5

    yasli = yas_yil(df["IdadeNaDataNotificacao"]) >= 60
    komorbidite = (df[KOMORBIDITE_SUTUNLARI] == "Sim").any(axis=1)
    gebe = ~df["Gestante"].isin(GEBE_DEGIL)
    df["RF"] = (yasli | komorbidite | gebe) * 1.0

    df["RS"] = (df[BELIRTI_SUTUNLARI] == "Sim").any(axis=1) * 1.0
    return df


def siddet_ekle(df):
    """Her farklı girdi kombinasyonu için SV'yi bir kez hesaplayıp eşler.

    Girdiler ikili olduğu için en fazla 2x2x2x2 = 16 kombinasyon vardır;
    1,6 milyon satırda tek tek çıkarım yapmaya gerek yoktur.
    """
    kombinasyonlar = df[["VS", "BD", "RF", "RS"]].drop_duplicates()
    kombinasyonlar["SV"] = [
        siddet(k.VS, k.BD, k.RF, k.RS) for k in kombinasyonlar.itertuples()
    ]
    return df.merge(kombinasyonlar, on=["VS", "BD", "RF", "RS"], how="left")


def karar_ekle(df, esik=YATIS_ESIGI):
    """SV eşiğe eşit ya da büyükse model yatış önerir."""
    df["ModelYatis"] = df["SV"] >= esik
    df["FiiliYatis"] = df["FicouInternado"] == "Sim"
    return df


def hazirla(dosya_yolu, esik=YATIS_ESIGI):
    """Tüm hattı çalıştırır: oku -> temizle -> girdiler -> SV -> karar."""
    df = oku(dosya_yolu)
    df = bos_yanitlari_at(df)
    df = girdileri_hesapla(df)
    df = siddet_ekle(df)
    df = karar_ekle(df, esik)
    return df
