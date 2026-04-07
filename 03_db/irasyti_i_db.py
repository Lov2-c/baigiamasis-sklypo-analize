from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import pandas as pd
import math

from db_modeliai import SklypoAnalize


def saugi_reiksme(reiksme, numatyta_reiksme=None):
    """
    Pagalbinė funkcija:
    jei reikšmė yra NaN, grąžina numatytą reikšmę.
    """
    if pd.isna(reiksme):
        return numatyta_reiksme
    return reiksme


def irasyti_csv_i_db(csv_kelias):
    """
    Ši funkcija:
    1. nuskaito galutinį CSV failą
    2. pereina per visas eilutes
    3. įrašo jas į SQLite duomenų bazę
    """

    # Nuskaitome CSV
    df = pd.read_csv(csv_kelias)

    # Prisijungiame prie duomenų bazės
    engine = create_engine("sqlite:///03_db/baigiamasis.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Kad neatsirastų dubliavimo, prieš naują įkėlimą ištriname senus įrašus
    session.query(SklypoAnalize).delete()
    session.commit()

    # Einame per visas CSV eilutes
    for _, eilute in df.iterrows():
        naujas_irasas = SklypoAnalize(
            # -------------------------------------------------
            # 1. Identifikaciniai laukai
            # -------------------------------------------------
            sklypo_id=str(saugi_reiksme(eilute.get("SKLYPO_ID"), "")),
            unik_id=str(saugi_reiksme(eilute.get("UNIKAL_ID"), "")),
            adresas=str(saugi_reiksme(eilute.get("ADRESAS"), "")),
            pask_tip=str(saugi_reiksme(eilute.get("PASK_TIP"), "")),
            plotas_reg=float(saugi_reiksme(eilute.get("PLOTAS_REG"), 0.0)),
            sklypo_plotas_m2=float(saugi_reiksme(eilute.get("SKLYPO_PLOTAS_M2"), 0.0)),
            duomenu_failas=str(csv_kelias),

            # -------------------------------------------------
            # 2. BP / TPD informacija
            # -------------------------------------------------
            zonu_kiekis=int(saugi_reiksme(eilute.get("zonu_kiekis"), 0)),

            pagrindine_zona_pavadinimas=str(saugi_reiksme(eilute.get("pagrindine_zona_pavadinimas"), "")),
            pagrindine_zona_kodas=str(saugi_reiksme(eilute.get("pagrindine_zona_kodas"), "")),
            pagrindine_zona_proc=float(saugi_reiksme(eilute.get("pagrindine_zona_proc"), 0.0)),
            pagrindine_u_intens=str(saugi_reiksme(eilute.get("pagrindine_u_intens"), "")),
            pagrindine_max_auk_sk=str(saugi_reiksme(eilute.get("pagrindine_max_auk_sk"), "")),
            pagrindine_pagr_pask=str(saugi_reiksme(eilute.get("pagrindine_pagr_pask"), "")),

            antra_zona_pavadinimas=str(saugi_reiksme(eilute.get("antra_zona_pavadinimas"), "")),
            antra_zona_kodas=str(saugi_reiksme(eilute.get("antra_zona_kodas"), "")),
            antra_zona_proc=float(saugi_reiksme(eilute.get("antra_zona_proc"), 0.0)),

            ar_yra_gyvenamoji_zona=int(saugi_reiksme(eilute.get("ar_yra_gyvenamoji_zona"), 0)),
            ar_yra_zemes_ukio_zona=int(saugi_reiksme(eilute.get("ar_yra_zemes_ukio_zona"), 0)),
            ar_yra_misku_zona=int(saugi_reiksme(eilute.get("ar_yra_misku_zona"), 0)),
            ar_yra_pramones_zona=int(saugi_reiksme(eilute.get("ar_yra_pramones_zona"), 0)),

            # -------------------------------------------------
            # 3. GIS požymiai
            # -------------------------------------------------
            draustiniu_proc=float(saugi_reiksme(eilute.get("draustiniu_proc"), 0.0)),
            rezervatu_proc=float(saugi_reiksme(eilute.get("rezervatu_proc"), 0.0)),
            parku_proc=float(saugi_reiksme(eilute.get("parku_proc"), 0.0)),
            biosferos_poligonu_proc=float(saugi_reiksme(eilute.get("biosferos_poligonu_proc"), 0.0)),
            bast_proc=float(saugi_reiksme(eilute.get("bast_proc"), 0.0)),
            past_proc=float(saugi_reiksme(eilute.get("past_proc"), 0.0)),
            pajurio_juostos_proc=float(saugi_reiksme(eilute.get("pajurio_juostos_proc"), 0.0)),
            buferiniu_apsaugos_zonu_proc=float(saugi_reiksme(eilute.get("buferiniu_apsaugos_zonu_proc"), 0.0)),

            misko_proc=float(saugi_reiksme(eilute.get("misko_proc"), 0.0)),
            ar_yra_miskas_proc=int(saugi_reiksme(eilute.get("ar_yra_miskas_proc"), 0)),

            kvr_poligonu_proc=float(saugi_reiksme(eilute.get("kvr_poligonu_proc"), 0.0)),
            kvr_apsaugos_zonu_proc=float(saugi_reiksme(eilute.get("kvr_apsaugos_zonu_proc"), 0.0)),
            ar_yra_kvr_poligonas=int(saugi_reiksme(eilute.get("ar_yra_kvr_poligonas"), 0)),
            ar_yra_kvr_apsaugos_zona=int(saugi_reiksme(eilute.get("ar_yra_kvr_apsaugos_zona"), 0)),

            pelkiu_proc=float(saugi_reiksme(eilute.get("pelkiu_proc"), 0.0)),
            saltinynu_proc=float(saugi_reiksme(eilute.get("saltinynu_proc"), 0.0)),
            pievu_ganyklu_proc=float(saugi_reiksme(eilute.get("pievu_ganyklu_proc"), 0.0)),
            ar_yra_pelke=int(saugi_reiksme(eilute.get("ar_yra_pelke"), 0)),
            ar_yra_saltinynas=int(saugi_reiksme(eilute.get("ar_yra_saltinynas"), 0)),
            ar_yra_pievos_ganyklos=int(saugi_reiksme(eilute.get("ar_yra_pievos_ganyklos"), 0)),

            drenazo_plotu_proc=float(saugi_reiksme(eilute.get("drenazo_plotu_proc"), 0.0)),
            rinktuvu_apsaugos_zonu_proc=float(saugi_reiksme(eilute.get("rinktuvu_apsaugos_zonu_proc"), 0.0)),
            ar_yra_drenazo_plotai=int(saugi_reiksme(eilute.get("ar_yra_drenazo_plotai"), 0)),
            ar_yra_rinktuvu_apsaugos_zona=int(saugi_reiksme(eilute.get("ar_yra_rinktuvu_apsaugos_zona"), 0)),

            gelezinkelio_ribojimo_zonos_proc=float(saugi_reiksme(eilute.get("gelezinkelio_ribojimo_zonos_proc"), 0.0)),
            ar_yra_gelezinkelio_ribojimo_zona=int(saugi_reiksme(eilute.get("ar_yra_gelezinkelio_ribojimo_zona"), 0)),

            # -------------------------------------------------
            # 4. Automatinės analizės laukai
            # Kol kas dar neužpildome galutinės logikos
            # -------------------------------------------------
            automatines_analizes_rezultatas=None,
            ukininko_sodybos_isvestis=None,
            automatines_analizes_paaiskinimas=None,

            # -------------------------------------------------
            # 5. Rankinė validacija
            # -------------------------------------------------
            reikia_rankines_validacijos=1,
            rankines_validacijos_statusas="neatlikta",
            galutinis_validuotas_rezultatas=None,
            validacijos_pastabos=None,

            # -------------------------------------------------
            # 6. Bendros pastabos
            # -------------------------------------------------
            pastabos=None
        )

        session.add(naujas_irasas)

    # Išsaugome visus įrašus
    session.commit()
    session.close()

    print(f"Į DB sėkmingai įrašyta {len(df)} įrašų.")


if __name__ == "__main__":
    csv_kelias = "06_rezultatai/mini_dataset_bp_50_galutinis_plus_gelezinkelis.csv"
    irasyti_csv_i_db(csv_kelias)