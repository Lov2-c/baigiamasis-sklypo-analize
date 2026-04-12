# =========================================================
# FAILAS: mini_dataset_sujungimas_su_saugomomis_1000.py
# PASKIRTIS:
# Prijungti saugomų teritorijų požymius prie 1000 sklypų
# agreguoto mini dataset.
# =========================================================

import pandas as pd


if __name__ == "__main__":
    # -----------------------------------
    # 1. Nuskaitome pagrindinį agreguotą mini dataset
    # -----------------------------------
    mini_dataset_kelias = "06_rezultatai/mini_dataset_bp_1000_agreguotas.csv"
    saugomu_pozymiu_kelias = "06_rezultatai/saugomu_teritoriju_pozymiai.csv"

    mini_df = pd.read_csv(mini_dataset_kelias, encoding="utf-8-sig")
    saugomu_df = pd.read_csv(saugomu_pozymiu_kelias, encoding="utf-8-sig")

    print("Pagrindinis mini dataset nuskaitytas.")
    print("Eilučių:", len(mini_df))
    print()

    print("Saugomų teritorijų požymių failas nuskaitytas.")
    print("Eilučių:", len(saugomu_df))
    print("Stulpeliai:")
    print(list(saugomu_df.columns))
    print()

    # -----------------------------------
    # 2. Sujungiame per SKLYPO_ID
    # -----------------------------------
    galutinis_df = mini_df.merge(
        saugomu_df,
        on="SKLYPO_ID",
        how="left"
    )

    # -----------------------------------
    # 3. Jei saugomų teritorijų požymių nėra,
    # užpildome 0
    # -----------------------------------
    saugomu_stulpeliai = [
        "draustiniu_proc",
        "rezervatu_proc",
        "parku_proc",
        "biosferos_poligonu_proc",
        "bast_proc",
        "past_proc",
        "pajurio_juostos_proc",
        "buferiniu_apsaugos_zonu_proc",
    ]

    for stulpelis in saugomu_stulpeliai:
        if stulpelis in galutinis_df.columns:
            galutinis_df[stulpelis] = galutinis_df[stulpelis].fillna(0)

    # -----------------------------------
    # 4. Parodome rezultatą
    # -----------------------------------
    print("Po sujungimo eilučių:", len(galutinis_df))
    print()
    print("Pirmos 5 eilutės:")
    print(galutinis_df.head())
    print()

    # -----------------------------------
    # 5. Išsaugome
    # -----------------------------------
    isvedimo_kelias = "06_rezultatai/mini_dataset_bp_1000_su_saugomomis.csv"
    galutinis_df.to_csv(isvedimo_kelias, index=False, encoding="utf-8-sig")

    print("Failas išsaugotas:")
    print(isvedimo_kelias)