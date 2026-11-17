"""Makale/kapsül sonuçlarının yeniden üretimi.

1. SV dağılımı
2. 0,75 ve 0,50 eşiklerinde yatış önerilen kayıt oranı (kapsül: %26,8)
3. Ölüm vakalarında model önerisi ile fiili yatış karşılaştırması

Çalıştırma:  python -m analiz.yeniden_uretim
Çıktılar:    sonuclar/sv_dagilimi.csv/.png, sonuclar/yatis_oranlari.csv,
             sonuclar/olum_karsilastirma.csv, sonuclar/olum_karsilastirma.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src import makale_degerleri as makale
from src.veri import hazirla

VERI_YOLU = Path("data/MICRODADOS.csv")
SONUC_KLASORU = Path("sonuclar")
ESIKLER = [0.75, 0.50]
OLUM_TURLERI = {
    "COVID-19 ölümü": "Óbito pelo COVID-19",
    "Diğer nedenli ölüm": "Óbito por outras causas",
}


def sv_dagilimi(df):
    """Her SV değerinde kaç kayıt var, yüzdesi ne."""
    tablo = df["SV"].round(3).value_counts().sort_index().rename("kayit").to_frame()
    tablo["yuzde"] = 100 * tablo["kayit"] / len(df)
    return tablo.reset_index()


def yatis_oranlari(df):
    """Her eşikte modelin yatış önerdiği kayıt oranı."""
    satirlar = []
    for esik in ESIKLER:
        oneri = (df["SV"] >= esik).sum()
        satirlar.append({"esik": esik, "yatis_onerilen": oneri,
                         "toplam": len(df), "yuzde": 100 * oneri / len(df)})
    return pd.DataFrame(satirlar)


def olum_karsilastirma(df):
    """Ölen hastalarda: fiilen yatırılanlar ve modelin yatış önerdikleri.

    İki taban raporlanır:
    - "tum": o gruptaki bütün ölümler
    - "bilinen": FicouInternado yanıtı "Sim" ya da "Não" olanlar. Makaledeki
      %63,29 / %47,15 bu tabana göre hesaplanmış (bkz. bulgular.md, B4).
    """
    satirlar = []
    for ad, deger in OLUM_TURLERI.items():
        olenler = df[df["Evolucao"] == deger]
        bilinenler = olenler[olenler["FicouInternado"].isin(["Sim", "Não"])]
        for taban, grup in [("tum", olenler), ("bilinen", bilinenler)]:
            satir = {"grup": ad, "taban": taban, "kayit": len(grup),
                     "fiili_yatis_yuzde": 100 * grup["FiiliYatis"].mean()}
            for esik in ESIKLER:
                satir[f"model_yatis_yuzde_{esik:.2f}"] = 100 * (grup["SV"] >= esik).mean()
            satirlar.append(satir)
    return pd.DataFrame(satirlar)


def olum_grafigi(tablo, dosya):
    """Gruplanmış çubuk grafik: fiili yatış ve iki eşikteki model önerisi."""
    sutunlar = ["fiili_yatis_yuzde", "model_yatis_yuzde_0.75", "model_yatis_yuzde_0.50"]
    etiketler = ["Fiili yatış", "Model (SV ≥ 0,75)", "Model (SV ≥ 0,50)"]
    renkler = ["#7f7f7f", "#1f77b4", "#9ecae1"]
    genislik = 0.25

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for i, (sutun, etiket, renk) in enumerate(zip(sutunlar, etiketler, renkler)):
        x = [j + (i - 1) * genislik for j in range(len(tablo))]
        cubuklar = ax.bar(x, tablo[sutun], genislik, label=etiket, color=renk)
        ax.bar_label(cubuklar, fmt="%.1f", fontsize=9)
    ax.set_xticks(range(len(tablo)))
    ax.set_xticklabels([f"{g}\n(n = {n:,})".replace(",", ".")
                        for g, n in zip(tablo["grup"], tablo["kayit"])])
    ax.set_ylabel("Hastaneye yatırılan / önerilen (%)")
    ax.set_ylim(0, 100)
    ax.set_title("Ölen hastalarda fiili yatış ve model önerisi\n"
                 "(yatış bilgisi bilinen kayıtlar)", fontsize=11)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(dosya, dpi=150)
    plt.close(fig)


def sv_grafigi(dagilim, dosya):
    """SV değerlerine göre kayıt sayısı çubuk grafiği."""
    fig, ax = plt.subplots(figsize=(6, 4))
    etiketler = [f"{sv:.1f}".replace(".", ",") for sv in dagilim["SV"]]
    cubuklar = ax.bar(etiketler, dagilim["kayit"], color="#1f77b4", width=0.5)
    ax.bar_label(cubuklar, labels=[f"%{y:.1f}".replace(".", ",") for y in dagilim["yuzde"]])
    ax.set_xlabel("Durulaştırılmış şiddet (SV)")
    ax.set_ylabel("Kayıt sayısı (bin)")
    ax.yaxis.set_major_formatter(lambda y, _: f"{y / 1000:,.0f}".replace(",", "."))
    ax.set_title(f"SV dağılımı (n = {dagilim['kayit'].sum():,})".replace(",", "."), fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(dosya, dpi=150)
    plt.close(fig)


def main():
    if not VERI_YOLU.exists():
        print(f"{VERI_YOLU} bulunamadı. İndirme adımı: data/README.md")
        return
    SONUC_KLASORU.mkdir(exist_ok=True)
    df = hazirla(VERI_YOLU)
    print(f"Ön işleme sonrası kayıt: {len(df):,}")

    print("\n1) SV dağılımı")
    dagilim = sv_dagilimi(df)
    dagilim.to_csv(SONUC_KLASORU / "sv_dagilimi.csv", index=False)
    sv_grafigi(dagilim, SONUC_KLASORU / "sv_dagilimi.png")
    print(dagilim.to_string(index=False))

    print(f"\n2) Yatış önerilen kayıt oranı (kapsül, 0,75: %{100 * makale.KAPSUL_YATIS_ORANI:.1f})")
    oranlar = yatis_oranlari(df)
    oranlar.to_csv(SONUC_KLASORU / "yatis_oranlari.csv", index=False)
    print(oranlar.to_string(index=False))

    print("\n3) Ölüm vakaları")
    olum = olum_karsilastirma(df)
    olum.to_csv(SONUC_KLASORU / "olum_karsilastirma.csv", index=False)
    print(olum.to_string(index=False))
    print(f"   Makale: COVID ölümü {makale.COVID_OLUM:,}, diğer {makale.DIGER_OLUM:,}; "
          f"fiili yatış %{100 * makale.FIILI_YATIS_COVID_OLUM:.2f} / "
          f"%{100 * makale.FIILI_YATIS_DIGER_OLUM:.2f}")
    bilinen = olum[olum["taban"] == "bilinen"].reset_index(drop=True)
    covid = bilinen.iloc[0]
    print(f"   COVID ölümlerinde yatırılmayan (bilinen taban): "
          f"fiili %{100 - covid['fiili_yatis_yuzde']:.1f} "
          f"(makale %{100 * makale.YATIRILMAYAN_FIILI:.0f}), "
          f"model 0,75 %{100 - covid['model_yatis_yuzde_0.75']:.1f} "
          f"(makale %{100 * makale.YATIRILMAYAN_MODEL:.0f})")

    olum_grafigi(bilinen, SONUC_KLASORU / "olum_karsilastirma.png")
    print("\nKaydedildi: sonuclar/ altındaki csv ve png dosyaları")


if __name__ == "__main__":
    main()
