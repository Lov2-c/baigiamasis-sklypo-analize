from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base

# Sukuriame bazinę klasę, nuo kurios paveldės mūsų lentelės
Base = declarative_base()


class SklypoAnalize(Base):
    """
    Ši klasė aprašo lentelę, kurioje saugosime
    sklypo analizės rezultatus.
    """

    __tablename__ = "sklypo_analizes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    zona_pavadinimas = Column(String(255))
    zonos_kodas = Column(String(100))
    uzstatymo_intensyvumas = Column(String(50))
    max_aukstu_skaicius = Column(String(50))
    pagrindine_paskirtis = Column(String(100))
    objekto_nr = Column(String(50))
    preliminari_klase = Column(String(50))


if __name__ == "__main__":
    # Sukuriame ryšį su SQLite duomenų baze
    engine = create_engine("sqlite:///03_db/baigiamasis.db")

    # Sukuriame visas lenteles, jei jų dar nėra
    Base.metadata.create_all(engine)

    print("Duomenų bazė ir lentelės sukurtos sėkmingai.")