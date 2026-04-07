from sqlalchemy import create_engine
import pandas as pd


def paruosti_modelio_duomenis():
    """
    Funkcija:
    1. nuskaito duomenis iš SQLite DB
    2. atrenka tik modeliui reikalingus stulpelius
    3. išsaugo naują CSV failą modeliavimo etapui
    """

    # Prisijungiame prie SQLite DB
    engine = create_engine("sqlite:///03_db/baigiamasis.db")

    # Nuskaitome visą lentelę į pandas DataFrame
    df = pd.read_sql("SELECT * FROM sklypu_analizes", engine)

    # Pasirenkame tik tuos stulpelius, kuriuos naudosime modeliui
    modelio_stulpeliai = [
        "ar_yra_gyvenamoji_zona",
        "ar_yra_zemes_ukio_zona",
        "ar_yra_misku_zona",
        "ar_yra_pramones_zona",
        "zonu_kiekis",
        "pagrindine_zona_proc",
        "antra_zona_proc",
        "draustiniu_proc",
        "rezervatu_proc",
        "parku_proc",
        "biosferos_poligonu_proc",
        "bast_proc",
        "past_proc",
        "pajurio_juostos_proc",
        "buferiniu_apsaugos_zonu_proc",
        "misko_proc",
        "kvr_poligonu_proc",
        "kvr_apsaugos_zonu_proc",
        "pelkiu_proc",
        "saltinynu_proc",
        "pievu_ganyklu_proc",
        "rinktuvu_apsaugos_zonu_proc",
        "gelezinkelio_ribojimo_zonos_proc",
        "automatines_analizes_rezultatas"
    ]

    # Sukuriame naują DataFrame tik su pasirinktais stulpeliais
    df_modeliui = df[modelio_stulpeliai].copy()

    # Patikriname, ar nėra tuščių reikšmių
    # Jei yra, užpildome 0 skaitiniuose stulpeliuose
    skaitiniai_stulpeliai = [
        "ar_yra_gyvenamoji_zona",
        "ar_yra_zemes_ukio_zona",
        "ar_yra_misku_zona",
        "ar_yra_pramones_zona",
        "zonu_kiekis",
        "pagrindine_zona_proc",
        "antra_zona_proc",
        "draustiniu_proc",
        "rezervatu_proc",
        "parku_proc",
        "biosferos_poligonu_proc",
        "bast_proc",
        "past_proc",
        "pajurio_juostos_proc",
        "buferiniu_apsaugos_zonu_proc",
        "misko_proc",
        "kvr_poligonu_proc",
        "kvr_apsaugos_zonu_proc",
        "pelkiu_proc",
        "saltinynu_proc",
        "pievu_ganyklu_proc",
        "rinktuvu_apsaugos_zonu_proc",
        "gelezinkelio_ribojimo_zonos_proc"
    ]

    df_modeliui[skaitiniai_stulpeliai] = df_modeliui[skaitiniai_stulpeliai].fillna(0)

    # Išsaugome į naują CSV
    isvedimo_failas = "06_rezultatai/modelio_duomenys_is_db.csv"
    df_modeliui.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

    print("Modelio duomenų failas sėkmingai sukurtas.")
    print(f"Išsaugotas failas: {isvedimo_failas}")
    print(f"Eilučių skaičius: {len(df_modeliui)}")
    print(f"Stulpelių skaičius: {len(df_modeliui.columns)}")
    print("\nTarget klasių pasiskirstymas:")
    print(df_modeliui["automatines_analizes_rezultatas"].value_counts())


if __name__ == "__main__":
    paruosti_modelio_duomenis()