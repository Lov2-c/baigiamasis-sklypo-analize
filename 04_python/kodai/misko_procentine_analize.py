# =========================================================
# FAILAS: misko_procentine_analize.py
# PASKIRTIS:
# Apskaičiuoti, kokia kiekvieno sklypo dalis (%) patenka
# į miško sklypų sluoksnį.
# =========================================================

import geopandas as gpd
from pathlib import Path


# ---------------------------------------------------------
# 1. Failų keliai
# ---------------------------------------------------------

# Sklypų sluoksnis
sklypu_failas = r"01_duomenys/sklypai/klaipedos_raj_ribos_2019.shp"

# Miško sklypų sluoksnis
misko_failas = r"01_duomenys/papildomi/miskai/misko_sklypai.gpkg"

# Kur išsaugosime rezultatą
isvedimo_failas = r"06_rezultatai/misko_proc.csv"


# ---------------------------------------------------------
# 2. Įkeliame duomenis
# ---------------------------------------------------------

print("Įkeliami sluoksniai...")

sklypai = gpd.read_file(sklypu_failas)
miskas = gpd.read_file(misko_failas)

print(f"Sklypų kiekis: {len(sklypai)}")
print(f"Miško objektų kiekis: {len(miskas)}")


# ---------------------------------------------------------
# 3. Patikriname CRS
# ---------------------------------------------------------

print(f"Sklypų CRS: {sklypai.crs}")
print(f"Miško sluoksnio CRS: {miskas.crs}")

if sklypai.crs != miskas.crs:
    print("CRS nesutampa, perprojektuojame miško sluoksnį...")
    miskas = miskas.to_crs(sklypai.crs)


# ---------------------------------------------------------
# 4. Tikriname, ar yra reikalingas ID stulpelis
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

print("Skaičiuojami susikirtimai tarp sklypų ir miško sluoksnio...")

susikirtimai = gpd.overlay(sklypai, miskas, how="intersection")

print(f"Susikirtimų kiekis: {len(susikirtimai)}")


# ---------------------------------------------------------
# 6. Jei susikirtimų nėra - procentas bus 0
# ---------------------------------------------------------

if len(susikirtimai) == 0:
    rezultatas = sklypai[["SKLYPO_ID"]].copy()
    rezultatas["misko_proc"] = 0.0
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
    rezultatas["misko_proc"] = (
        rezultatas["susikirtimo_plotas"] / rezultatas["sklypo_plotas"] * 100
    ).round(2)

    # Pasiliekame tik reikalingus stulpelius
    rezultatas = rezultatas[["SKLYPO_ID", "misko_proc"]].copy()


# ---------------------------------------------------------
# 7. Išsaugome CSV
# ---------------------------------------------------------

Path(isvedimo_failas).parent.mkdir(parents=True, exist_ok=True)
rezultatas.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

print("\nRezultatas išsaugotas:")
print(isvedimo_failas)

print("\nPirmos 10 eilučių:")
print(rezultatas.head(10))