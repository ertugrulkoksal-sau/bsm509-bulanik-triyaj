"""Veri dosyasını kapsül çıktısıyla karşılaştırır.

Çalıştırma (proje klasöründen):  python -m analiz.veri_ozeti
"""

from pathlib import Path

from src.makale_degerleri import KAPSUL_FEBRE, TOPLAM_KAYIT
from src.veri import bos_yanitlari_at, girdileri_hesapla, oku, siddet_ekle

VERI_YOLU = Path("data/MICRODADOS.csv")


def main():
    if not VERI_YOLU.exists():
        print(f"{VERI_YOLU} bulunamadı. İndirme adımı: data/README.md")
        return

    df = oku(VERI_YOLU)
    print(f"Toplam kayıt: {len(df):,}  (makale: {TOPLAM_KAYIT:,})")

    print("\nFebre dağılımı (ham veri):")
    print(df["Febre"].value_counts().to_string())

    print("\nGestante yanıtları (gebelik kodlamasını kontrol için):")
    print(df["Gestante"].value_counts().to_string())

    temiz = bos_yanitlari_at(df)
    print(f"\n'-' yanıtlı satırlar atıldıktan sonra: {len(temiz):,} "
          f"({len(df) - len(temiz):,} satır atıldı)")

    # Kapsüldeki Febre sayıları ön işleme SONRASINA ait
    print("\nFebre dağılımı (ön işleme sonrası) ve kapsül:")
    febre = temiz["Febre"].value_counts()
    for yanit, beklenen in KAPSUL_FEBRE.items():
        durum = "uyuşuyor" if febre.get(yanit, 0) == beklenen else "FARKLI"
        print(f"  {yanit}: bizim {febre.get(yanit, 0):,}  kapsül {beklenen:,}  -> {durum}")

    temiz = siddet_ekle(girdileri_hesapla(temiz))
    print("\nGirdi kombinasyonları ve SV:")
    tablo = (temiz.groupby(["VS", "BD", "RF", "RS", "SV"]).size()
             .rename("kayit").reset_index())
    print(tablo.to_string(index=False))

    print("\nSV dağılımı:")
    print(temiz["SV"].round(3).value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
