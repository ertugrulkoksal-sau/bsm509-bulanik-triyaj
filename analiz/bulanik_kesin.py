"""Bulanık model ile aynı kuralların kesin sürümünü ölçerek karşılaştırır.

1. Gerçek veride: 1,67 milyon kayıtta iki model kaç kayıtta farklı?
2. Sürekli girdi ızgarasında: fark ne kadar, 0,75 kararı kaç noktada değişiyor?
3. Her girdide iki terimin örtüştüğü (bulanık geçiş) bölgenin genişliği.

Çalıştırma:  python -m analiz.bulanik_kesin
Çıktı:       sonuclar/bulanik_kesin.csv, sonuclar/ortusme_bolgeleri.csv
"""

import itertools
from pathlib import Path

import numpy as np
import pandas as pd

from src.kesin_model import kesin_siddet
from src.mamdani import bulaniklastir, cikarim, siddet
from src.model import GIRDI_SIRASI, GIRDILER, YATIS_ESIGI
from src.veri import bos_yanitlari_at, girdileri_hesapla, oku

VERI_YOLU = Path("data/MICRODADOS.csv")
SONUC_KLASORU = Path("sonuclar")

# Izgara: VS 0,5 adım; BD 0,02 adım; RF ve RS 0,1 adım
IZGARA = {
    "VS": np.round(np.arange(0, 18.001, 0.5), 3),
    "BD": np.round(np.arange(0, 1.0001, 0.02), 3),
    "RF": np.round(np.arange(0, 1.0001, 0.1), 3),
    "RS": np.round(np.arange(0, 1.0001, 0.1), 3),
}


def gercek_veride_karsilastir():
    """16 girdi kombinasyonunda iki modeli karşılaştırıp kayıt sayısıyla tartar."""
    df = girdileri_hesapla(bos_yanitlari_at(oku(VERI_YOLU)))
    kombinasyonlar = df.groupby(["VS", "BD", "RF", "RS"]).size().rename("kayit").reset_index()
    farkli_kayit = 0
    for k in kombinasyonlar.itertuples():
        if abs(siddet(k.VS, k.BD, k.RF, k.RS) - kesin_siddet(k.VS, k.BD, k.RF, k.RS)) > 0.001:
            farkli_kayit += k.kayit
    return int(kombinasyonlar["kayit"].sum()), farkli_kayit


def kismi_uyelik_var(dereceler):
    """Herhangi bir girdi tek bir terime tam (1,0) üye değilse True.

    Bütün girdiler tam üyeyse yalnız bir kural tam güçle ateşlenir ve
    bulanık model kesin modelle aynı sonucu verir.
    """
    for terim_dereceleri in dereceler.values():
        degerler = sorted(terim_dereceleri.values(), reverse=True)
        if degerler[0] < 1 or degerler[1] > 0:
            return True
    return False


def izgarada_karsilastir():
    """Izgaranın her noktasında iki modeli hesaplar."""
    satirlar = []
    for vs, bd, rf, rs in itertools.product(*[IZGARA[d] for d in GIRDI_SIRASI]):
        sonuc = cikarim(vs, bd, rf, rs)
        satirlar.append({"VS": vs, "BD": bd, "RF": rf, "RS": rs,
                         "bulanik": sonuc["sv"],
                         "kesin": kesin_siddet(vs, bd, rf, rs),
                         "kismi": kismi_uyelik_var(sonuc["dereceler"])})
    tablo = pd.DataFrame(satirlar)
    tablo["fark"] = (tablo["bulanik"] - tablo["kesin"]).abs()
    tablo["karar_farkli"] = (tablo["bulanik"] >= YATIS_ESIGI) != (tablo["kesin"] >= YATIS_ESIGI)
    return tablo


def ortusme_bolgeleri():
    """Her girdinin evreninde birden çok terimin aynı anda > 0 olduğu pay."""
    satirlar = []
    for degisken in GIRDI_SIRASI:
        alt, ust = GIRDILER[degisken]["evren"]
        noktalar = np.linspace(alt, ust, 18001)
        ortusen = 0
        bos = 0
        for x in noktalar:
            sifirdan_buyuk = sum(d > 0 for d in bulaniklastir(
                {"VS": 0, "BD": 0, "RF": 0, "RS": 0, degisken: x})[degisken].values())
            ortusen += sifirdan_buyuk >= 2
            bos += sifirdan_buyuk == 0
        satirlar.append({"degisken": degisken,
                         "ortusme_yuzde": round(100 * ortusen / len(noktalar), 1),
                         "hicbir_terim_yok_nokta": bos})
    return pd.DataFrame(satirlar)


def main():
    SONUC_KLASORU.mkdir(exist_ok=True)

    print("1) Gerçek veri")
    toplam, farkli = gercek_veride_karsilastir()
    print(f"   {toplam:,} kaydın {farkli:,} tanesinde iki model farklı SV veriyor.")

    print("\n2) Sürekli ızgara (her girdi evreninde eşit aralıklı)")
    tablo = izgarada_karsilastir()
    tanimli = tablo.dropna(subset=["bulanik"])
    ozet = {
        "izgara_noktasi": len(tablo),
        "bulanik_tanimsiz": int(tablo["bulanik"].isna().sum()),
        "ayni_yuzde (fark < 0,001)": round(100 * (tanimli["fark"] < 0.001).mean(), 1),
        "ortalama_mutlak_fark": round(tanimli["fark"].mean(), 4),
        "en_buyuk_fark": round(tanimli["fark"].max(), 3),
        "karar_farkli_yuzde (0,75)": round(100 * tanimli["karar_farkli"].mean(), 1),
    }
    for ad, deger in ozet.items():
        print(f"   {ad}: {deger}")
    pd.DataFrame([ozet]).to_csv(SONUC_KLASORU / "bulanik_kesin.csv", index=False)

    print("\n   Kısmi üyelik var mı? (en az bir girdi tek terime tam üye değil)")
    for kismi, grup in tanimli.groupby("kismi"):
        print(f"   kısmi = {kismi}: {len(grup):,} nokta, "
              f"aynı %{100 * (grup['fark'] < 0.001).mean():.1f}, "
              f"karar farklı %{100 * grup['karar_farkli'].mean():.1f}, "
              f"en büyük fark {grup['fark'].max():.3f}")

    print("\n3) Örtüşme bölgeleri (iki terimin birlikte > 0 olduğu pay)")
    ortusme = ortusme_bolgeleri()
    ortusme.to_csv(SONUC_KLASORU / "ortusme_bolgeleri.csv", index=False)
    print(ortusme.to_string(index=False))


if __name__ == "__main__":
    main()
