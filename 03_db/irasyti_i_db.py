from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_modeliai import Base, SklypoAnalize
from pathlib import Path
import sys

# -------------------------------------------------
# Pridedame 04_python/kodai aplanką prie importų kelio
# -------------------------------------------------
projekto_saknis = Path(__file__).resolve().parent.parent
kodai_aplankas = projekto_saknis / "04_python" / "kodai"

if str(kodai_aplankas) not in sys.path:
    sys.path.append(str(kodai_aplankas))

from features_ruosimas import paruosti_features


def irasyti_analize_i_db(bp_kelias, sklypo_kelias):
    """
    Ši funkcija:
    1. paruošia features lentelę
    2. paima pirmą eilutę
    3. įrašo ją į duomenų bazę
    """

    # Paruošiame features
    df, klaida = paruosti_features(bp_kelias, sklypo_kelias)

    if klaida:
        print("Klaida ruošiant features:")
        print(klaida)
        return

    # Sukuriame ryšį su duomenų baze
    engine = create_engine("sqlite:///03_db/baigiamasis.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Paimame pirmą eilutę iš DataFrame
    eilute = df.iloc[0]

    # Sukuriame naują objektą pagal DB modelį
    naujas_irasyas = SklypoAnalize(
        zona_pavadinimas=str(eilute["zona_pavadinimas"]),
        zonos_kodas=str(eilute["zonos_kodas"]),
        uzstatymo_intensyvumas=str(eilute["uzstatymo_intensyvumas"]),
        max_aukstu_skaicius=str(eilute["max_aukstu_skaicius"]),
        pagrindine_paskirtis=str(eilute["pagrindine_paskirtis"]),
        objekto_nr=str(eilute["objekto_nr"]),
        preliminari_klase=str(eilute["preliminari_klase"])
    )

    # Įrašome į DB
    session.add(naujas_irasyas)
    session.commit()

    print("Analizės rezultatas sėkmingai įrašytas į DB.")

    # Uždarome sesiją
    session.close()


if __name__ == "__main__":
    bp_kelias = "01_duomenys/bp/bp_funkc.shp"
    sklypo_kelias = "03_eksportai/sklypas.gpkg"

    irasyti_analize_i_db(bp_kelias, sklypo_kelias)