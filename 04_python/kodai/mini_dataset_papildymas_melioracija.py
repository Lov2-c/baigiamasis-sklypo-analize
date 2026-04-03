# =========================================================
# FAILAS: mini_dataset_papildymas_melioracija.py
# PASKIRTIS:
# Prijungti melioracijos požymius prie pilno mini dataset'o.
# =========================================================

import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# 1. Failų keliai
# ---------------------------------------------------------

mini_dataset_failas = r"06_rezultatai/mini_dataset_bp_50_pilnas.csv"
drenazo_failas = r"06_rezultatai/drenazo_plotu_proc.csv"
rinktuvu_failas = r"06_rezultatai/rinktuvu_apsaugos_zonu_proc.csv"

isvedimo_failas = r"06_rezultatai/mini_dataset_bp_50_galutinis.csv"


# ---------------------------------------------------------
# 2. Įkeliame failus
# ---------------------------------------------------------

print("Įkeliami failai...")

mini_df = pd.read_csv(mini_dataset_failas)
drenazo_df = pd.read_csv(drenazo_failas)
rinktuvu_df = pd.read_csv(rinktuvu_failas)

print(f"Mini dataset eilučių skaičius: {len(mini_df)}")
print(f"Drenažo failo eilučių skaičius: {len(drenazo_df)}")
print(f"Rinktuvų failo eilučių skaičius: {len(rinktuvu_df)}")


# ---------------------------------------------------------
# 3. Patikriname, ar visur yra SKLYPO_ID
# ---------------------------------------------------------

for pavadinimas, df in [
    ("mini dataset", mini_df),
    ("drenazo_plotu_proc", drenazo_df),
    ("rinktuvu_apsaugos_zonu_proc", rinktuvu_df)
]:
    if "SKLYPO_ID" not in df.columns:
        raise ValueError(f"Faile {pavadinimas} nerastas stulpelis 'SKLYPO_ID'.")


# ---------------------------------------------------------
# 4. Jei yra dublikatų - sutvarkome
# ---------------------------------------------------------

def sutvarkyti_dublikatus(df, stulpelis):
    dublikatu_kiekis = df["SKLYPO_ID"].duplicated().sum()
    print(f"Pasikartojančių SKLYPO_ID faile {stulpelis}: {dublikatu_kiekis}")

    if dublikatu_kiekis > 0:
        df = df.groupby("SKLYPO_ID", as_index=False)[stulpelis].max()

    return df


drenazo_df = sutvarkyti_dublikatus(drenazo_df, "drenazo_plotu_proc")
rinktuvu_df = sutvarkyti_dublikatus(rinktuvu_df, "rinktuvu_apsaugos_zonu_proc")


# ---------------------------------------------------------
# 5. Sujungiame lenteles
# ---------------------------------------------------------

galutinis_df = mini_df.merge(
    drenazo_df,
    on="SKLYPO_ID",
    how="left"
)

galutinis_df = galutinis_df.merge(
    rinktuvu_df,
    on="SKLYPO_ID",
    how="left"
)

print("\nSujungimas atliktas.")
print(f"Galutinio failo eilučių skaičius: {len(galutinis_df)}")


# ---------------------------------------------------------
# 6. Užpildome trūkstamas reikšmes nuliais
# ---------------------------------------------------------

for stulpelis in ["drenazo_plotu_proc", "rinktuvu_apsaugos_zonu_proc"]:
    if stulpelis in galutinis_df.columns:
        galutinis_df[stulpelis] = galutinis_df[stulpelis].fillna(0)


# ---------------------------------------------------------
# 7. Sukuriame dvejetainius požymius
# ---------------------------------------------------------

galutinis_df["ar_yra_drenazo_plotai"] = (galutinis_df["drenazo_plotu_proc"] > 0).astype(int)
galutinis_df["ar_yra_rinktuvu_apsaugos_zona"] = (galutinis_df["rinktuvu_apsaugos_zonu_proc"] > 0).astype(int)


# ---------------------------------------------------------
# 8. Išsaugome rezultatą
# ---------------------------------------------------------

Path(isvedimo_failas).parent.mkdir(parents=True, exist_ok=True)
galutinis_df.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

print(f"\nGalutinis failas išsaugotas:\n{isvedimo_failas}")

print("\nPirmos 10 eilučių:")
print(galutinis_df.head(10))