# =========================================================
# FAILAS: draustiniu_procentine_analize.py
# PASKIRTIS:
# Apskaičiuoti, kokia kiekvieno sklypo dalis (%) patenka
# į draustinių sluoksnį.
# =========================================================

import geopandas as gpd
from pathlib import Path


# ---------------------------------------------------------
# 1. Failų keliai
# ---------------------------------------------------------

# Sklypų sluoksnis
sklypu_failas = r"01_duomenys/sklypai/klaipedos_raj_ribos_2019.shp"

# Iškirptas draustinių sluoksnis pagal TPDR ribą
draustiniu_failas = r"02_projektas/papildomi/draustiniai_tpdr.gpkg"

# Kur saugosime rezultatą
isvedimo_failas = r"06_rezultatai/draustiniu_proc.csv"


# ---------------------------------------------------------
# 2. Įkeliame duomenis
# ---------------------------------------------------------

print("Įkeliami sluoksniai...")

sklypai = gpd.read_file(sklypu_failas)
draustiniai = gpd.read_file(draustiniu_failas)

print(f"Sklypų kiekis: {len(sklypai)}")
print(f"Draustinių objektų kiekis: {len(draustiniai)}")


# ---------------------------------------------------------
# 3. Patikriname koordinačių sistemą
# ---------------------------------------------------------

print(f"Sklypų CRS: {sklypai.crs}")
print(f"Draustinių CRS: {draustiniai.crs}")

if sklypai.crs != draustiniai.crs:
    print("CRS nesutampa, perprojektuojame draustinius...")
    draustiniai = draustiniai.to_crs(sklypai.crs)


# ---------------------------------------------------------
# 4. Patikriname, ar yra reikalingas ID stulpelis
# ---------------------------------------------------------

if "SKLYPO_ID" not in sklypai.columns:
    raise ValueError("Sklypų sluoksnyje nerastas stulpelis 'SKLYPO_ID'.")

# Pasiliekame tik reikalingus stulpelius
sklypai = sklypai[["SKLYPO_ID", "geometry"]].copy()

# Pašaliname eilutes, kur nėra sklypo identifikatoriaus
sklypai = sklypai.dropna(subset=["SKLYPO_ID"]).copy()

print(f"Sklypų kiekis po tuščių SKLYPO_ID pašalinimo: {len(sklypai)}")

# Apskaičiuojame sklypo plotą
sklypai["sklypo_plotas"] = sklypai.geometry.area


# ---------------------------------------------------------
# 5. Apskaičiuojame susikirtimus
# ---------------------------------------------------------

print("Skaičiuojami susikirtimai tarp sklypų ir draustinių...")

susikirtimai = gpd.overlay(sklypai, draustiniai, how="intersection")

print(f"Susikirtimų kiekis: {len(susikirtimai)}")


# ---------------------------------------------------------
# 6. Jei susikirtimų nėra - procentas bus 0
# ---------------------------------------------------------

if len(susikirtimai) == 0:
    rezultatas = sklypai[["SKLYPO_ID"]].copy()
    rezultatas["draustiniu_proc"] = 0.0
else:
    # Apskaičiuojame susikirtimo plotą
    susikirtimai["susikirtimo_plotas"] = susikirtimai.geometry.area

    # Susumuojame pagal sklypą
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

    # Kur nebuvo persidengimo - įrašome 0
    rezultatas["susikirtimo_plotas"] = rezultatas["susikirtimo_plotas"].fillna(0)

    # Skaičiuojame procentą
    rezultatas["draustiniu_proc"] = (
        rezultatas["susikirtimo_plotas"] / rezultatas["sklypo_plotas"] * 100
    ).round(2)

    # Pasiliekame tik reikalingus stulpelius
    rezultatas = rezultatas[["SKLYPO_ID", "draustiniu_proc"]].copy()


# ---------------------------------------------------------
# 7. Išsaugome CSV
# ---------------------------------------------------------

Path(isvedimo_failas).parent.mkdir(parents=True, exist_ok=True)
rezultatas.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

print("\nRezultatas išsaugotas:")
print(isvedimo_failas)

print("\nPirmos 10 eilučių:")
print(rezultatas.head(10))