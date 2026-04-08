import pandas as pd


def apziureti_modelio_duomenis():
    """
    Funkcija nuskaito modeliui paruoštą CSV failą
    ir parodo pagrindinę jo informaciją.
    """

    # Nurodome failo kelią
    failo_kelias = "06_rezultatai/modelio_duomenys_is_db.csv"

    # Nuskaitome CSV failą
    df = pd.read_csv(failo_kelias, encoding="utf-8-sig")

    # --------------------------------------------
    # 1. Pagrindinė informacija
    # --------------------------------------------
    print("PIRMOS 5 EILUTĖS")
    print(df.head())
    print("\n" + "=" * 80)

    print("DATAFRAME MATMENYS")
    print(f"Eilučių skaičius: {df.shape[0]}")
    print(f"Stulpelių skaičius: {df.shape[1]}")
    print("\n" + "=" * 80)

    # --------------------------------------------
    # 2. Stulpelių sąrašas
    # --------------------------------------------
    print("STULPELIŲ SĄRAŠAS")
    for stulpelis in df.columns:
        print(stulpelis)
    print("\n" + "=" * 80)

    # --------------------------------------------
    # 3. Duomenų tipai
    # --------------------------------------------
    print("DUOMENŲ TIPAI")
    print(df.dtypes)
    print("\n" + "=" * 80)

    # --------------------------------------------
    # 4. Trūkstamos reikšmės
    # --------------------------------------------
    print("TRŪKSTAMOS REIKŠMĖS")
    print(df.isnull().sum())
    print("\n" + "=" * 80)

    # --------------------------------------------
    # 5. Target pasiskirstymas
    # --------------------------------------------
    print("TARGET KLASIŲ PASISKIRSTYMAS")
    print(df["automatines_analizes_rezultatas"].value_counts())
    print("\n" + "=" * 80)

    # --------------------------------------------
    # 6. Paprasta statistika skaitiniams laukams
    # --------------------------------------------
    print("SKAITINIŲ STULPELIŲ APRAŠOMOJI STATISTIKA")
    print(df.describe())
    print("\n" + "=" * 80)


if __name__ == "__main__":
    apziureti_modelio_duomenis()