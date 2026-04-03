# =========================================================
# FAILAS: mini_dataset_papildymas_szns.py
# PASKIRTIS:
# Prijungti pelkių, šaltinynų ir pievų/ganyklų procentinius
# požymius prie mini dataset'o.
# =========================================================

import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# 1. Failų keliai
# ---------------------------------------------------------

mini_dataset_failas = r"06_rezultatai/mini_dataset_bp_50_su_saugomomis_misku_ir_kvr.csv"
pelkiu_failas = r"06_rezultatai/pelkiu_proc.csv"
saltinynu_failas = r"06_rezultatai/saltinynu_proc.csv"
pievu_failas = r"06_rezultatai/pievu_ganyklu_proc.csv"

isvedimo_failas = r"06_rezultatai/mini_dataset_bp_50_pilnas.csv"


# ---------------------------------------------------------
# 2. Įkeliame failus
# ---------------------------------------------------------

print("Įkeliami failai...")

mini_df = pd.read_csv(mini_dataset_failas)
pelkiu_df = pd.read_csv(pelkiu_failas)
saltinynu_df = pd.read_csv(saltinynu_failas)
pievu_df = pd.read_csv(pievu_failas)

print(f"Mini dataset eilučių skaičius: {len(mini_df)}")
print(f"Pelkių failo eilučių skaičius: {len(pelkiu_df)}")
print(f"Šaltinynų failo eilučių skaičius: {len(saltinynu_df)}")
print(f"Pievų/ganyklų failo eilučių skaičius: {len(pievu_df)}")


# ---------------------------------------------------------
# 3. Patikriname, ar visur yra SKLYPO_ID
# ---------------------------------------------------------

for pavadinimas, df in [
    ("mini dataset", mini_df),
    ("pelkiu_proc", pelkiu_df),
    ("saltinynu_proc", saltinynu_df),
    ("pievu_ganyklu_proc", pievu_df)
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


pelkiu_df = sutvarkyti_dublikatus(pelkiu_df, "pelkiu_proc")
saltinynu_df = sutvarkyti_dublikatus(saltinynu_df, "saltinynu_proc")
pievu_df = sutvarkyti_dublikatus(pievu_df, "pievu_ganyklu_proc")


# ---------------------------------------------------------
# 5. Sujungiame lenteles
# ---------------------------------------------------------

galutinis_df = mini_df.merge(
    pelkiu_df,
    on="SKLYPO_ID",
    how="left"
)

galutinis_df = galutinis_df.merge(
    saltinynu_df,
    on="SKLYPO_ID",
    how="left"
)

galutinis_df = galutinis_df.merge(
    pievu_df,
    on="SKLYPO_ID",
    how="left"
)

print("\nSujungimas atliktas.")
print(f"Galutinio failo eilučių skaičius: {len(galutinis_df)}")


# ---------------------------------------------------------
# 6. Užpildome trūkstamas reikšmes nuliais
# ---------------------------------------------------------

for stulpelis in ["pelkiu_proc", "saltinynu_proc", "pievu_ganyklu_proc"]:
    if stulpelis in galutinis_df.columns:
        galutinis_df[stulpelis] = galutinis_df[stulpelis].fillna(0)


# ---------------------------------------------------------
# 7. Sukuriame dvejetainius požymius
# ---------------------------------------------------------

galutinis_df["ar_yra_pelke"] = (galutinis_df["pelkiu_proc"] > 0).astype(int)
galutinis_df["ar_yra_saltinynas"] = (galutinis_df["saltinynu_proc"] > 0).astype(int)
galutinis_df["ar_yra_pievos_ganyklos"] = (galutinis_df["pievu_ganyklu_proc"] > 0).astype(int)


# ---------------------------------------------------------
# 8. Išsaugome rezultatą
# ---------------------------------------------------------

Path(isvedimo_failas).parent.mkdir(parents=True, exist_ok=True)
galutinis_df.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

print(f"\nGalutinis failas išsaugotas:\n{isvedimo_failas}")

print("\nPirmos 10 eilučių:")
print(galutinis_df.head(10))