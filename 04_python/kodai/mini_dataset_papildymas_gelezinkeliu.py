# =========================================================
# FAILAS: mini_dataset_papildymas_gelezinkeliu.py
# PASKIRTIS:
# Prijungti geležinkelio ribojimo zonos požymį prie
# galutinio mini dataset'o.
# =========================================================

import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# 1. Failų keliai
# ---------------------------------------------------------

mini_dataset_failas = r"06_rezultatai/mini_dataset_bp_50_galutinis.csv"
gelezinkelio_failas = r"06_rezultatai/gelezinkelio_ribojimo_zonos_proc.csv"
isvedimo_failas = r"06_rezultatai/mini_dataset_bp_50_galutinis_plus_gelezinkelis.csv"


# ---------------------------------------------------------
# 2. Įkeliame failus
# ---------------------------------------------------------

print("Įkeliami failai...")

mini_df = pd.read_csv(mini_dataset_failas)
gelezinkelio_df = pd.read_csv(gelezinkelio_failas)

print(f"Mini dataset eilučių skaičius: {len(mini_df)}")
print(f"Geležinkelio failo eilučių skaičius: {len(gelezinkelio_df)}")


# ---------------------------------------------------------
# 3. Patikriname, ar visur yra SKLYPO_ID
# ---------------------------------------------------------

if "SKLYPO_ID" not in mini_df.columns:
    raise ValueError("Mini dataset faile nerastas stulpelis 'SKLYPO_ID'.")

if "SKLYPO_ID" not in gelezinkelio_df.columns:
    raise ValueError("Geležinkelio faile nerastas stulpelis 'SKLYPO_ID'.")


# ---------------------------------------------------------
# 4. Jei yra dublikatų - sutvarkome
# ---------------------------------------------------------

dublikatu_kiekis = gelezinkelio_df["SKLYPO_ID"].duplicated().sum()
print(f"Pasikartojančių SKLYPO_ID geležinkelio faile: {dublikatu_kiekis}")

if dublikatu_kiekis > 0:
    gelezinkelio_df = (
        gelezinkelio_df.groupby("SKLYPO_ID", as_index=False)["gelezinkelio_ribojimo_zonos_proc"]
        .max()
    )


# ---------------------------------------------------------
# 5. Sujungiame lenteles
# ---------------------------------------------------------

galutinis_df = mini_df.merge(
    gelezinkelio_df,
    on="SKLYPO_ID",
    how="left"
)

print("\nSujungimas atliktas.")
print(f"Galutinio failo eilučių skaičius: {len(galutinis_df)}")


# ---------------------------------------------------------
# 6. Užpildome trūkstamas reikšmes nuliais
# ---------------------------------------------------------

galutinis_df["gelezinkelio_ribojimo_zonos_proc"] = (
    galutinis_df["gelezinkelio_ribojimo_zonos_proc"].fillna(0)
)


# ---------------------------------------------------------
# 7. Sukuriame dvejetainį požymį
# ---------------------------------------------------------

galutinis_df["ar_yra_gelezinkelio_ribojimo_zona"] = (
    galutinis_df["gelezinkelio_ribojimo_zonos_proc"] > 0
).astype(int)


# ---------------------------------------------------------
# 8. Išsaugome rezultatą
# ---------------------------------------------------------

Path(isvedimo_failas).parent.mkdir(parents=True, exist_ok=True)
galutinis_df.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

print(f"\nGalutinis failas išsaugotas:\n{isvedimo_failas}")

print("\nPirmos 10 eilučių:")
print(galutinis_df.head(10))