import pandas as pd


# -----------------------------------
# FAILŲ KELIAI
# -----------------------------------
ivesties_kelias = "06_rezultatai/mini_dataset_bp_50.csv"
isvesties_kelias = "06_rezultatai/mini_dataset_bp_50_agreguotas.csv"


def nustatyti_zonos_pozymius(sklypo_grupe):
    """
    Ši funkcija pagal visas sklypo zonas nustato,
    ar sklype yra tam tikrų tipų teritorijų.
    """

    zonu_kodai = sklypo_grupe["BP_ZONOS_KODAS"].dropna().astype(str).tolist()

    return {
        "ar_yra_gyvenamoji_zona": int(any(kodas.startswith("U_GG") for kodas in zonu_kodai)),
        "ar_yra_zemes_ukio_zona": int(any(kodas.startswith("ZU") for kodas in zonu_kodai)),
        "ar_yra_misku_zona": int(any(kodas.startswith("MI") for kodas in zonu_kodai)),
        "ar_yra_pramones_zona": int(any(kodas.startswith("U_PS") for kodas in zonu_kodai)),
    }


def agreguoti_vieno_sklypo_duomenis(sklypo_grupe):
    """
    Ši funkcija vieno sklypo kelių eilučių BP duomenis
    paverčia į vieną eilutę.
    """

    # Išrikiuojame zonas pagal didžiausią procentą
    sklypo_grupe = sklypo_grupe.sort_values(
        by="SUSIKIRTIMO_PROC",
        ascending=False
    ).reset_index(drop=True)

    # Pagrindinė zona = ta, kuri turi didžiausią procentą
    pagrindine_zona = sklypo_grupe.iloc[0]

    # Antra zona - jei tokia egzistuoja
    if len(sklypo_grupe) > 1:
        antra_zona = sklypo_grupe.iloc[1]
        antra_zona_pavadinimas = antra_zona["BP_ZONA_PAV"]
        antra_zona_kodas = antra_zona["BP_ZONOS_KODAS"]
        antra_zona_proc = antra_zona["SUSIKIRTIMO_PROC"]
    else:
        antra_zona_pavadinimas = None
        antra_zona_kodas = None
        antra_zona_proc = 0.0

    # Suskaičiuojame papildomus požymius
    zonos_pozymiai = nustatyti_zonos_pozymius(sklypo_grupe)

    # Sudedame viską į vieną eilutę
    eilute = {
        "SKLYPO_ID": pagrindine_zona["SKLYPO_ID"],
        "UNIKAL_ID": pagrindine_zona["UNIKAL_ID"],
        "PLOTAS_REG": pagrindine_zona["PLOTAS_REG"],
        "ADRESAS": pagrindine_zona["ADRESAS"],
        "PASK_TIP": pagrindine_zona["PASK_TIP"],
        "SKLYPO_PLOTAS_M2": pagrindine_zona["SKLYPO_PLOTAS_M2"],
        "zonu_kiekis": len(sklypo_grupe),
        "pagrindine_zona_pavadinimas": pagrindine_zona["BP_ZONA_PAV"],
        "pagrindine_zona_kodas": pagrindine_zona["BP_ZONOS_KODAS"],
        "pagrindine_zona_proc": pagrindine_zona["SUSIKIRTIMO_PROC"],
        "pagrindine_u_intens": pagrindine_zona["U_INTENS"],
        "pagrindine_max_auk_sk": pagrindine_zona["MAX_AUK_SK"],
        "pagrindine_pagr_pask": pagrindine_zona["PAGR_PASK"],
        "antra_zona_pavadinimas": antra_zona_pavadinimas,
        "antra_zona_kodas": antra_zona_kodas,
        "antra_zona_proc": antra_zona_proc,
    }

    # Pridedame loginius zonų požymius
    eilute.update(zonos_pozymiai)

    return eilute


if __name__ == "__main__":
    print("Nuskaitomas mini-datasetas...")
    df = pd.read_csv(ivesties_kelias)

    print("=== PRADINĖ INFORMACIJA ===")
    print("Eilučių skaičius prieš agregavimą:", len(df))
    print("Unikalių sklypų skaičius:", df["SKLYPO_ID"].nunique())
    print()

    # Grupavimas pagal sklypą
    agreguotos_eilutes = []

    for sklypo_id, sklypo_grupe in df.groupby("SKLYPO_ID"):
        agreguota_eilute = agreguoti_vieno_sklypo_duomenis(sklypo_grupe)
        agreguotos_eilutes.append(agreguota_eilute)

    # Sukuriame naują DataFrame
    agreguotas_df = pd.DataFrame(agreguotos_eilutes)

    # Surikiuojame pagal SKLYPO_ID
    agreguotas_df = agreguotas_df.sort_values(by="SKLYPO_ID").reset_index(drop=True)

    print("=== AGREGUOTO DATASETO REZULTATAS ===")
    print("Eilučių skaičius po agregavimo:", len(agreguotas_df))
    print()

    print("=== PIRMOS 10 EILUČIŲ ===")
    print(agreguotas_df.head(10))
    print()

    # Išsaugome į CSV
    agreguotas_df.to_csv(isvesties_kelias, index=False, encoding="utf-8-sig")

    print("Agreguotas datasetas išsaugotas faile:")
    print(isvesties_kelias)