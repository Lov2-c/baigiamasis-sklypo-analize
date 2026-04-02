from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_modeliai import SklypoAnalize


def nuskaityti_visas_analizes():
    """
    Ši funkcija prisijungia prie duomenų bazės
    ir nuskaito visus sklypų analizės įrašus.
    """

    # Prisijungiame prie SQLite duomenų bazės
    engine = create_engine("sqlite:///03_db/baigiamasis.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Pasiimame visus įrašus iš lentelės
    irasai = session.query(SklypoAnalize).all()

    # Jei įrašų nėra
    if not irasai:
        print("Duomenų bazėje įrašų nerasta.")
        session.close()
        return

    print("=== DUOMENŲ BAZĖS ĮRAŠAI ===")

    # Pereiname per visus įrašus ir juos atspausdiname
    for irasas in irasai:
        print(f"\nID: {irasas.id}")
        print(f"Zona: {irasas.zona_pavadinimas}")
        print(f"Zonos kodas: {irasas.zonos_kodas}")
        print(f"Užstatymo intensyvumas: {irasas.uzstatymo_intensyvumas}")
        print(f"Maksimalus aukštų skaičius: {irasas.max_aukstu_skaicius}")
        print(f"Pagrindinė paskirtis: {irasas.pagrindine_paskirtis}")
        print(f"Objekto nr.: {irasas.objekto_nr}")
        print(f"Preliminari klasė: {irasas.preliminari_klase}")

    session.close()


if __name__ == "__main__":
    nuskaityti_visas_analizes()