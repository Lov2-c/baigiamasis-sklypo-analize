# =========================================================
# FAILAS: mini_dataset_sujungimas_su_kvr_10000.py
# PASKIRTIS:
# Prijungti KVR požymius prie 10000 sklypų mini dataset,
# kuris jau papildytas saugomomis teritorijomis ir mišku.
# =========================================================

import pandas as pd


if __name__ == "__main__":
    mini_dataset_kelias = "06_rezultatai/mini_dataset_bp_10000_su_saugomomis_ir_misku.csv"
    kvr_poligonu_kelias = "06_rezultatai/kvr_poligonu_proc.csv"
    kvr_apsaugos_zonu_kelias = "06_rezultatai/kvr_apsaugos_zonu_proc.csv"

    mini_df = pd.read_csv(mini_dataset_kelias, encoding="utf-8-sig")
    kvr_poligonu_df = pd.read_csv(kvr_poligonu_kelias, encoding="utf-8-sig")
    kvr_apsaugos_df = pd.read_csv(kvr_apsaugos_zonu_kelias, encoding="utf-8-sig")

    print("Pagrindinis mini dataset nuskaitytas.")
    print("Eilučių:", len(mini_df))
    print()

    print("KVR poligonų failas nuskaitytas.")
    print("Eilučių:", len(kvr_poligonu_df))
    print("Stulpeliai:", list(kvr_poligonu_df.columns))
    print()

    print("KVR apsaugos zonų failas nuskaitytas.")
    print("Eilučių:", len(kvr_apsaugos_df))
    print("Stulpeliai:", list(kvr_apsaugos_df.columns))
    print()

    # -----------------------------------
    # 1. Jei reikia, agreguojame iki vienos eilutės vienam sklypui
    # -----------------------------------
    if "SKLYPO_ID" in kvr_poligonu_df.columns and "kvr_poligonu_proc" in kvr_poligonu_df.columns:
        kvr_poligonu_df = (
            kvr_poligonu_df.groupby("SKLYPO_ID", as_index=False)["kvr_poligonu_proc"]
            .max()
        )

    if "SKLYPO_ID" in kvr_apsaugos_df.columns and "kvr_apsaugos_zonu_proc" in kvr_apsaugos_df.columns:
        kvr_apsaugos_df = (
            kvr_apsaugos_df.groupby("SKLYPO_ID", as_index=False)["kvr_apsaugos_zonu_proc"]
            .max()
        )

    print("Po agregavimo:")
    print("KVR poligonų eilučių:", len(kvr_poligonu_df))
    print("KVR apsaugos zonų eilučių:", len(kvr_apsaugos_df))
    print()

    # -----------------------------------
    # 2. Prijungiame KVR poligonus
    # -----------------------------------
    galutinis_df = mini_df.merge(
        kvr_poligonu_df,
        on="SKLYPO_ID",
        how="left"
    )

    # -----------------------------------
    # 3. Prijungiame KVR apsaugos zonas
    # -----------------------------------
    galutinis_df = galutinis_df.merge(
        kvr_apsaugos_df,
        on="SKLYPO_ID",
        how="left"
    )

    # -----------------------------------
    # 4. Užpildome trūkstamas reikšmes nuliais
    # -----------------------------------
    if "kvr_poligonu_proc" in galutinis_df.columns:
        galutinis_df["kvr_poligonu_proc"] = galutinis_df["kvr_poligonu_proc"].fillna(0)

    if "kvr_apsaugos_zonu_proc" in galutinis_df.columns:
        galutinis_df["kvr_apsaugos_zonu_proc"] = galutinis_df["kvr_apsaugos_zonu_proc"].fillna(0)

    print("Po sujungimo eilučių:", len(galutinis_df))
    print()
    print("Pirmos 5 eilutės:")
    print(galutinis_df.head())
    print()

    isvedimo_kelias = "06_rezultatai/mini_dataset_bp_10000_su_saugomomis_misku_ir_kvr.csv"
    galutinis_df.to_csv(isvedimo_kelias, index=False, encoding="utf-8-sig")

    print("Failas išsaugotas:")
    print(isvedimo_kelias)