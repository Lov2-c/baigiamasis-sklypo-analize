# =========================================================
# FAILAS: saugomu_sluoksniu_procentine_analize.py
# PASKIRTIS:
# Apskaičiuoti, kokia kiekvieno sklypo dalis (%) patenka
# į pasirinktus saugomų teritorijų sluoksnius.
# =========================================================

import geopandas as gpd
from pathlib import Path


def apskaiciuoti_procentus(sklypu_failas, sluoksnio_failas, isvedimo_failas, procento_stulpelis):
    """
    Apskaičiuoja, kokia kiekvieno sklypo dalis (%) patenka į pasirinktą sluoksnį.

    Parametrai:
    - sklypu_failas: kelias iki sklypų sluoksnio
    - sluoksnio_failas: kelias iki analizuojamo sluoksnio
    - isvedimo_failas: kur išsaugoti CSV rezultatą
    - procento_stulpelis: naujo stulpelio pavadinimas, pvz. draustiniu_proc
    """

    print("\n" + "=" * 60)
    print(f"Pradedama analizė: {procento_stulpelis}")
    print("=" * 60)

    # 1. Įkeliame duomenis
    sklypai = gpd.read_file(sklypu_failas)
    sluoksnis = gpd.read_file(sluoksnio_failas)

    print(f"Sklypų kiekis prieš filtravimą: {len(sklypai)}")
    print(f"Sluoksnio objektų kiekis: {len(sluoksnis)}")

    # 2. CRS patikra
    print(f"Sklypų CRS: {sklypai.crs}")
    print(f"Sluoksnio CRS: {sluoksnis.crs}")

    if sklypai.crs != sluoksnis.crs:
        print("CRS nesutampa, perprojektuojama...")
        sluoksnis = sluoksnis.to_crs(sklypai.crs)

    # 3. Tikriname, ar yra sklypo ID
    if "SKLYPO_ID" not in sklypai.columns:
        raise ValueError("Sklypų sluoksnyje nerastas stulpelis 'SKLYPO_ID'.")

    # 4. Pasiliekame tik reikalingus stulpelius
    sklypai = sklypai[["SKLYPO_ID", "geometry"]].copy()

    # Pašaliname eilutes, kur nėra sklypo identifikatoriaus
    sklypai = sklypai.dropna(subset=["SKLYPO_ID"]).copy()

    print(f"Sklypų kiekis po tuščių SKLYPO_ID pašalinimo: {len(sklypai)}")

    # 5. Sklypų plotai
    sklypai["sklypo_plotas"] = sklypai.geometry.area

    # 6. Susikirtimai
    print("Skaičiuojami susikirtimai...")
    susikirtimai = gpd.overlay(sklypai, sluoksnis, how="intersection")

    print(f"Susikirtimų kiekis: {len(susikirtimai)}")

    # 7. Jei susikirtimų nėra
    if len(susikirtimai) == 0:
        rezultatas = sklypai[["SKLYPO_ID"]].copy()
        rezultatas[procento_stulpelis] = 0.0

    else:
        # Susikirtimo plotas
        susikirtimai["susikirtimo_plotas"] = susikirtimai.geometry.area

        # Sumuojame plotus pagal sklypą
        susikirtimu_suma = (
            susikirtimai.groupby("SKLYPO_ID")["susikirtimo_plotas"]
            .sum()
            .reset_index()
        )

        # Prijungiame prie visų sklypų
        rezultatas = sklypai[["SKLYPO_ID", "sklypo_plotas"]].merge(
            susikirtimu_suma,
            on="SKLYPO_ID",
            how="left"
        )

        # Kur nėra persidengimo - įrašome 0
        rezultatas["susikirtimo_plotas"] = rezultatas["susikirtimo_plotas"].fillna(0)

        # Skaičiuojame procentą
        rezultatas[procento_stulpelis] = (
            rezultatas["susikirtimo_plotas"] / rezultatas["sklypo_plotas"] * 100
        ).round(2)

        # Pasiliekame tik reikalingus stulpelius
        rezultatas = rezultatas[["SKLYPO_ID", procento_stulpelis]].copy()

    # 8. Išsaugome rezultatą
    Path(isvedimo_failas).parent.mkdir(parents=True, exist_ok=True)
    rezultatas.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

    print(f"Rezultatas išsaugotas: {isvedimo_failas}")
    print("Pirmos 5 eilutės:")
    print(rezultatas.head())


if __name__ == "__main__":
    # Sklypų sluoksnis
    sklypu_failas = r"01_duomenys/sklypai/klaipedos_raj_ribos_2019.gpkg"

    # Visi analizuojami sluoksniai:
    sluoksniai = [
        {
            "failas": r"02_projektas/papildomi/draustiniai_tpdr.gpkg",
            "csv": r"06_rezultatai/draustiniu_proc.csv",
            "stulpelis": "draustiniu_proc"
        },
        {
            "failas": r"02_projektas/papildomi/rezervatai_tpdr.gpkg",
            "csv": r"06_rezultatai/rezervatu_proc.csv",
            "stulpelis": "rezervatu_proc"
        },
        {
            "failas": r"02_projektas/papildomi/parkai_tpdr.gpkg",
            "csv": r"06_rezultatai/parku_proc.csv",
            "stulpelis": "parku_proc"
        },
        {
            "failas": r"02_projektas/papildomi/biosferos_poligonai_tpdr.gpkg",
            "csv": r"06_rezultatai/biosferos_poligonu_proc.csv",
            "stulpelis": "biosferos_poligonu_proc"
        },
        {
            "failas": r"02_projektas/papildomi/bast_tpdr.gpkg",
            "csv": r"06_rezultatai/bast_proc.csv",
            "stulpelis": "bast_proc"
        },
        {
            "failas": r"02_projektas/papildomi/past_tpdr.gpkg",
            "csv": r"06_rezultatai/past_proc.csv",
            "stulpelis": "past_proc"
        },
        {
            "failas": r"02_projektas/papildomi/pajurio_juosta_tpdr.gpkg",
            "csv": r"06_rezultatai/pajurio_juostos_proc.csv",
            "stulpelis": "pajurio_juostos_proc"
        },
        {
            "failas": r"02_projektas/papildomi/buferines_apsaugos_zonos_tpdr.gpkg",
            "csv": r"06_rezultatai/buferiniu_apsaugos_zonu_proc.csv",
            "stulpelis": "buferiniu_apsaugos_zonu_proc"
        }
    ]

    # Paleidžiame analizę kiekvienam sluoksniui
    for sluoksnis in sluoksniai:
        apskaiciuoti_procentus(
            sklypu_failas=sklypu_failas,
            sluoksnio_failas=sluoksnis["failas"],
            isvedimo_failas=sluoksnis["csv"],
            procento_stulpelis=sluoksnis["stulpelis"]
        )

    print("\nVisų sluoksnių analizė baigta.")