# =========================================================
# FAILAS: gelezinkelio_procentine_analize.py
# PASKIRTIS:
# Apskaičiuoti, kokia kiekvieno sklypo dalis (%) patenka
# į preliminarią geležinkelio ribojimo zoną.
# =========================================================

import geopandas as gpd
from pathlib import Path


# ---------------------------------------------------------
# 1. Failų keliai
# ---------------------------------------------------------

sklypu_failas = r"01_duomenys/sklypai/klaipedos_raj_ribos_2019.gpkg"
gelezinkelio_failas = r"01_duomenys/papildomi/grpk/gelezink_tpdr_buffer_45m.gpkg"
isvedimo_failas = r"06_rezultatai/gelezinkelio_ribojimo_zonos_proc.csv"


# ---------------------------------------------------------
# 2. Įkeliame duomenis
# ---------------------------------------------------------

print("Įkeliami sluoksniai...")

sklypai = gpd.read_file(sklypu_failas)
gelezinkelis = gpd.read_file(gelezinkelio_failas)

print(f"Sklypų kiekis: {len(sklypai)}")
print(f"Geležinkelio buferio objektų kiekis: {len(gelezinkelis)}")


# ---------------------------------------------------------
# 3. CRS patikra
# ---------------------------------------------------------

print(f"Sklypų CRS: {sklypai.crs}")
print(f"Geležinkelio buferio CRS: {gelezinkelis.crs}")

if sklypai.crs != gelezinkelis.crs:
    print("CRS nesutampa, perprojektuojame geležinkelio buferį...")
    gelezinkelis = gelezinkelis.to_crs(sklypai.crs)


# ---------------------------------------------------------
# 4. Pasiruošiame sklypus
# ---------------------------------------------------------

if "SKLYPO_ID" not in sklypai.columns:
    raise ValueError("Sklypų sluoksnyje nerastas stulpelis 'SKLYPO_ID'.")

sklypai = sklypai[["SKLYPO_ID", "geometry"]].copy()
sklypai = sklypai.dropna(subset=["SKLYPO_ID"]).copy()

print(f"Sklypų kiekis po tuščių SKLYPO_ID pašalinimo: {len(sklypai)}")

sklypai["sklypo_plotas"] = sklypai.geometry.area


# ---------------------------------------------------------
# 5. Susikirtimai
# ---------------------------------------------------------

print("Skaičiuojami susikirtimai tarp sklypų ir geležinkelio buferio...")

susikirtimai = gpd.overlay(sklypai, gelezinkelis, how="intersection")

print(f"Susikirtimų kiekis: {len(susikirtimai)}")


# ---------------------------------------------------------
# 6. Skaičiuojame procentą
# ---------------------------------------------------------

if len(susikirtimai) == 0:
    rezultatas = sklypai[["SKLYPO_ID"]].copy()
    rezultatas["gelezinkelio_ribojimo_zonos_proc"] = 0.0
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

    rezultatas["gelezinkelio_ribojimo_zonos_proc"] = (
        rezultatas["susikirtimo_plotas"] / rezultatas["sklypo_plotas"] * 100
    ).round(2)

    rezultatas = rezultatas[["SKLYPO_ID", "gelezinkelio_ribojimo_zonos_proc"]].copy()


# ---------------------------------------------------------
# 7. Išsaugome rezultatą
# ---------------------------------------------------------

Path(isvedimo_failas).parent.mkdir(parents=True, exist_ok=True)
rezultatas.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

print("\nRezultatas išsaugotas:")
print(isvedimo_failas)

print("\nPirmos 10 eilučių:")
print(rezultatas.head(10))