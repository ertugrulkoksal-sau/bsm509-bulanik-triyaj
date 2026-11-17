"""Gerçek veride hangi kuralların kaç kayıtta ateşlendiğini sayar (bulgu B3).

Girdiler ikili olduğu için en fazla 16 farklı girdi kombinasyonu var.
Her kombinasyonda çıkarımı bir kez yapıp kural güçlerini o kombinasyonun
kayıt sayısıyla çarparak sayarız.

Çalıştırma:  python -m analiz.kural_ateslenme
Çıktılar:    sonuclar/kural_ateslenme.csv, sonuclar/girdi_uyelikleri.csv
"""

from pathlib import Path

import pandas as pd

from src.mamdani import bulaniklastir, cikarim
from src.model import KURALLAR
from src.veri import bos_yanitlari_at, girdileri_hesapla, oku

VERI_YOLU = Path("data/MICRODADOS.csv")
SONUC_KLASORU = Path("sonuclar")


def girdi_uyelikleri():
    """Veride görülen girdi değerlerinin her terimdeki üyelik derecesi."""
    satirlar = []
    for degisken, degerler in [("VS", [0, 2]), ("BD", [0, 0.5]), ("RF", [0, 1]), ("RS", [0, 1])]:
        for deger in degerler:
            girdiler = {"VS": 0, "BD": 0, "RF": 0, "RS": 0, degisken: deger}
            for terim, derece in bulaniklastir(girdiler)[degisken].items():
                satirlar.append({"degisken": degisken, "deger": deger,
                                 "terim": terim, "uyelik": derece})
    return pd.DataFrame(satirlar)


def kural_sayimi(kombinasyonlar):
    """Her kural için: ateşlendiği kayıt sayısı (güç > 0)."""
    sayac = [0] * len(KURALLAR)
    for k in kombinasyonlar.itertuples():
        gucler = cikarim(k.VS, k.BD, k.RF, k.RS)["kural_gucleri"]
        for i, guc in enumerate(gucler):
            if guc > 0:
                sayac[i] += k.kayit
    satirlar = []
    for i, (vs, bd, rf, rs, sv) in enumerate(KURALLAR):
        satirlar.append({"kural": i + 1, "VS": vs, "BD": bd, "RF": rf, "RS": rs,
                         "SV": sv, "ateslendigi_kayit": sayac[i]})
    return pd.DataFrame(satirlar)


def ates_etkisi(kombinasyonlar):
    """Ateş (VS 0 -> 2) değişince SV değişiyor mu? Diğer girdiler sabit."""
    satirlar = []
    for k in kombinasyonlar[kombinasyonlar["VS"] == 0].itertuples():
        sv_atessiz = cikarim(0, k.BD, k.RF, k.RS)["sv"]
        sv_atesli = cikarim(2, k.BD, k.RF, k.RS)["sv"]
        satirlar.append({"BD": k.BD, "RF": k.RF, "RS": k.RS,
                         "SV_ates_yok": round(sv_atessiz, 3),
                         "SV_ates_var": round(sv_atesli, 3),
                         "fark": round(sv_atesli - sv_atessiz, 6)})
    return pd.DataFrame(satirlar)


def main():
    if not VERI_YOLU.exists():
        print(f"{VERI_YOLU} bulunamadı. İndirme adımı: data/README.md")
        return
    df = girdileri_hesapla(bos_yanitlari_at(oku(VERI_YOLU)))
    kombinasyonlar = (df.groupby(["VS", "BD", "RF", "RS"]).size()
                      .rename("kayit").reset_index())
    toplam = int(kombinasyonlar["kayit"].sum())

    print("1) Veride görülen girdi değerlerinin üyelik dereceleri")
    uyelik = girdi_uyelikleri()
    uyelik.to_csv(SONUC_KLASORU / "girdi_uyelikleri.csv", index=False)
    print(uyelik[uyelik["uyelik"] > 0].to_string(index=False))

    print("\n2) Ateşin etkisi (VS = 0 ve VS = 2, diğer girdiler aynı)")
    print(ates_etkisi(kombinasyonlar).to_string(index=False))

    print(f"\n3) Kural başına ateşlendiği kayıt sayısı (toplam {toplam:,} kayıt)")
    sayim = kural_sayimi(kombinasyonlar)
    sayim["yuzde"] = (100 * sayim["ateslendigi_kayit"] / toplam).round(2)
    sayim.to_csv(SONUC_KLASORU / "kural_ateslenme.csv", index=False)
    print(sayim.to_string(index=False))
    calisan = sayim[sayim["ateslendigi_kayit"] > 0]["kural"].tolist()
    print(f"\nEn az bir kayıtta ateşlenen kurallar: {calisan} ({len(calisan)}/36)")
    print(f"Toplam ateşlenme = {sayim['ateslendigi_kayit'].sum():,} "
          f"(her kayıtta tam bir kural ateşleniyorsa toplam kayda eşit olmalı)")


if __name__ == "__main__":
    main()
