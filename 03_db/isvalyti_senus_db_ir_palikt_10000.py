from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_modeliai import SklypoAnalize


PROJEKTO_KATALOGAS = Path(__file__).resolve().parents[1]
DB_KELIAS = PROJEKTO_KATALOGAS / "03_db" / "baigiamasis.db"


def main():
    print("=== SENŲ DB ĮRAŠŲ IŠVALYMAS ===")
    print()

    engine = create_engine(f"sqlite:///{DB_KELIAS}")
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        visi_pries = session.query(SklypoAnalize).count()

        naujo_importo_kiekis = (
            session.query(SklypoAnalize)
            .filter(SklypoAnalize.duomenu_failas == "modelio_duomenys_10000.csv")
            .count()
        )

        senu_irasa_kiekis = (
            session.query(SklypoAnalize)
            .filter(SklypoAnalize.duomenu_failas != "modelio_duomenys_10000.csv")
            .count()
        )

        print(f"Visi DB įrašai prieš valymą: {visi_pries}")
        print(f"Naujo 10000 importo įrašai: {naujo_importo_kiekis}")
        print(f"Seni / kiti įrašai: {senu_irasa_kiekis}")
        print()

        istrinta = (
            session.query(SklypoAnalize)
            .filter(SklypoAnalize.duomenu_failas != "modelio_duomenys_10000.csv")
            .delete(synchronize_session=False)
        )

        session.commit()

        visi_po = session.query(SklypoAnalize).count()

        print("=== VALYMAS BAIGTAS ===")
        print(f"Ištrinta senų įrašų: {istrinta}")
        print(f"DB įrašų po valymo: {visi_po}")

    except Exception as klaida:
        session.rollback()
        raise klaida

    finally:
        session.close()


if __name__ == "__main__":
    main()