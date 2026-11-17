"""Veri hattının ön işleme kurallarını küçük bir örnek dosyayla dener.

Buradaki 5 satır analiz verisi DEĞİLDİR: kuralları (ateş -> 2, "-" -> atılır
vb.) kontrol etmek için elle yazılmış birim test kayıtlarıdır.
Gerçek analizler data/MICRODADOS.csv ile yapılır.
"""

import pytest

from src.veri import KOMORBIDITE_SUTUNLARI, OKUNACAK_SUTUNLAR, hazirla

KOMORBIDITE_YOK = ["Não"] * len(KOMORBIDITE_SUTUNLARI)


def satir(febre, dificuldade, belirtiler, komorbidite, idade, gestante,
          internado="Não", evolucao="Cura"):
    """OKUNACAK_SUTUNLAR sırasında bir CSV satırı üretir."""
    degerler = ([febre, dificuldade] + belirtiler + komorbidite
                + [internado, idade, gestante, evolucao])
    return ";".join(degerler)


@pytest.fixture
def ornek_dosya(tmp_path):
    belirti_yok = ["Não"] * 5
    satirlar = [
        ";".join(OKUNACAK_SUTUNLAR),
        # 1) hiçbir şey yok, 30 yaş -> 0,0,0,0
        satir("Não", "Não", belirti_yok, KOMORBIDITE_YOK, "30 anos, 1 meses, 2 dias", "Não"),
        # 2) ateş + öksürük, 65 yaş -> VS=2, RF=1, RS=1
        satir("Sim", "Não", ["Sim"] + ["Não"] * 4, KOMORBIDITE_YOK, "65 anos, 0 meses, 0 dias", "Não"),
        # 3) nefes darlığı + diyabet -> BD=0,5, RF=1
        satir("Não", "Sim", belirti_yok, ["Não", "Não", "Não", "Sim", "Não", "Não"], "40 anos", "Não"),
        # 4) gebe, baş ağrısı -> RF=1, RS=1
        satir("Não", "Não", ["Não"] * 4 + ["Sim"], KOMORBIDITE_YOK, "28 anos", "2º Trimestre"),
        # 5) Febre "-" -> atılmalı
        satir("-", "Não", belirti_yok, KOMORBIDITE_YOK, "50 anos", "Não"),
        # 6) yalnız sigara "-" -> atılmamalı (kapsülle aynı filtre), RF=0
        satir("Não", "Não", belirti_yok, ["Não"] * 4 + ["-", "Não"], "35 anos", "Não"),
    ]
    yol = tmp_path / "ornek.csv"
    yol.write_text("\n".join(satirlar), encoding="ISO-8859-1")
    return yol


def test_bos_yanitli_satir_atilir(ornek_dosya):
    df = hazirla(ornek_dosya)
    assert len(df) == 5


def test_girdi_kodlamasi(ornek_dosya):
    df = hazirla(ornek_dosya)
    girdiler = df[["VS", "BD", "RF", "RS"]].values.tolist()
    assert girdiler == [
        [0, 0, 0, 0],
        [2, 0, 1, 1],
        [0, 0.5, 1, 0],
        [0, 0, 1, 1],
        [0, 0, 0, 0],
    ]


def test_siddet_ve_karar(ornek_dosya):
    df = hazirla(ornek_dosya)
    # Kural 1 (mild) -> 0,1; kural 4 (severe) -> 0,9; kural 7 (severe) -> 0,9
    assert df["SV"].tolist() == pytest.approx([0.1, 0.9, 0.9, 0.9, 0.1], abs=0.001)
    assert df["ModelYatis"].tolist() == [False, True, True, True, False]
