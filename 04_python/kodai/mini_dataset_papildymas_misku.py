# =========================================================
# FAILAS: mini_dataset_papildymas_misku.py
# PASKIRTIS:
# Prijungti miško procentinį požymį prie jau turimo
# mini dataset'o su BP ir saugomomis teritorijomis.
# =========================================================

import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# 1. Failų keliai
# ---------------------------------------------------------

mini_dataset_failas = r"06_rezultatai/mini_dataset_bp_50_su_saugomomis.csv"
misko_failas = r"06_rezultatai/misko_proc.csv"
isvedimo_failas = r"06_rezultatai/mini_dataset_bp_50_su_saugomomis_ir_misku.csv"


# ---------------------------------------------------------
# 2. Įkeliame failus
# ---------------------------------------------------------

print("Įkeliami failai...")

mini_df = pd.read_csv(mini_dataset_failas)
misko_df = pd.read_csv(misko_failas)

print(f"Mini dataset eilučių skaičius: {len(mini_df)}")
print(f"Miško lentelės eilučių skaičius: {len(misko_df)}")

print("\nMini dataset stulpeliai:")
print(mini_df.columns.tolist())

print("\nMiško lentelės stulpeliai:")
print(misko_df.columns.tolist())


# ---------------------------------------------------------
# 3. Patikriname, ar yra SKLYPO_ID
# ---------------------------------------------------------

if "SKLYPO_ID" not in mini_df.columns:
    raise ValueError("Mini dataset faile nerastas stulpelis 'SKLYPO_ID'.")

if "SKLYPO_ID" not in misko_df.columns:
    raise ValueError("Miško faile nerastas stulpelis 'SKLYPO_ID'.")


# ---------------------------------------------------------
# 4. Jei misko faile yra pasikartojančių SKLYPO_ID - sutvarkome
# ---------------------------------------------------------

dublikatu_kiekis = misko_df["SKLYPO_ID"].duplicated().sum()
print(f"\nPasikartojančių SKLYPO_ID miško faile: {dublikatu_kiekis}")

if dublikatu_kiekis > 0:
    misko_df = (
        misko_df.groupby("SKLYPO_ID", as_index=False)["misko_proc"]
        .max()
    )
    print(f"Eilučių skaičius po miško failo sugrupavimo: {len(misko_df)}")


# ---------------------------------------------------------
# 5. Sujungiame lenteles
# ---------------------------------------------------------

galutinis_df = mini_df.merge(
    misko_df,
    on="SKLYPO_ID",
    how="left"
)

print("\nSujungimas atliktas.")
print(f"Galutinio failo eilučių skaičius: {len(galutinis_df)}")


# ---------------------------------------------------------
# 6. Kur nėra reikšmės - įrašome 0
# ---------------------------------------------------------

if "misko_proc" in galutinis_df.columns:
    galutinis_df["misko_proc"] = galutinis_df["misko_proc"].fillna(0)


# ---------------------------------------------------------
# 7. Sukuriame papildomą dvejetainį požymį
# ---------------------------------------------------------

galutinis_df["ar_yra_miskas_proc"] = (galutinis_df["misko_proc"] > 0).astype(int)


# ---------------------------------------------------------
# 8. Išsaugome rezultatą
# ---------------------------------------------------------

Path(isvedimo_failas).parent.mkdir(parents=True, exist_ok=True)
galutinis_df.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

print(f"\nGalutinis failas išsaugotas:\n{isvedimo_failas}")

print("\nPirmos 10 eilučių:")
print(galutinis_df.head(10))