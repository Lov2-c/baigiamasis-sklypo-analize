# =========================================================
# FAILAS: melioracijos_procentine_analize.py
# PASKIRTIS:
# Apskaičiuoti, kokia kiekvieno sklypo dalis (%) patenka
# į drenažo plotus ir preliminarias rinktuvų apsaugos zonas.
# =========================================================

import geopandas as gpd
from pathlib import Path


def apskaiciuoti_procentus(sklypu_failas, sluoksnio_failas, isvedimo_failas, procento_stulpelis):
    """
    Apskaičiuoja, kokia kiekvieno sklypo dalis (%) patenka į pasirinktą sluoksnį.
    """

    print("\n" + "=" * 60)
    print(f"Pradedama analizė: {procento_stulpelis}")
    print("=" * 60)

    sklypai = gpd.read_file(sklypu_failas)
    sluoksnis = gpd.read_file(sluoksnio_failas)

    print(f"Sklypų kiekis prieš filtravimą: {len(sklypai)}")
    print(f"Sluoksnio objektų kiekis: {len(sluoksnis)}")

    print(f"Sklypų CRS: {sklypai.crs}")
    print(f"Sluoksnio CRS: {sluoksnis.crs}")

    if sklypai.crs != sluoksnis.crs:
        print("CRS nesutampa, perprojektuojama...")
        sluoksnis = sluoksnis.to_crs(sklypai.crs)

    if "SKLYPO_ID" not in sklypai.columns:
        raise ValueError("Sklypų sluoksnyje nerastas stulpelis 'SKLYPO_ID'.")

    sklypai = sklypai[["SKLYPO_ID", "geometry"]].copy()
    sklypai = sklypai.dropna(subset=["SKLYPO_ID"]).copy()

    print(f"Sklypų kiekis po tuščių SKLYPO_ID pašalinimo: {len(sklypai)}")

    sklypai["sklypo_plotas"] = sklypai.geometry.area

    print("Skaičiuojami susikirtimai...")
    susikirtimai = gpd.overlay(sklypai, sluoksnis, how="intersection")

    print(f"Susikirtimų kiekis: {len(susikirtimai)}")

    if len(susikirtimai) == 0:
        rezultatas = sklypai[["SKLYPO_ID"]].copy()
        rezultatas[procento_stulpelis] = 0.0
    else:
        susikirtimai["susikirtimo_plotas"] = susikirtimai.geometry.area

        susikirtimu_suma = (
            susikirtimai.groupby("SKLYPO_ID")["susikirtimo_plotas"]
            .sum()
            .reset_index()
        )

        rezultatas = sklypai[["SKLYPO_ID", "sklypo_plotas"]].merge(
            susikirtimu_suma,
            on="SKLYPO_ID",
            how="left"
        )

        rezultatas["susikirtimo_plotas"] = rezultatas["susikirtimo_plotas"].fillna(0)

        rezultatas[procento_stulpelis] = (
            rezultatas["susikirtimo_plotas"] / rezultatas["sklypo_plotas"] * 100
        ).round(2)

        rezultatas = rezultatas[["SKLYPO_ID", procento_stulpelis]].copy()

    Path(isvedimo_failas).parent.mkdir(parents=True, exist_ok=True)
    rezultatas.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

    print(f"Rezultatas išsaugotas: {isvedimo_failas}")
    print("Pirmos 5 eilutės:")
    print(rezultatas.head())


if __name__ == "__main__":
    sklypu_failas = r"01_duomenys/sklypai/klaipedos_raj_ribos_2019.shp"

    sluoksniai = [
        {
            "failas": r"01_duomenys/papildomi/melioracija/dren_p.gpkg",
            "csv": r"06_rezultatai/drenazo_plotu_proc.csv",
            "stulpelis": "drenazo_plotu_proc"
        },
        {
            "failas": r"01_duomenys/papildomi/melioracija/rinkt_l_125plus_buffer_15m.gpkg",
            "csv": r"06_rezultatai/rinktuvu_apsaugos_zonu_proc.csv",
            "stulpelis": "rinktuvu_apsaugos_zonu_proc"
        }
    ]

    for sluoksnis in sluoksniai:
        apskaiciuoti_procentus(
            sklypu_failas=sklypu_failas,
            sluoksnio_failas=sluoksnis["failas"],
            isvedimo_failas=sluoksnis["csv"],
            procento_stulpelis=sluoksnis["stulpelis"]
        )

    print("\nMelioracijos sluoksnių analizė baigta.")