from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_modeliai import SklypoAnalize


def nuskaityti_visus_irasus():
    """
    Funkcija prisijungia prie DB ir parodo visus įrašus
    kartu su automatinės analizės rezultatais.
    """

    engine = create_engine("sqlite:///03_db/baigiamasis.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    visi_irasai = session.query(SklypoAnalize).all()

    print(f"Iš viso DB rasta įrašų: {len(visi_irasai)}")
    print("-" * 100)

    for irasas in visi_irasai:
        print(f"ID: {irasas.id}")
        print(f"Sklypo ID: {irasas.sklypo_id}")
        print(f"Adresas: {irasas.adresas}")
        print(f"Pagrindinė zona: {irasas.pagrindine_zona_pavadinimas}")
        print(f"Zona gyvenamoji: {irasas.ar_yra_gyvenamoji_zona}")
        print(f"Draustinių proc.: {irasas.draustiniu_proc}")
        print(f"Miško proc.: {irasas.misko_proc}")
        print(f"Automatinės analizės rezultatas: {irasas.automatines_analizes_rezultatas}")
        print(f"Ūkininko sodybos išvestis: {irasas.ukininko_sodybos_isvestis}")
        print(f"Automatinės analizės paaiškinimas: {irasas.automatines_analizes_paaiskinimas}")
        print(f"Rankinės validacijos būsena: {irasas.rankines_validacijos_statusas}")
        print("-" * 100)

    session.close()


if __name__ == "__main__":
    nuskaityti_visus_irasus()