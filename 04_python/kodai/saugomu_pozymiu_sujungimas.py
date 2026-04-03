# =========================================================
# FAILAS: saugomu_pozymiu_sujungimas.py
# PASKIRTIS:
# Sujungti visus saugomų teritorijų procentinius CSV
# į vieną bendrą lentelę pagal SKLYPO_ID.
# =========================================================

import pandas as pd
from functools import reduce
from pathlib import Path


# ---------------------------------------------------------
# 1. Nurodome visus CSV failus
# ---------------------------------------------------------

csv_failai = [
    r"06_rezultatai/draustiniu_proc.csv",
    r"06_rezultatai/rezervatu_proc.csv",
    r"06_rezultatai/parku_proc.csv",
    r"06_rezultatai/biosferos_poligonu_proc.csv",
    r"06_rezultatai/bast_proc.csv",
    r"06_rezultatai/past_proc.csv",
    r"06_rezultatai/pajurio_juostos_proc.csv",
    r"06_rezultatai/buferiniu_apsaugos_zonu_proc.csv"
]

isvedimo_failas = r"06_rezultatai/saugomu_teritoriju_pozymiai.csv"


# ---------------------------------------------------------
# 2. Įkeliame ir sutvarkome kiekvieną CSV
# ---------------------------------------------------------

duomenu_sarasas = []

for failas in csv_failai:
    df = pd.read_csv(failas)

    print(f"\nĮkeltas failas: {failas}")
    print(f"Eilučių skaičius prieš tvarkymą: {len(df)}")
    print(f"Stulpeliai: {df.columns.tolist()}")

    if "SKLYPO_ID" not in df.columns:
        raise ValueError(f"Faile {failas} nėra stulpelio 'SKLYPO_ID'.")

    # Pašaliname eilutes, kur nėra SKLYPO_ID
    df = df.dropna(subset=["SKLYPO_ID"]).copy()

    # Surandame procentinio požymio stulpelį
    kitu_stulpeliu = [st for st in df.columns if st != "SKLYPO_ID"]

    if len(kitu_stulpeliu) != 1:
        raise ValueError(
            f"Faile {failas} tikėtasi 1 požymio stulpelio, bet rasta: {kitu_stulpeliu}"
        )

    pozymio_stulpelis = kitu_stulpeliu[0]

    # Patikriname, kiek yra pasikartojančių SKLYPO_ID
    dublikatu_kiekis = df["SKLYPO_ID"].duplicated().sum()
    print(f"Pasikartojančių SKLYPO_ID kiekis: {dublikatu_kiekis}")

    # Jei tas pats SKLYPO_ID kartojasi, suagreguojame iki vienos eilutės
    # Naudojame max(), nes procentinis požymis vienam sklypui turėtų būti vienas,
    # o jei dėl duomenų struktūros atsirado keli įrašai, pasiimame didžiausią reikšmę.
    df = (
        df.groupby("SKLYPO_ID", as_index=False)[pozymio_stulpelis]
        .max()
    )

    print(f"Eilučių skaičius po sugrupavimo: {len(df)}")

    duomenu_sarasas.append(df)


# ---------------------------------------------------------
# 3. Sujungiame visus DataFrame pagal SKLYPO_ID
# ---------------------------------------------------------

galutinis_df = reduce(
    lambda kaire, desine: pd.merge(kaire, desine, on="SKLYPO_ID", how="outer"),
    duomenu_sarasas
)

print("\nSujungimas baigtas.")
print(f"Galutinis eilučių skaičius: {len(galutinis_df)}")


# ---------------------------------------------------------
# 4. Kur trūksta reikšmių - įrašome 0
# ---------------------------------------------------------

galutinis_df = galutinis_df.fillna(0)


# ---------------------------------------------------------
# 5. Išsaugome rezultatą
# ---------------------------------------------------------

Path(isvedimo_failas).parent.mkdir(parents=True, exist_ok=True)
galutinis_df.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

print(f"\nGalutinis failas išsaugotas:\n{isvedimo_failas}")

print("\nPirmos 10 eilučių:")
print(galutinis_df.head(10))