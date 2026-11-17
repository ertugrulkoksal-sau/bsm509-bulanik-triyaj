"""Sürekli girdilerle model davranışı: yüzey ve duyarlılık grafikleri.

Gerçek veride girdiler ikili (VS 0/2, BD 0/0,5, RF ve RS 0/1). Burada aynı
modeli girdilerin bütün evreninde çalıştırıp bulanık yapının nerede fark
yarattığını gösteriyoruz. Her grafikte aynı kuralların kesin sürümü de var.

Çalıştırma:  python -m analiz.yuzey_duyarlilik
Çıktılar:    sonuclar/yuzey_vs_bd.png, sonuclar/yuzey_3b.png,
             sonuclar/duyarlilik.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.kesin_model import kesin_siddet
from src.mamdani import siddet
from src.model import YATIS_ESIGI

SONUC_KLASORU = Path("sonuclar")
VS_IZGARA = np.round(np.arange(0, 18.001, 0.1), 2)
BD_IZGARA = np.round(np.arange(0, 1.0001, 0.01), 2)
# Yüzeyde sabit tutulan RF, RS çiftleri
RF_RS_CIFTLERI = [(0, 0), (0, 1), (1, 1)]


def yuzey_hesapla(model, rf, rs):
    """VS x BD ızgarasında modelin SV değerleri (satır: BD, sütun: VS)."""
    yuzey = np.zeros((len(BD_IZGARA), len(VS_IZGARA)))
    for i, bd in enumerate(BD_IZGARA):
        for j, vs in enumerate(VS_IZGARA):
            yuzey[i, j] = model(vs, bd, rf, rs)
    return yuzey


def isi_haritasi(ax, yuzey, baslik):
    """Bir yüzeyi ısı haritası olarak çizer; 0,75 eşiğini kontur olarak ekler.

    Tanımsız (NaN) noktalar kırmızı gösterilir.
    """
    renk_haritasi = plt.get_cmap("viridis").copy()
    renk_haritasi.set_bad("red")
    sinirlar = [VS_IZGARA[0], VS_IZGARA[-1], BD_IZGARA[0], BD_IZGARA[-1]]
    resim = ax.imshow(np.ma.masked_invalid(yuzey), origin="lower", aspect="auto",
                      extent=sinirlar, cmap=renk_haritasi, vmin=0, vmax=1)
    ax.contour(VS_IZGARA, BD_IZGARA, np.nan_to_num(yuzey), levels=[YATIS_ESIGI],
               colors="white", linewidths=1.2)
    # Gerçek verideki dört (VS, BD) noktası
    ax.scatter([0, 2, 0, 2], [0, 0, 0.5, 0.5], s=18, c="white", edgecolors="black", zorder=3)
    ax.set_title(baslik, fontsize=10)
    return resim


def yuzey_grafigi(yuzeyler):
    fig, eksenler = plt.subplots(2, 3, figsize=(13, 7), sharex=True, sharey=True)
    for sutun, (rf, rs) in enumerate(RF_RS_CIFTLERI):
        isi_haritasi(eksenler[0, sutun], yuzeyler[("bulanik", rf, rs)],
                     f"Bulanık, RF = {rf}, RS = {rs}")
        resim = isi_haritasi(eksenler[1, sutun], yuzeyler[("kesin", rf, rs)],
                             f"Kesin, RF = {rf}, RS = {rs}")
    for ax in eksenler[1]:
        ax.set_xlabel("VS (yaşamsal bulgular)")
    for ax in eksenler[:, 0]:
        ax.set_ylabel("BD (nefes darlığı)")
    fig.colorbar(resim, ax=eksenler, label="SV (şiddet)", shrink=0.8)
    fig.suptitle("SV yüzeyi. Beyaz çizgi: SV = 0,75 sınırı. Kırmızı: hiçbir kural "
                 "ateşlenmiyor (tanımsız). Noktalar: gerçek verideki girdiler.", fontsize=11)
    fig.savefig(SONUC_KLASORU / "yuzey_vs_bd.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def uc_boyutlu_grafik(yuzey, rf, rs):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(projection="3d")
    vs, bd = np.meshgrid(VS_IZGARA, BD_IZGARA)
    ax.plot_surface(vs, bd, np.ma.masked_invalid(yuzey), cmap="viridis",
                    vmin=0, vmax=1, linewidth=0)
    ax.set_xlabel("VS")
    ax.set_ylabel("BD")
    ax.set_zlabel("SV")
    ax.set_title(f"Bulanık model yüzeyi (RF = {rf}, RS = {rs})")
    ax.view_init(elev=28, azim=-125)
    fig.savefig(SONUC_KLASORU / "yuzey_3b.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def duyarlilik_grafigi():
    """Bir girdiyi evren boyunca değiştir, diğerlerini sabit tut."""
    paneller = [
        ("VS", np.round(np.arange(0, 18.001, 0.05), 3), lambda x: (x, 0, 0, 1),
         "BD = 0, RF = 0, RS = 1", [0, 2]),
        ("BD", np.round(np.arange(0, 1.0001, 0.005), 4), lambda x: (0, x, 0, 1),
         "VS = 0, RF = 0, RS = 1", [0, 0.5]),
        ("RF", np.round(np.arange(0, 1.0001, 0.005), 4), lambda x: (0, 0, x, 1),
         "VS = 0, BD = 0, RS = 1", [0, 1]),
    ]
    fig, eksenler = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
    for ax, (ad, degerler, girdi, sabitler, veri_degerleri) in zip(eksenler, paneller):
        bulanik = [siddet(*girdi(x)) for x in degerler]
        kesin = [kesin_siddet(*girdi(x)) for x in degerler]
        ax.plot(degerler, kesin, color="#7f7f7f", linestyle="--", label="Kesin")
        ax.plot(degerler, bulanik, color="#1f77b4", label="Bulanık")
        for x in veri_degerleri:
            ax.axvline(x, color="black", linestyle=":", linewidth=0.8)
        ax.axhline(YATIS_ESIGI, color="#d62728", linewidth=0.8)
        ax.set_xlabel(ad)
        ax.set_title(sabitler, fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
    eksenler[0].set_ylabel("SV")
    eksenler[0].legend(frameon=False, loc="center right")
    fig.suptitle("Duyarlılık: tek girdi değişiyor. Noktalı çizgi: gerçek verideki "
                 "değerler. Kırmızı: 0,75 eşiği.", fontsize=11)
    fig.tight_layout()
    fig.savefig(SONUC_KLASORU / "duyarlilik.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    SONUC_KLASORU.mkdir(exist_ok=True)
    yuzeyler = {}
    for rf, rs in RF_RS_CIFTLERI:
        print(f"Yüzey hesaplanıyor: RF = {rf}, RS = {rs}")
        yuzeyler[("bulanik", rf, rs)] = yuzey_hesapla(siddet, rf, rs)
        yuzeyler[("kesin", rf, rs)] = yuzey_hesapla(kesin_siddet, rf, rs)
    yuzey_grafigi(yuzeyler)
    uc_boyutlu_grafik(yuzeyler[("bulanik", 0, 1)], 0, 1)
    duyarlilik_grafigi()
    print("Kaydedildi: sonuclar/yuzey_vs_bd.png, yuzey_3b.png, duyarlilik.png")


if __name__ == "__main__":
    main()
