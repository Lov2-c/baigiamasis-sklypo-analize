# =========================================================
# FAILAS: modelio_duomenu_paruosimas_10000.py
# PASKIRTIS:
# Paruošti 10000 sklypų modelio duomenų failą,
# kur target reiškia ne gyvenamojo namo statybą, o
# bendrą teritorijos vystymo / užstatymo palankumą.
#
# TARGET KLASĖS:
# - vystymas_tiesiogiai_galimas
# - vystymas_galimas_su_salygomis
# - vystymas_labai_apribotas
# =========================================================

import pandas as pd


def ar_reiksme_reiksminga(reiksme) -> bool:
    """
    Patikrina, ar procentinė / skaitinė reikšmė laikytina reikšminga.
    """
    if pd.isna(reiksme):
        return False
    return float(reiksme) > 0


def gauti_reiksmingu_ribojimu_kieki(eilute: pd.Series) -> int:
    """
    Suskaičiuoja, kiek reikšmingų ribojimų turi sklypas.
    """
    ribojimu_laukai = [
        "draustiniu_proc",
        "rezervatu_proc",
        "parku_proc",
        "biosferos_poligonu_proc",
        "bast_proc",
        "past_proc",
        "pajurio_juostos_proc",
        "buferiniu_apsaugos_zonu_proc",
        "misko_proc",
        "kvr_poligonu_proc",
        "kvr_apsaugos_zonu_proc",
        "pelkiu_proc",
        "saltinynu_proc",
        "pievu_ganyklu_proc",
        "drenazo_plotu_proc",
        "rinktuvu_apsaugos_zonu_proc",
        "gelezinkelio_ribojimo_zonos_proc",
    ]

    kiekis = 0

    for laukas in ribojimu_laukai:
        if laukas in eilute.index and ar_reiksme_reiksminga(eilute[laukas]):
            kiekis += 1

    return kiekis


def ar_yra_stiprus_ribojimas(eilute: pd.Series) -> bool:
    """
    Patikrina, ar sklype yra bent vienas stiprus ribojimas,
    kuris reikšmingai apsunkina vystymą.
    """
    stiprus_laukai = [
        "rezervatu_proc",
        "draustiniu_proc",
        "pajurio_juostos_proc",
        "gelezinkelio_ribojimo_zonos_proc",
        "kvr_poligonu_proc",
        "kvr_apsaugos_zonu_proc",
    ]

    for laukas in stiprus_laukai:
        if laukas in eilute.index and ar_reiksme_reiksminga(eilute[laukas]):
            return True

    return False


def suformuoti_vystymo_target(eilute: pd.Series) -> str:
    """
    Suformuoja Variant B target:
    - vystymas_tiesiogiai_galimas
    - vystymas_galimas_su_salygomis
    - vystymas_labai_apribotas
    """

    zonos_kodas = str(eilute.get("PAGRINDINE_ZONOS_KODAS", "")).strip()
    ribojimu_kiekis = gauti_reiksmingu_ribojimu_kieki(eilute)
    stiprus_ribojimas = ar_yra_stiprus_ribojimas(eilute)

    # -----------------------------------------------------
    # 1. Labai apriboti atvejai
    # -----------------------------------------------------
    # Jei yra rezervatas arba keli stiprūs ribojimai vienu metu,
    # vystymas laikomas labai apribotu.
    if ar_reiksme_reiksminga(eilute.get("rezervatu_proc", 0)):
        return "vystymas_labai_apribotas"

    if ar_reiksme_reiksminga(eilute.get("pajurio_juostos_proc", 0)) and ar_reiksme_reiksminga(eilute.get("draustiniu_proc", 0)):
        return "vystymas_labai_apribotas"

    if stiprus_ribojimas and ribojimu_kiekis >= 3:
        return "vystymas_labai_apribotas"

    # -----------------------------------------------------
    # 2. Zonos, kur vystymas iš principo galimas tiesiogiai
    # -----------------------------------------------------
    gyvenamosios_zonos = {"U_GG_E_F", "U_GG_M_F", "U_GG_V_F", "U_GG_I_F"}
    pramones_zonos = {"U_PS_F"}
    specializuotos_zonos = {"U_SK_F"}

    if zonos_kodas in gyvenamosios_zonos:
        if ribojimu_kiekis == 0:
            return "vystymas_tiesiogiai_galimas"
        return "vystymas_galimas_su_salygomis"

    if zonos_kodas in pramones_zonos:
        if not stiprus_ribojimas and ribojimu_kiekis <= 1:
            return "vystymas_tiesiogiai_galimas"
        return "vystymas_galimas_su_salygomis"

    if zonos_kodas in specializuotos_zonos:
        if not stiprus_ribojimas and ribojimu_kiekis <= 1:
            return "vystymas_tiesiogiai_galimas"
        return "vystymas_galimas_su_salygomis"

    # -----------------------------------------------------
    # 3. Zonos, kur vystymas galimas, bet dažniausiai su sąlygomis
    # -----------------------------------------------------
    zemes_ukio_zonos = {"ZU_F"}
    misku_zonos = {"MI_F"}
    vandenu_zonos = {"H_F"}
    zeldynu_zonos = {"U_BZ_F"}

    if zonos_kodas in zemes_ukio_zonos:
        return "vystymas_galimas_su_salygomis"

    if zonos_kodas in misku_zonos:
        if stiprus_ribojimas or ribojimu_kiekis >= 2:
            return "vystymas_labai_apribotas"
        return "vystymas_galimas_su_salygomis"

    if zonos_kodas in vandenu_zonos:
        return "vystymas_labai_apribotas"

    if zonos_kodas in zeldynu_zonos:
        return "vystymas_labai_apribotas"

    # -----------------------------------------------------
    # 4. Atsarginė logika nežinomoms zonoms
    # -----------------------------------------------------
    if stiprus_ribojimas:
        return "vystymas_galimas_su_salygomis"

    return "vystymas_galimas_su_salygomis"


if __name__ == "__main__":
    ivesties_failas = "06_rezultatai/mini_dataset_bp_10000_pilnas.csv"
    isvesties_failas = "06_rezultatai/modelio_duomenys_10000.csv"

    df = pd.read_csv(ivesties_failas, encoding="utf-8-sig")

    print("Nuskaitytas pradinis 10000 sklypų dataset.")
    print(f"Eilučių skaičius: {len(df)}")
    print(f"Stulpelių skaičius: {len(df.columns)}")
    print()

    # -----------------------------------------------------
    # 1. Užpildome trūkstamus procentinius laukus nuliais
    # -----------------------------------------------------
    procentiniai_laukai = [
        "PAGRINDINE_ZONOS_PROC",
        "ANTRA_ZONOS_PROC",
        "draustiniu_proc",
        "rezervatu_proc",
        "parku_proc",
        "biosferos_poligonu_proc",
        "bast_proc",
        "past_proc",
        "pajurio_juostos_proc",
        "buferiniu_apsaugos_zonu_proc",
        "misko_proc",
        "kvr_poligonu_proc",
        "kvr_apsaugos_zonu_proc",
        "pelkiu_proc",
        "saltinynu_proc",
        "pievu_ganyklu_proc",
        "drenazo_plotu_proc",
        "rinktuvu_apsaugos_zonu_proc",
        "gelezinkelio_ribojimo_zonos_proc",
    ]

    for laukas in procentiniai_laukai:
        if laukas in df.columns:
            df[laukas] = df[laukas].fillna(0)

    # -----------------------------------------------------
    # 2. Sukuriame papildomus indikatorius pagal pagrindinę BP zoną
    # -----------------------------------------------------
    df["ar_gyvenamoji_zona"] = df["PAGRINDINE_ZONOS_KODAS"].isin(
        ["U_GG_E_F", "U_GG_M_F", "U_GG_V_F", "U_GG_I_F"]
    ).astype(int)

    df["ar_zemes_ukio_zona"] = (df["PAGRINDINE_ZONOS_KODAS"] == "ZU_F").astype(int)
    df["ar_misku_zona"] = (df["PAGRINDINE_ZONOS_KODAS"] == "MI_F").astype(int)
    df["ar_vandenu_zona"] = (df["PAGRINDINE_ZONOS_KODAS"] == "H_F").astype(int)
    df["ar_pramones_zona"] = (df["PAGRINDINE_ZONOS_KODAS"] == "U_PS_F").astype(int)
    df["ar_specializuota_zona"] = (df["PAGRINDINE_ZONOS_KODAS"] == "U_SK_F").astype(int)
    df["ar_zeldynu_zona"] = (df["PAGRINDINE_ZONOS_KODAS"] == "U_BZ_F").astype(int)

    # -----------------------------------------------------
    # 3. Suskaičiuojame ribojimų skaičių
    # -----------------------------------------------------
    df["reiksmingu_ribojimu_kiekis"] = df.apply(gauti_reiksmingu_ribojimu_kieki, axis=1)
    df["ar_yra_stiprus_ribojimas"] = df.apply(ar_yra_stiprus_ribojimas, axis=1).astype(int)

    # -----------------------------------------------------
    # 4. Formuojame target
    # -----------------------------------------------------
    df["vystymo_target"] = df.apply(suformuoti_vystymo_target, axis=1)

    print("Target suformuotas.")
    print()
    print("Target klasių pasiskirstymas:")
    print(df["vystymo_target"].value_counts())
    print()

    # -----------------------------------------------------
    # 5. Atrenkame modeliui reikalingus laukus
    # -----------------------------------------------------
    modelio_stulpeliai = [
        "SKLYPO_ID",
        "UNIKAL_ID",
        "PLOTAS_REG",
        "SKLYPO_PLOTAS_M2",

        "PAGRINDINE_ZONOS_KODAS",
        "PAGRINDINE_ZONOS_PROC",
        "ANTRA_ZONOS_KODAS",
        "ANTRA_ZONOS_PROC",

        "ar_gyvenamoji_zona",
        "ar_zemes_ukio_zona",
        "ar_misku_zona",
        "ar_vandenu_zona",
        "ar_pramones_zona",
        "ar_specializuota_zona",
        "ar_zeldynu_zona",

        "draustiniu_proc",
        "rezervatu_proc",
        "parku_proc",
        "biosferos_poligonu_proc",
        "bast_proc",
        "past_proc",
        "pajurio_juostos_proc",
        "buferiniu_apsaugos_zonu_proc",
        "misko_proc",
        "kvr_poligonu_proc",
        "kvr_apsaugos_zonu_proc",
        "pelkiu_proc",
        "saltinynu_proc",
        "pievu_ganyklu_proc",
        "drenazo_plotu_proc",
        "rinktuvu_apsaugos_zonu_proc",
        "gelezinkelio_ribojimo_zonos_proc",

        "reiksmingu_ribojimu_kiekis",
        "ar_yra_stiprus_ribojimas",

        "vystymo_target",
    ]

    modelio_df = df[modelio_stulpeliai].copy()

    print("Paruoštas modelio dataset.")
    print(f"Eilučių: {len(modelio_df)}")
    print(f"Stulpelių: {len(modelio_df.columns)}")
    print()
    print(modelio_df.head())

    # -----------------------------------------------------
    # 6. Išsaugome
    # -----------------------------------------------------
    modelio_df.to_csv(isvesties_failas, index=False, encoding="utf-8-sig")

    print()
    print("Modelio duomenys išsaugoti:")
    print(isvesties_failas)