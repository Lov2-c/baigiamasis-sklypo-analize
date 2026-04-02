from sklypo_analize_funkcija import analizuoti_sklypa


def nustatyti_preliminaria_klase(zonos_kodas):
    """
    Pagal BP zonos kodą priskiriama labai preliminari klasė:
    - palanku
    - ribota
    - nepalanku

    Vėliau šią logiką plėsime su papildomais apribojimais.
    """

    palankios_zonos = [
        "U_GG_E_F",
        "U_GG_M_F",
        "U_GG_E_E",
        "U_BZ_F",
        "U_PS_F",
    ]

    nepalankios_zonos = [
        "H_F",
        "M_F",
        "ZU_F",
    ]

    if zonos_kodas in palankios_zonos:
        return "palanku"
    elif zonos_kodas in nepalankios_zonos:
        return "nepalanku"
    else:
        return "ribota"


if __name__ == "__main__":
    bp_kelias = "01_duomenys/bp/bp_funkc.shp"
    sklypo_kelias = "03_eksportai/sklypas.gpkg"

    rezultatas = analizuoti_sklypa(bp_kelias, sklypo_kelias)

    if rezultatas["sekme"]:
        preliminari_klase = nustatyti_preliminaria_klase(rezultatas["zonos_kodas"])

        print("=== PRELIMINARUS VERTINIMAS ===")
        print(f"Zona: {rezultatas['zona_pavadinimas']}")
        print(f"Zonos kodas: {rezultatas['zonos_kodas']}")
        print(f"Užstatymo intensyvumas: {rezultatas['uzstatymo_intensyvumas']}")
        print(f"Maksimalus aukštų skaičius: {rezultatas['max_aukstu_skaicius']}")
        print(f"Pagrindinė paskirtis: {rezultatas['pagrindine_paskirtis']}")
        print(f"Preliminari klasė: {preliminari_klase}")
    else:
        print("=== KLAIDA ===")
        print(rezultatas["zinute"])