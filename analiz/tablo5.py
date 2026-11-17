"""Makale Tablo 5'teki 15 vakayı motorumuzla tek tek hesaplar.

Çalıştırma:  python -m analiz.tablo5
Çıktı:       sonuclar/tablo5.csv
"""

from pathlib import Path

import pandas as pd

from src.makale_degerleri import TABLO5
from src.mamdani import cikarim
from src.model import CIKTI, KURALLAR, YATIS_ESIGI
from src.uyelik import uyelik_hesapla

CIKTI_DOSYASI = Path("sonuclar/tablo5.csv")


def en_yuksek_terim(sv):
    """SV'nin en yüksek üyelikle düştüğü çıktı terimi (mild/moderate/severe)."""
    dereceler = {terim: float(uyelik_hesapla(sv, tip, p))
                 for terim, (tip, p) in CIKTI["terimler"].items()}
    return max(dereceler, key=dereceler.get)


def vaka_hesapla(vaka):
    """Bir vakayı hesaplar; ateşlenen kuralları ve makaleyle farkı döndürür."""
    no, vs, bd, rf, rs, makale_terim, makale_sv = vaka
    sonuc = cikarim(vs, bd, rf, rs)
    atesenler = [i + 1 for i, guc in enumerate(sonuc["kural_gucleri"]) if guc > 0]
    kural_terimi = KURALLAR[atesenler[0] - 1][4] if len(atesenler) == 1 else "birden çok"
    return {
        "vaka": no, "VS": vs, "BD": bd, "RF": rf, "RS": rs,
        "ateslenen_kural": ",".join(map(str, atesenler)),
        "kural_tablosuna_gore": kural_terimi,
        "bizim_SV": round(sonuc["sv"], 3),
        "bizim_terim": en_yuksek_terim(sonuc["sv"]),
        "makale_terim": makale_terim,
        "makale_SV": makale_sv,
        "terim_uyusuyor": en_yuksek_terim(sonuc["sv"]) == makale_terim,
        "bizim_karar_075": sonuc["sv"] >= YATIS_ESIGI,
        "makale_karar_075": makale_sv >= YATIS_ESIGI,
    }


def main():
    tablo = pd.DataFrame([vaka_hesapla(v) for v in TABLO5])
    CIKTI_DOSYASI.parent.mkdir(exist_ok=True)
    tablo.to_csv(CIKTI_DOSYASI, index=False)
    print(tablo.to_string(index=False))
    farkli = tablo[~tablo["terim_uyusuyor"]]["vaka"].tolist()
    print(f"\nTerimi makaleyle uyuşmayan vakalar: {farkli}")
    print(f"Kaydedildi: {CIKTI_DOSYASI}")


if __name__ == "__main__":
    main()
