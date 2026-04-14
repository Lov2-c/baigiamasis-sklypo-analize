# =========================================================
# FAILAS: mini_dataset_agregavimas_10000.py
# PASKIRTIS:
# Iš mini_dataset_bp_10000.csv suformuoti agreguotą lentelę,
# kur vienam sklypui tenka viena eilutė.
# =========================================================

import pandas as pd


def suformuoti_agreguota_lentele(df):
    """
    Iš kelių BP zonų eilučių vienam sklypui
    suformuojame vieną eilutę.

    Pasiliekame:
    - pagrindinę zoną
    - antrą zoną (jei tokia yra)
    - pagrindinius sklypo atributus
    """

    agreguotos_eilutes = []

    grupes = df.groupby("SKLYPO_ID")

    for sklypo_id, grupe in grupes:
        grupe = grupe.sort_values(by="SUSIKIRTIMO_PROC", ascending=False).reset_index(drop=True)

        pirma = grupe.iloc[0]

        eilute = {
            "SKLYPO_ID": pirma["SKLYPO_ID"],
            "UNIKAL_ID": pirma["UNIKAL_ID"],
            "PLOTAS_REG": pirma["PLOTAS_REG"],
            "ADRESAS": pirma["ADRESAS"],
            "PASK_TIP": pirma["PASK_TIP"],
            "SKLYPO_PLOTAS_M2": pirma["SKLYPO_PLOTAS_M2"],

            "PAGRINDINE_ZONA_PAV": pirma["BP_ZONA_PAV"],
            "PAGRINDINE_ZONOS_KODAS": pirma["BP_ZONOS_KODAS"],
            "PAGRINDINE_U_INTENS": pirma["U_INTENS"],
            "PAGRINDINE_MAX_AUK_SK": pirma["MAX_AUK_SK"],
            "PAGRINDINE_PAGR_PASK": pirma["PAGR_PASK"],
            "PAGRINDINE_BP_OBJ_NR": pirma["BP_OBJ_NR"],
            "PAGRINDINE_ZONOS_PROC": pirma["SUSIKIRTIMO_PROC"],
        }

        # Jei yra antra zona, pasiimame ir ją
        if len(grupe) > 1:
            antra = grupe.iloc[1]

            eilute.update({
                "ANTRA_ZONA_PAV": antra["BP_ZONA_PAV"],
                "ANTRA_ZONOS_KODAS": antra["BP_ZONOS_KODAS"],
                "ANTRA_ZONOS_PROC": antra["SUSIKIRTIMO_PROC"],
            })
        else:
            eilute.update({
                "ANTRA_ZONA_PAV": None,
                "ANTRA_ZONOS_KODAS": None,
                "ANTRA_ZONOS_PROC": 0,
            })

        agreguotos_eilutes.append(eilute)

    return pd.DataFrame(agreguotos_eilutes)


if __name__ == "__main__":
    ivestis = "06_rezultatai/mini_dataset_bp_10000.csv"
    isvestis = "06_rezultatai/mini_dataset_bp_10000_agreguotas.csv"

    df = pd.read_csv(ivestis, encoding="utf-8-sig")

    print("Nuskaityta eilučių:", len(df))

    agreguotas_df = suformuoti_agreguota_lentele(df)

    print("Agreguotoje lentelėje eilučių:", len(agreguotas_df))
    print("\nPirmos 5 eilutės:")
    print(agreguotas_df.head())

    agreguotas_df.to_csv(isvestis, index=False, encoding="utf-8-sig")

    print("\nAgreguota lentelė išsaugota:")
    print(isvestis)