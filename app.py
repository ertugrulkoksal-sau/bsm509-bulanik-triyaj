"""Canlı demo: Galo vd. (2022) bulanık triyaj modeli.

Çalıştırma (proje klasöründen):  streamlit run app.py

Sayfa, motorun her adımını gösterir:
    1. bulanıklaştırma  -> dört girdinin üyelik grafikleri ve dereceleri
    2. kural ateşleme   -> ateşlenen kurallar ve güçleri (VE = min)
    3-4. kırpma ve birleştirme -> çıktı grafiği
    5. durulaştırma     -> ağırlık merkezi (SV) ve yatış kararı
"""

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from src.makale_degerleri import TABLO5
from src.mamdani import cikarim, kirp
from src.model import CIKTI, CIKTI_EVRENI, GIRDI_SIRASI, GIRDILER, KURALLAR
from src.uyelik import uyelik_hesapla

# Kaydırıcı ayarları: (Türkçe ad, adım)
KAYDIRICI = {
    "VS": ("VS: yaşamsal bulgular (NEWS puanı, 0-18)", 0.1),
    "BD": ("BD: nefes darlığı (0-1)", 0.01),
    "RF": ("RF: risk faktörleri (0-1)", 0.01),
    "RS": ("RS: diğer belirtiler (0-1)", 0.01),
}
TERIM_RENKLERI = ["#1f77b4", "#ff7f0e", "#2ca02c"]
CIKTI_RENKLERI = {"mild": "#2ca02c", "moderate": "#ff7f0e", "severe": "#d62728"}
TURKCE_TERIM = {
    "low": "düşük", "medium": "orta", "high": "yüksek", "minimal": "minimal/yok",
    "veryhigh": "çok yüksek", "meaningful": "anlamlı",
    "mild": "hafif", "moderate": "orta", "severe": "ağır",
}
# Makaledeki değeri kural tablosuyla çelişen vakalar (bulgular.md, B2)
CELISKILI_VAKALAR = {5, 13, 15}


def virgul(sayi, basamak):
    """Sayıyı Türkçe ondalık virgülle yazar: 0.873 -> '0,873'."""
    return f"{sayi:.{basamak}f}".replace(".", ",")


# ---------- Durum: kaydırıcı değerleri ----------

def baslangic_degerleri():
    """İlk açılışta kaydırıcıları Tablo 5'in 1. vakasına ayarlar."""
    if "VS" not in st.session_state:
        vaka_yukle(TABLO5[0])


def vaka_yukle(vaka):
    """Bir Tablo 5 vakasını kaydırıcılara yazar (buton geri çağrısı)."""
    no, vs, bd, rf, rs, _, _ = vaka
    st.session_state["VS"] = float(vs)
    st.session_state["BD"] = float(bd)
    st.session_state["RF"] = float(rf)
    st.session_state["RS"] = float(rs)
    st.session_state["secili_vaka"] = no


def vaka_secimini_temizle():
    """Kaydırıcı elle değişince seçili vaka bilgisini kaldırır."""
    st.session_state["secili_vaka"] = None


# ---------- Grafikler ----------

def uyelik_grafigi(degisken, x, dereceler):
    """Bir girdinin ÜF'lerini, girdi çizgisini ve dereceleri çizer."""
    alt, ust = GIRDILER[degisken]["evren"]
    evren = np.linspace(alt, ust, 721)
    fig, ax = plt.subplots(figsize=(6, 2.6))
    terimler = GIRDILER[degisken]["terimler"].items()
    for renk, (terim, (tip, parametreler)) in zip(TERIM_RENKLERI, terimler):
        derece = dereceler[terim]
        ax.plot(evren, uyelik_hesapla(evren, tip, parametreler), color=renk,
                label=f"{TURKCE_TERIM[terim]}: {virgul(derece, 2)}")
        if derece > 0:
            ax.plot([alt, x], [derece, derece], color=renk, linestyle=":", linewidth=1)
    ax.axvline(x, color="black", linewidth=1.5)
    ax.set_ylim(-0.03, 1.1)
    ax.set_title(f"{degisken} = {x:g}".replace(".", ","), fontsize=10)
    ax.legend(fontsize=7, loc="center right", frameon=False)
    ax.tick_params(labelsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def cikti_grafigi(sonuc, esik):
    """Çıktı kümeleri, kırpılmış kümeler, birleşik küme ve ağırlık merkezi."""
    fig, ax = plt.subplots(figsize=(8, 3.2))
    # Kırpılmamış çıktı kümeleri (kesikli)
    for terim, (tip, parametreler) in CIKTI["terimler"].items():
        ax.plot(CIKTI_EVRENI, uyelik_hesapla(CIKTI_EVRENI, tip, parametreler),
                color=CIKTI_RENKLERI[terim], linestyle="--", linewidth=1,
                label=TURKCE_TERIM[terim])
    # Her ateşlenen kuralın kırpılmış kümesi (yalnız 0'dan büyük kısmı çizilir)
    for kural, guc in zip(KURALLAR, sonuc["kural_gucleri"]):
        if guc > 0:
            kume = kirp(kural[4], guc)
            ax.plot(CIKTI_EVRENI, np.where(kume > 0, kume, np.nan),
                    color=CIKTI_RENKLERI[kural[4]], linewidth=1.5)
    # Birleşik küme (max) ve ağırlık merkezi
    ax.fill_between(CIKTI_EVRENI, sonuc["birlesik"], color="#9467bd", alpha=0.35,
                    label="birleşik küme (max)")
    if not math.isnan(sonuc["sv"]):
        ax.axvline(sonuc["sv"], color="black", linewidth=2,
                   label=f"ağırlık merkezi = {virgul(sonuc['sv'], 3)}")
    ax.axvline(esik, color="#7f7f7f", linestyle=":", label=f"eşik = {virgul(esik, 2)}")
    ax.set_xlabel("SV (şiddet)")
    ax.set_ylabel("üyelik")
    ax.set_ylim(-0.03, 1.1)
    ax.legend(fontsize=8, loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


# ---------- Tablolar ----------

def kural_metni(kural):
    vs, bd, rf, rs, sv = kural
    return (f"EĞER VS={TURKCE_TERIM[vs]} VE BD={TURKCE_TERIM[bd]} VE "
            f"RF={TURKCE_TERIM[rf]} VE RS={TURKCE_TERIM[rs]} İSE SV={TURKCE_TERIM[sv]}")


def ateslenen_kurallar_tablosu(sonuc):
    """Gücü 0'dan büyük kurallar: numara, metin, dört koşul derecesi, güç."""
    satirlar = []
    for i, (kural, guc) in enumerate(zip(KURALLAR, sonuc["kural_gucleri"])):
        if guc == 0:
            continue
        satir = {"kural": i + 1, "kural metni": kural_metni(kural)}
        for degisken, terim in zip(GIRDI_SIRASI, kural[:4]):
            satir[degisken] = round(sonuc["dereceler"][degisken][terim], 3)
        satir["güç (min)"] = round(guc, 3)
        satirlar.append(satir)
    return pd.DataFrame(satirlar)


# ---------- Sayfa ----------

def kenar_cubugu():
    """Eşik seçimi ve Tablo 5 vakaları."""
    st.sidebar.header("Yatış eşiği")
    esik = st.sidebar.radio("SV ≥ eşik ise yatış önerilir", [0.75, 0.50],
                            format_func=lambda e: virgul(e, 2))
    st.sidebar.header("Makale Tablo 5 vakaları")
    st.sidebar.caption("Vaka numarasına basınca kaydırıcılar o vakanın girdilerine ayarlanır.")
    sutunlar = st.sidebar.columns(3)
    for i, vaka in enumerate(TABLO5):
        no, vs, bd, rf, rs, _, _ = vaka
        isaret = " ⚠" if no in CELISKILI_VAKALAR else ""
        sutunlar[i % 3].button(f"{no}{isaret}", key=f"vaka{no}",
                               on_click=vaka_yukle, args=(vaka,),
                               help=f"VS={vs}, BD={bd}, RF={rf}, RS={rs}",
                               width="stretch")
    st.sidebar.caption("⚠ Makaledeki sonucu kural tablosuyla çelişen vaka (bulgu B2).")
    return esik


def girdi_kaydiricilari():
    sutunlar = st.columns(4)
    for sutun, degisken in zip(sutunlar, GIRDI_SIRASI):
        etiket, adim = KAYDIRICI[degisken]
        alt, ust = GIRDILER[degisken]["evren"]
        sutun.slider(etiket, float(alt), float(ust), step=adim, key=degisken,
                     on_change=vaka_secimini_temizle)
    return {d: st.session_state[d] for d in GIRDI_SIRASI}


def sonuc_ozeti(sonuc, esik):
    sv = sonuc["sv"]
    sutunlar = st.columns(3)
    if math.isnan(sv):
        sutunlar[0].metric("Şiddet (SV)", "tanımsız")
        sutunlar[1].metric("Karar", "—")
        st.error("Hiçbir kural ateşlenmedi: birleşik küme boş, ağırlık merkezi 0/0. "
                 "BD = 0,25 ve 0,75'te BD'nin üç teriminin üyeliği de 0 (bulgu B5).")
    else:
        sutunlar[0].metric("Şiddet (SV)", virgul(sv, 3))
        karar = "Yatış önerilir" if sv >= esik else "Ayaktan izlem"
        sutunlar[1].metric(f"Karar (eşik {virgul(esik, 2)})", karar)
    ateslenen = sum(g > 0 for g in sonuc["kural_gucleri"])
    sutunlar[2].metric("Ateşlenen kural", f"{ateslenen} / {len(KURALLAR)}")


def makale_karsilastirmasi(sonuc):
    """Seçili bir Tablo 5 vakası varsa makaledeki değerle yan yana gösterir."""
    no = st.session_state.get("secili_vaka")
    if no is None:
        return
    vaka = next(v for v in TABLO5 if v[0] == no)
    _, _, _, _, _, makale_terim, makale_sv = vaka
    metin = (f"**Vaka {no}**: makalede {TURKCE_TERIM[makale_terim]} "
             f"({virgul(makale_sv, 3)}), bizim motor {virgul(sonuc['sv'], 3)}.")
    if no in CELISKILI_VAKALAR:
        st.warning(metin + " Makaledeki terim, Tablo 3'teki kural tabanıyla çelişiyor (B2).")
    else:
        st.info(metin + " Terim aynı. Sayısal fark, makalede farklı çıktı ÜF "
                "parametreleri kullanılmış olmasından kaynaklanıyor olabilir (B1).")


def main():
    st.set_page_config(page_title="Bulanık COVID-19 triyajı", layout="wide")
    baslangic_degerleri()
    esik = kenar_cubugu()

    st.title("Bulanık COVID-19 triyaj modeli")
    st.caption("Galo, Roriz Junior, Pereira (2022), Applied Soft Computing 129, 109626. "
               "Mamdani çıkarımı: VE = min, kırpma = min, birleştirme = max, "
               "durulaştırma = ağırlık merkezi.")

    girdiler = girdi_kaydiricilari()
    sonuc = cikarim(girdiler["VS"], girdiler["BD"], girdiler["RF"], girdiler["RS"])

    sonuc_ozeti(sonuc, esik)
    makale_karsilastirmasi(sonuc)

    st.subheader("1. Bulanıklaştırma: üyelik dereceleri")
    # 2 x 2 düzen: projeksiyonda okunabilsin diye grafikler büyük
    sutunlar = st.columns(2) + st.columns(2)
    for sutun, degisken in zip(sutunlar, GIRDI_SIRASI):
        fig = uyelik_grafigi(degisken, girdiler[degisken], sonuc["dereceler"][degisken])
        sutun.pyplot(fig)
        plt.close(fig)

    st.subheader("2. Ateşlenen kurallar (güç = dört koşulun en küçüğü)")
    tablo = ateslenen_kurallar_tablosu(sonuc)
    if tablo.empty:
        st.write("Ateşlenen kural yok.")
    else:
        st.dataframe(tablo, hide_index=True, width="stretch")

    st.subheader("3-5. Kırpma, birleştirme ve durulaştırma")
    fig = cikti_grafigi(sonuc, esik)
    st.pyplot(fig)
    plt.close(fig)


main()
