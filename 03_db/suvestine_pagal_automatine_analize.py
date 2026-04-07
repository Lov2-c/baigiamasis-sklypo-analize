from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_modeliai import SklypoAnalize


def parodyti_suvestine():
    engine = create_engine("sqlite:///03_db/baigiamasis.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    visi_irasai = session.query(SklypoAnalize).all()

    kiek_galima_tiesiogiai = 0
    kiek_ribotai_galima = 0
    kiek_preliminariai_negalima = 0
    kiek_ukininko_sodyba = 0

    for irasas in visi_irasai:
        if irasas.automatines_analizes_rezultatas == "galima_tiesiogiai":
            kiek_galima_tiesiogiai += 1

        elif irasas.automatines_analizes_rezultatas == "ribotai_galima":
            kiek_ribotai_galima += 1

        elif irasas.automatines_analizes_rezultatas == "preliminariai_negalima":
            kiek_preliminariai_negalima += 1

        if irasas.ukininko_sodybos_isvestis == "reikia_tikrinti_tpd":
            kiek_ukininko_sodyba += 1

    print("AUTOMATINĖS ANALIZĖS SUVESTINĖ")
    print("-" * 50)
    print(f"Galima tiesiogiai: {kiek_galima_tiesiogiai}")
    print(f"Ribotai galima: {kiek_ribotai_galima}")
    print(f"Preliminariai negalima: {kiek_preliminariai_negalima}")
    print(f"Ūkininko sodybos scenarijus (reikia tikrinti TPD): {kiek_ukininko_sodyba}")
    print(f"Iš viso įrašų: {len(visi_irasai)}")

    session.close()


if __name__ == "__main__":
    parodyti_suvestine()