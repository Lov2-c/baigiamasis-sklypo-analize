import pandas as pd

from sklypo_analize_funkcija import analizuoti_sklypa
from preliminarus_vertinimas import nustatyti_preliminaria_klase


def paruosti_features(bp_kelias, sklypo_kelias):
    """
    Ši funkcija:
    1. atlieka sklypo analizę,
    2. nustato preliminarią klasę,
    3. sudeda rezultatą į vienos eilutės DataFrame.

    Tai pirmas žingsnis į būsimo dataset formavimą.
    """

    # Paleidžiame pagrindinę analizę
    rezultatas = analizuoti_sklypa(bp_kelias, sklypo_kelias)

    # Jei analizė nepavyko, grąžiname klaidą
    if not rezultatas["sekme"]:
        return None, rezultatas["zinute"]

    # Nustatome preliminarią klasę
    preliminari_klase = nustatyti_preliminaria_klase(rezultatas["zonos_kodas"])

    # Sudedame viską į vieną žodyną
    eilute = {
        "zona_pavadinimas": rezultatas["zona_pavadinimas"],
        "zonos_kodas": rezultatas["zonos_kodas"],
        "uzstatymo_intensyvumas": rezultatas["uzstatymo_intensyvumas"],
        "max_aukstu_skaicius": rezultatas["max_aukstu_skaicius"],
        "pagrindine_paskirtis": rezultatas["pagrindine_paskirtis"],
        "objekto_nr": rezultatas["objekto_nr"],
        "preliminari_klase": preliminari_klase
    }

    # Paverčiame į DataFrame
    df = pd.DataFrame([eilute])

    return df, None


if __name__ == "__main__":
    bp_kelias = "01_duomenys/bp/bp_funkc.shp"
    sklypo_kelias = "03_eksportai/sklypas.gpkg"

    df, klaida = paruosti_features(bp_kelias, sklypo_kelias)

    if klaida:
        print("=== KLAIDA ===")
        print(klaida)
    else:
        print("=== FEATURES LENTELĖ ===")
        print(df)