"""Gerçek veride yatış eşiğinin etkisi.

Gerçek veride SV yalnız 0,1 / 0,5 / 0,9 değerlerini alıyor. Bu yüzden eşik
0'dan 1'e kaydırılınca karar yalnız üç noktada değişir. Her eşik için:
    - bütün kayıtların yüzde kaçına yatış öneriliyor
    - COVID-19 ölümlerinin yüzde kaçına öneriliyor (yakalanan ölüm)
    - iyileşenlerin (Cura) yüzde kaçına öneriliyor (gereksiz yatış göstergesi)

Çalıştırma:  python -m analiz.esik_analizi
Çıktılar:    sonuclar/esik_analizi.csv, sonuclar/esik_analizi.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.veri import hazirla

VERI_YOLU = Path("data/MICRODADOS.csv")
SONUC_KLASORU = Path("sonuclar")
ESIKLER = np.round(np.arange(0.0, 1.0001, 0.05), 2)          # tablo için
INCE_ESIKLER = np.round(np.arange(0.0, 1.0001, 0.001), 3)   # grafik için


def esik_tablosu(df, esikler):
    """Her eşik için öneri oranlarını hesaplar."""
    covid_olum = df[(df["Evolucao"] == "Óbito pelo COVID-19")
                    & df["FicouInternado"].isin(["Sim", "Não"])]
    iyilesen = df[df["Evolucao"] == "Cura"]
    satirlar = []
    for esik in esikler:
        satirlar.append({
            "esik": esik,
            "tum_kayit_yuzde": 100 * (df["SV"] >= esik).mean(),
            "covid_olum_yuzde": 100 * (covid_olum["SV"] >= esik).mean(),
            "iyilesen_yuzde": 100 * (iyilesen["SV"] >= esik).mean(),
            "yatis_onerilen": int((df["SV"] >= esik).sum()),
            "yakalanan_covid_olum": int((covid_olum["SV"] >= esik).sum()),
        })
    tablo = pd.DataFrame(satirlar)
    # Yakalanan her COVID ölümü başına kaç kayda yatış öneriliyor
    tablo["oneri_basina_olum"] = (tablo["yatis_onerilen"]
                                  / tablo["yakalanan_covid_olum"].replace(0, np.nan)).round(1)
    return tablo, len(covid_olum), len(iyilesen)


def esik_grafigi(tablo, fiili_covid_yatis):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.step(tablo["esik"], tablo["covid_olum_yuzde"], where="post",
            label="COVID-19 ölümlerine öneri", color="#d62728")
    ax.step(tablo["esik"], tablo["tum_kayit_yuzde"], where="post",
            label="Bütün kayıtlara öneri", color="#1f77b4")
    ax.step(tablo["esik"], tablo["iyilesen_yuzde"], where="post",
            label="İyileşenlere öneri", color="#2ca02c", linestyle="--")
    ax.axhline(fiili_covid_yatis, color="#d62728", linestyle=":", linewidth=1,
               label=f"COVID-19 ölümlerinde fiili yatış (%{fiili_covid_yatis:.1f})")
    for x, ad in [(0.1, "SV = 0,1"), (0.5, "SV = 0,5"), (0.9, "SV = 0,9")]:
        ax.axvline(x, color="gray", linewidth=0.6)
        ax.text(x, 106, ad, ha="center", fontsize=8, color="gray")
    ax.axvline(0.75, color="black", linestyle="--", linewidth=0.8)
    ax.text(0.75, 3, " makale eşiği 0,75", fontsize=8)
    ax.set_xlabel("Yatış eşiği (SV ≥ eşik)")
    ax.set_ylabel("Yatış önerilen (%)")
    ax.set_ylim(0, 105)
    ax.set_title("Eşik analizi (gerçek veri)", fontsize=11, pad=18)
    ax.set_xlim(0, 1)
    ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(SONUC_KLASORU / "esik_analizi.png", dpi=150)
    plt.close(fig)


def main():
    if not VERI_YOLU.exists():
        print(f"{VERI_YOLU} bulunamadı. İndirme adımı: data/README.md")
        return
    df = hazirla(VERI_YOLU)
    # Kayan nokta hatası (0,0999989 / 0,900001) eşik karşılaştırmasını
    # bozmasın diye SV 4 haneye yuvarlanır: 0,1 / 0,5 / 0,9
    df["SV"] = df["SV"].round(4)
    tablo, n_olum, n_iyilesen = esik_tablosu(df, ESIKLER)
    tablo.to_csv(SONUC_KLASORU / "esik_analizi.csv", index=False)
    print(f"COVID-19 ölümü (yatış bilgisi bilinen): {n_olum:,}  İyileşen: {n_iyilesen:,}\n")
    print(tablo.round(2).to_string(index=False))

    print("\nFarklı karar veren eşik aralıkları (yalnız bunlar anlamlı):")
    farkli = tablo.drop_duplicates(subset=["yatis_onerilen"])
    print(farkli[["esik", "tum_kayit_yuzde", "covid_olum_yuzde", "iyilesen_yuzde",
                  "oneri_basina_olum"]].round(2).to_string(index=False))

    covid = df[(df["Evolucao"] == "Óbito pelo COVID-19")
               & df["FicouInternado"].isin(["Sim", "Não"])]
    ince_tablo, _, _ = esik_tablosu(df, INCE_ESIKLER)
    esik_grafigi(ince_tablo, 100 * covid["FiiliYatis"].mean())
    print("\nKaydedildi: sonuclar/esik_analizi.csv, esik_analizi.png")


if __name__ == "__main__":
    main()
