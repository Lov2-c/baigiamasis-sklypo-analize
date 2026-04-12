# =========================================================
# FAILAS: misko_procentine_analize.py
# PASKIRTIS:
# Apskaičiuoti, kokia kiekvieno sklypo dalis (%) patenka
# į miško sklypų sluoksnį.
#
# SVARBI PASTABA:
# Prieš skaičiavimą sujungiame visas to paties SKLYPO_ID
# geometrijas į vieną objektą, kad vienam sklypui tektų
# viena galutinė eilutė ir procentas neviršytų 100.
# =========================================================

import geopandas as gpd
from pathlib import Path


# ---------------------------------------------------------
# 1. Failų keliai
# ---------------------------------------------------------

sklypu_failas = r"01_duomenys/sklypai/klaipedos_raj_ribos_2019.gpkg"
misko_failas = r"01_duomenys/papildomi/miskai/misko_sklypai.gpkg"
isvedimo_failas = r"06_rezultatai/misko_proc.csv"


# ---------------------------------------------------------
# 2. Įkeliame duomenis
# ---------------------------------------------------------

print("Įkeliami sluoksniai...")

sklypai = gpd.read_file(sklypu_failas)
miskas = gpd.read_file(misko_failas)

print(f"Sklypų kiekis pradžioje: {len(sklypai)}")
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
# 4. Paliekame tik reikalingus laukus ir sutvarkome geometrijas
# ---------------------------------------------------------

if "SKLYPO_ID" not in sklypai.columns:
    raise ValueError("Sklypų sluoksnyje nerastas stulpelis 'SKLYPO_ID'.")

sklypai = sklypai[["SKLYPO_ID", "geometry"]].copy()
sklypai = sklypai.dropna(subset=["SKLYPO_ID"]).copy()
sklypai = sklypai[sklypai.geometry.notna()].copy()
sklypai = sklypai[~sklypai.geometry.is_empty].copy()

miskas = miskas[miskas.geometry.notna()].copy()
miskas = miskas[~miskas.geometry.is_empty].copy()

# Sutvarkome galimai netvarkingas geometrijas
try:
    sklypai.geometry = sklypai.geometry.buffer(0)
except Exception:
    pass

try:
    miskas.geometry = miskas.geometry.buffer(0)
except Exception:
    pass

print(f"Sklypų kiekis po filtravimo: {len(sklypai)}")


# ---------------------------------------------------------
# 5. Sujungiame sklypų geometrijas pagal SKLYPO_ID
# ---------------------------------------------------------

print("Sujungiamos sklypų geometrijos pagal SKLYPO_ID...")

sklypai_sujungti = sklypai.dissolve(by="SKLYPO_ID").reset_index()

print(f"Sklypų kiekis po sujungimo pagal SKLYPO_ID: {len(sklypai_sujungti)}")

# Perskaičiuojame plotą jau sujungtam sklypui
sklypai_sujungti["sklypo_plotas"] = sklypai_sujungti.geometry.area


# ---------------------------------------------------------
# 6. Apskaičiuojame susikirtimus
# ---------------------------------------------------------

print("Skaičiuojami susikirtimai tarp sujungtų sklypų ir miško sluoksnio...")

susikirtimai = gpd.overlay(
    sklypai_sujungti[["SKLYPO_ID", "geometry"]],
    miskas[["geometry"]],
    how="intersection"
)

print(f"Susikirtimų kiekis: {len(susikirtimai)}")


# ---------------------------------------------------------
# 7. Formuojame rezultatą
# ---------------------------------------------------------

if len(susikirtimai) == 0:
    rezultatas = sklypai_sujungti[["SKLYPO_ID"]].copy()
    rezultatas["misko_proc"] = 0.0
else:
    susikirtimai["susikirtimo_plotas"] = susikirtimai.geometry.area

    susikirtimu_suma = (
        susikirtimai.groupby("SKLYPO_ID", as_index=False)["susikirtimo_plotas"]
        .sum()
    )

    rezultatas = sklypai_sujungti[["SKLYPO_ID", "sklypo_plotas"]].merge(
        susikirtimu_suma,
        on="SKLYPO_ID",
        how="left"
    )

    rezultatas["susikirtimo_plotas"] = rezultatas["susikirtimo_plotas"].fillna(0)

    rezultatas["misko_proc"] = (
        rezultatas["susikirtimo_plotas"] / rezultatas["sklypo_plotas"] * 100
    ).round(2)

    rezultatas = rezultatas[["SKLYPO_ID", "misko_proc"]].copy()


# ---------------------------------------------------------
# 8. Papildoma patikra
# ---------------------------------------------------------

print("\nTikrinama, ar nėra pasikartojančių SKLYPO_ID...")
print("Pasikartojančių SKLYPO_ID:", rezultatas["SKLYPO_ID"].duplicated().sum())

print("Didžiausia misko_proc reikšmė:", rezultatas["misko_proc"].max())


# ---------------------------------------------------------
# 9. Išsaugome CSV
# ---------------------------------------------------------

Path(isvedimo_failas).parent.mkdir(parents=True, exist_ok=True)
rezultatas.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

print("\nRezultatas išsaugotas:")
print(isvedimo_failas)

print("\nPirmos 10 eilučių:")
print(rezultatas.head(10))