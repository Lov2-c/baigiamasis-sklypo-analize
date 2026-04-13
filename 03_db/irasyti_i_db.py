from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from datetime import datetime
import pandas as pd

from db_modeliai import SklypoAnalize
from atnaujinti_automatines_analizes_rezultatus import (
    nustatyti_automatines_analizes_rezultata,
    nustatyti_ukininko_sodybos_scenariju,
)


def saugi_reiksme(reiksme, numatyta_reiksme=None):
    """
    Pagalbinė funkcija:
    jei reikšmė yra NaN, grąžina numatytą reikšmę.
    """
    if pd.isna(reiksme):
        return numatyta_reiksme
    return reiksme


def sutvarkyti_reiksme_pries_db(reiksme):
    """
    Sutvarko reikšmę prieš įrašant į DB:
    - NaN paverčia į None
    - numpy tipo reikšmes paverčia į paprastas Python reikšmes
    """
    try:
        if pd.isna(reiksme):
            return None
    except Exception:
        pass

    if hasattr(reiksme, "item"):
        try:
            return reiksme.item()
        except Exception:
            return reiksme

    return reiksme


def suformuoti_db_url(db_kelias: str) -> str:
    """
    Iš failo kelio suformuoja SQLAlchemy tinkamą SQLite URL.
    Tai saugesnis variantas, ypač Windows aplinkoje.
    """
    return f"sqlite:///{Path(db_kelias).resolve().as_posix()}"


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
            # -------------------------------------------------
            automatines_analizes_rezultatas=None,
            ukininko_sodybos_isvestis=None,
            ukininko_sodybos_statusas=None,
            ukininko_sodybos_salygos=None,
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


def issaugoti_ar_atnaujinti_analize_db(
    db_kelias: str,
    sklypo_id: str,
    rezultato_dict: dict,
    atviro_sklypo_info: dict | None = None,
    atviro_sklypo_atributai: dict | None = None,
    saltinis: str | None = None,
    sklypo_plotas_m2: float | None = None,
):
    """
    Ši funkcija skirta UI workflow:

    1. pagal sklypo_id ieško esamo įrašo
    2. jei įrašas yra -> atnaujina
    3. jei įrašo nėra -> sukuria naują
    4. užpildo laukus iš analizės rezultato
    5. perskaičiuoja automatinės analizės išvadinius laukus
    6. grąžina išsaugoto įrašo dict
    """

    atviro_sklypo_info = atviro_sklypo_info or {}
    atviro_sklypo_atributai = atviro_sklypo_atributai or {}
    rezultato_dict = rezultato_dict or {}

    if not sklypo_id or not str(sklypo_id).strip():
        return {
            "sekme": False,
            "zinute": "Negautas sklypo_id išsaugojimui į DB.",
        }

    engine = create_engine(suformuoti_db_url(db_kelias))
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        sklypo_id_text = str(sklypo_id).strip()
        atviru_unikalus_nr = atviro_sklypo_info.get("atviru_unikalus_nr")
        atviru_kadastro_nr = atviro_sklypo_info.get("atviru_kadastro_nr")

        # 1. Pirmiausia bandome rasti pagal sklypo_id
        irasas = (
            session.query(SklypoAnalize)
            .filter(SklypoAnalize.sklypo_id == sklypo_id_text)
            .first()
        )

        # 2. Jei neradome, bandome rasti pagal unik_id
        if irasas is None and atviru_unikalus_nr:
            irasas = (
                session.query(SklypoAnalize)
                .filter(SklypoAnalize.unik_id == str(atviru_unikalus_nr))
                .first()
            )

        # 3. Jei vis tiek neradome ir turime kadastro numerį, pabandome pagal sklypo_id
        if irasas is None and atviru_kadastro_nr:
            irasas = (
                session.query(SklypoAnalize)
                .filter(SklypoAnalize.sklypo_id == str(atviru_kadastro_nr))
                .first()
            )

        ar_naujas_irasas = irasas is None

        if ar_naujas_irasas:
            irasas = SklypoAnalize(sklypo_id=sklypo_id_text)
            session.add(irasas)
        else:
            # Jei radome seną įrašą kitu identifikatoriumi,
            # perrašome jį į dabartinį sklypo_id
            irasas.sklypo_id = sklypo_id_text

        # Visi DB modelio laukai
        modelio_laukai = {stulpelis.name for stulpelis in SklypoAnalize.__table__.columns}

        # Šių laukų nenorime aklai perrašyti iš rezultato_dict
        saugomi_laukai = {
            "id",
            "sklypo_id",
            "analizes_laikas",
            "reikia_rankines_validacijos",
            "rankines_validacijos_statusas",
            "galutinis_validuotas_rezultatas",
            "validacijos_pastabos",
            "pastabos",
        }

        # ---------------------------------------------------------
        # 1. Užpildome DB laukus iš analizės rezultato
        # ---------------------------------------------------------
        for laukas, reiksme in rezultato_dict.items():
            if laukas in modelio_laukai and laukas not in saugomi_laukai:
                setattr(irasas, laukas, sutvarkyti_reiksme_pries_db(reiksme))

        # ---------------------------------------------------------
        # 2. Papildome identifikacinius / UI kilmės laukus
        # ---------------------------------------------------------
        if atviru_unikalus_nr:
            irasas.unik_id = str(atviru_unikalus_nr)

        pask_tipas = atviro_sklypo_atributai.get("pask_tipas")
        if pask_tipas is not None:
            irasas.pask_tip = str(pask_tipas)

        plotas_ha = sutvarkyti_reiksme_pries_db(atviro_sklypo_atributai.get("skl_plotas"))
        if plotas_ha is not None:
            irasas.plotas_reg = float(plotas_ha)

        if sklypo_plotas_m2 is not None:
            irasas.sklypo_plotas_m2 = float(sklypo_plotas_m2)

        if saltinis:
            irasas.duomenu_failas = str(saltinis)

        # Kiekvieną kartą atnaujiname analizės laiką
        irasas.analizes_laikas = datetime.utcnow()

        # Jei įrašas naujas – nustatome bazines validacijos reikšmes
        if ar_naujas_irasas:
            irasas.reikia_rankines_validacijos = 1
            if not irasas.rankines_validacijos_statusas:
                irasas.rankines_validacijos_statusas = "neatlikta"

        # ---------------------------------------------------------
        # 3. Perskaičiuojame išvadinius laukus pagal jau esamą logiką
        # ---------------------------------------------------------
        automatines_rezultatas, paaiskinimas = nustatyti_automatines_analizes_rezultata(irasas)
        ukininko_statusas, ukininko_salygos = nustatyti_ukininko_sodybos_scenariju(irasas)

        irasas.automatines_analizes_rezultatas = automatines_rezultatas
        irasas.automatines_analizes_paaiskinimas = paaiskinimas

        # Senasis laukas paliekamas suderinamumui
        irasas.ukininko_sodybos_isvestis = ukininko_statusas

        # Nauji laukai
        irasas.ukininko_sodybos_statusas = ukininko_statusas
        irasas.ukininko_sodybos_salygos = ukininko_salygos

        # ---------------------------------------------------------
        # 4. Išsaugome
        # ---------------------------------------------------------
        session.commit()
        session.refresh(irasas)

        issaugoto_irazo_dict = {
            stulpelis.name: getattr(irasas, stulpelis.name)
            for stulpelis in SklypoAnalize.__table__.columns
        }

        return {
            "sekme": True,
            "veiksmas": "sukurta" if ar_naujas_irasas else "atnaujinta",
            "irasas_dict": issaugoto_irazo_dict,
        }

    except Exception as klaida:
        session.rollback()
        return {
            "sekme": False,
            "zinute": f"Nepavyko išsaugoti analizės į DB: {klaida}",
        }

    finally:
        session.close()


if __name__ == "__main__":
    csv_kelias = "06_rezultatai/mini_dataset_bp_50_galutinis_plus_gelezinkelis.csv"
    irasyti_csv_i_db(csv_kelias)