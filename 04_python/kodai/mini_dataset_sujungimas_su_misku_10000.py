# =========================================================
# FAILAS: mini_dataset_sujungimas_su_misku_10000.py
# PASKIRTIS:
# Prijungti miško požymį prie 10000 sklypų mini dataset,
# kuris jau papildytas saugomomis teritorijomis.
# =========================================================

import pandas as pd


if __name__ == "__main__":
    mini_dataset_kelias = "06_rezultatai/mini_dataset_bp_10000_su_saugomomis.csv"
    misko_pozymio_kelias = "06_rezultatai/misko_proc.csv"

    mini_df = pd.read_csv(mini_dataset_kelias, encoding="utf-8-sig")
    misko_df = pd.read_csv(misko_pozymio_kelias, encoding="utf-8-sig")

    print("Mini dataset nuskaitytas.")
    print("Eilučių:", len(mini_df))
    print()

    print("Miško požymio failas nuskaitytas.")
    print("Eilučių:", len(misko_df))
    print("Stulpeliai:")
    print(list(misko_df.columns))
    print()

    galutinis_df = mini_df.merge(
        misko_df,
        on="SKLYPO_ID",
        how="left"
    )

    if "misko_proc" in galutinis_df.columns:
        galutinis_df["misko_proc"] = galutinis_df["misko_proc"].fillna(0)

    print("Po sujungimo eilučių:", len(galutinis_df))
    print()
    print("Pirmos 5 eilutės:")
    print(galutinis_df.head())
    print()

    isvedimo_kelias = "06_rezultatai/mini_dataset_bp_10000_su_saugomomis_ir_misku.csv"
    galutinis_df.to_csv(isvedimo_kelias, index=False, encoding="utf-8-sig")

    print("Failas išsaugotas:")
    print(isvedimo_kelias)