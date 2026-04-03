# =========================================================
# FAILAS: mini_dataset_papildymas_kulturos_paveldu.py
# PASKIRTIS:
# Prijungti kultūros paveldo procentinius požymius prie
# mini dataset'o su BP, saugomomis teritorijomis ir mišku.
# =========================================================

import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# 1. Failų keliai
# ---------------------------------------------------------

mini_dataset_failas = r"06_rezultatai/mini_dataset_bp_50_su_saugomomis_ir_misku.csv"
kvr_poligonu_failas = r"06_rezultatai/kvr_poligonu_proc.csv"
kvr_apsaugos_failas = r"06_rezultatai/kvr_apsaugos_zonu_proc.csv"

isvedimo_failas = r"06_rezultatai/mini_dataset_bp_50_su_saugomomis_misku_ir_kvr.csv"


# ---------------------------------------------------------
# 2. Įkeliame failus
# ---------------------------------------------------------

print("Įkeliami failai...")

mini_df = pd.read_csv(mini_dataset_failas)
kvr_pol_df = pd.read_csv(kvr_poligonu_failas)
kvr_aps_df = pd.read_csv(kvr_apsaugos_failas)

print(f"Mini dataset eilučių skaičius: {len(mini_df)}")
print(f"KVR poligonų eilučių skaičius: {len(kvr_pol_df)}")
print(f"KVR apsaugos zonų eilučių skaičius: {len(kvr_aps_df)}")


# ---------------------------------------------------------
# 3. Patikriname, ar yra SKLYPO_ID
# ---------------------------------------------------------

for pavadinimas, df in [
    ("mini dataset", mini_df),
    ("kvr_poligonu_proc", kvr_pol_df),
    ("kvr_apsaugos_zonu_proc", kvr_aps_df)
]:
    if "SKLYPO_ID" not in df.columns:
        raise ValueError(f"Faile {pavadinimas} nerastas stulpelis 'SKLYPO_ID'.")


# ---------------------------------------------------------
# 4. Jei KVR failuose yra dublikatų - sutvarkome
# ---------------------------------------------------------

for df, stulpelis in [
    (kvr_pol_df, "kvr_poligonu_proc"),
    (kvr_aps_df, "kvr_apsaugos_zonu_proc")
]:
    dublikatu_kiekis = df["SKLYPO_ID"].duplicated().sum()
    print(f"\nPasikartojančių SKLYPO_ID faile {stulpelis}: {dublikatu_kiekis}")

    if dublikatu_kiekis > 0:
        df_sugrupuotas = (
            df.groupby("SKLYPO_ID", as_index=False)[stulpelis]
            .max()
        )

        if stulpelis == "kvr_poligonu_proc":
            kvr_pol_df = df_sugrupuotas
        else:
            kvr_aps_df = df_sugrupuotas


# ---------------------------------------------------------
# 5. Sujungiame lenteles
# ---------------------------------------------------------

galutinis_df = mini_df.merge(
    kvr_pol_df,
    on="SKLYPO_ID",
    how="left"
)

galutinis_df = galutinis_df.merge(
    kvr_aps_df,
    on="SKLYPO_ID",
    how="left"
)

print("\nSujungimas atliktas.")
print(f"Galutinio failo eilučių skaičius: {len(galutinis_df)}")


# ---------------------------------------------------------
# 6. Užpildome trūkstamas reikšmes nuliais
# ---------------------------------------------------------

for stulpelis in ["kvr_poligonu_proc", "kvr_apsaugos_zonu_proc"]:
    if stulpelis in galutinis_df.columns:
        galutinis_df[stulpelis] = galutinis_df[stulpelis].fillna(0)


# ---------------------------------------------------------
# 7. Sukuriame dvejetainius požymius
# ---------------------------------------------------------

galutinis_df["ar_yra_kvr_poligonas"] = (galutinis_df["kvr_poligonu_proc"] > 0).astype(int)
galutinis_df["ar_yra_kvr_apsaugos_zona"] = (galutinis_df["kvr_apsaugos_zonu_proc"] > 0).astype(int)


# ---------------------------------------------------------
# 8. Išsaugome rezultatą
# ---------------------------------------------------------

Path(isvedimo_failas).parent.mkdir(parents=True, exist_ok=True)
galutinis_df.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

print(f"\nGalutinis failas išsaugotas:\n{isvedimo_failas}")

print("\nPirmos 10 eilučių:")
print(galutinis_df.head(10))