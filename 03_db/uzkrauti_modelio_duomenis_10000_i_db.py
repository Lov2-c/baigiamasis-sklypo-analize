from pathlib import Path
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_modeliai import Base, SklypoAnalize


# ============================================================
# KONFIGŪRACIJA
# ============================================================

PROJEKTO_KATALOGAS = Path(__file__).resolve().parents[1]

DB_KELIAS = PROJEKTO_KATALOGAS / "03_db" / "baigiamasis.db"
CSV_KELIAS = PROJEKTO_KATALOGAS / "06_rezultatai" / "modelio_duomenys_10000.csv"


# ============================================================
# PAGALBINĖS FUNKCIJOS
# ============================================================

def normalizuoti_reiksme(reiksme):
    """
    Paverčia Pandas / NumPy reikšmes į paprastas Python reikšmes.
    Tuščias reikšmes paverčia į None.
    """
    if pd.isna(reiksme):
        return None

    # NumPy tipai -> Python tipai
    if hasattr(reiksme, "item"):
        try:
            return reiksme.item()
        except Exception:
            return reiksme

    return reiksme


def gauti_pirma_esama_reiksme(eilute: dict, galimi_laukai: list[str]):
    """
    Paima pirmą rastą reikšmę iš kelių galimų stulpelių pavadinimų.
    Tai naudinga, jei CSV stulpeliai tarp versijų kiek skiriasi.
    """
    for laukas in galimi_laukai:
        if laukas in eilute:
            return normalizuoti_reiksme(eilute.get(laukas))
    return None


def i_int_0_1(reiksme):
    """
    Loginėms / dvejetainėms reikšmėms.
    Jei reikšmė > 0, grąžina 1, kitaip 0.
    """
    if reiksme is None:
        return 0
    try:
        return 1 if float(reiksme) > 0 else 0
    except Exception:
        return 0


def nustatyti_zonu_kieki(pagrindine_zona_kodas, antra_zona_kodas, antra_zona_proc):
    """
    Jei yra antra zona ir jos procentas reikšmingas, laikome, kad zonų yra 2.
    Kitu atveju - 1.
    """
    if antra_zona_kodas is not None:
        try:
            if antra_zona_proc is not None and float(antra_zona_proc) > 0:
                return 2
        except Exception:
            return 2

    if pagrindine_zona_kodas is not None:
        return 1

    return 0


def suformuoti_db_duomenis_is_csv_eilutes(eilute: dict, duomenu_failo_pavadinimas: str):
    """
    Iš vienos CSV eilutės suformuoja žodyną,
    kuris atitinka lentelės sklypu_analizes laukus.
    """

    sklypo_id = gauti_pirma_esama_reiksme(eilute, ["SKLYPO_ID", "sklypo_id"])
    unik_id = gauti_pirma_esama_reiksme(eilute, ["UNIKAL_ID", "unik_id"])
    adresas = gauti_pirma_esama_reiksme(eilute, ["ADRESAS", "adresas"])
    pask_tip = gauti_pirma_esama_reiksme(eilute, ["PASK_TIP", "pask_tip"])
    plotas_reg = gauti_pirma_esama_reiksme(eilute, ["PLOTAS_REG", "plotas_reg"])
    sklypo_plotas_m2 = gauti_pirma_esama_reiksme(eilute, ["SKLYPO_PLOTAS_M2", "sklypo_plotas_m2"])

    pagrindine_zona_pavadinimas = gauti_pirma_esama_reiksme(
        eilute,
        ["PAGRINDINE_ZONA_PAV", "PAGRINDINE_ZONOS_PAV", "pagrindine_zona_pavadinimas"],
    )
    pagrindine_zona_kodas = gauti_pirma_esama_reiksme(
        eilute,
        ["PAGRINDINE_ZONOS_KODAS", "pagrindine_zona_kodas"],
    )
    pagrindine_zona_proc = gauti_pirma_esama_reiksme(
        eilute,
        ["PAGRINDINE_ZONOS_PROC", "pagrindine_zona_proc"],
    )
    pagrindine_u_intens = gauti_pirma_esama_reiksme(
        eilute,
        ["PAGRINDINE_U_INTENS", "U_INTENS", "pagrindine_u_intens"],
    )
    pagrindine_max_auk_sk = gauti_pirma_esama_reiksme(
        eilute,
        ["PAGRINDINE_MAX_AUK_SK", "MAX_AUK_SK", "pagrindine_max_auk_sk"],
    )
    pagrindine_pagr_pask = gauti_pirma_esama_reiksme(
        eilute,
        ["PAGRINDINE_PAGR_PASK", "PAGR_PASK", "pagrindine_pagr_pask"],
    )

    antra_zona_pavadinimas = gauti_pirma_esama_reiksme(
        eilute,
        ["ANTRA_ZONA_PAV", "ANTRA_ZONOS_PAV", "antra_zona_pavadinimas"],
    )
    antra_zona_kodas = gauti_pirma_esama_reiksme(
        eilute,
        ["ANTRA_ZONOS_KODAS", "antra_zona_kodas"],
    )
    antra_zona_proc = gauti_pirma_esama_reiksme(
        eilute,
        ["ANTRA_ZONOS_PROC", "antra_zona_proc"],
    )

    # Automatinės analizės išvada
    vystymo_target = gauti_pirma_esama_reiksme(
        eilute,
        ["vystymo_target", "automatines_analizes_rezultatas"],
    )

    # Erdviniai procentiniai požymiai
    draustiniu_proc = gauti_pirma_esama_reiksme(eilute, ["draustiniu_proc"])
    rezervatu_proc = gauti_pirma_esama_reiksme(eilute, ["rezervatu_proc"])
    parku_proc = gauti_pirma_esama_reiksme(eilute, ["parku_proc"])
    biosferos_poligonu_proc = gauti_pirma_esama_reiksme(eilute, ["biosferos_poligonu_proc"])
    bast_proc = gauti_pirma_esama_reiksme(eilute, ["bast_proc"])
    past_proc = gauti_pirma_esama_reiksme(eilute, ["past_proc"])
    pajurio_juostos_proc = gauti_pirma_esama_reiksme(eilute, ["pajurio_juostos_proc"])
    buferiniu_apsaugos_zonu_proc = gauti_pirma_esama_reiksme(eilute, ["buferiniu_apsaugos_zonu_proc"])
    misko_proc = gauti_pirma_esama_reiksme(eilute, ["misko_proc"])
    kvr_poligonu_proc = gauti_pirma_esama_reiksme(eilute, ["kvr_poligonu_proc"])
    kvr_apsaugos_zonu_proc = gauti_pirma_esama_reiksme(eilute, ["kvr_apsaugos_zonu_proc"])
    pelkiu_proc = gauti_pirma_esama_reiksme(eilute, ["pelkiu_proc"])
    saltinynu_proc = gauti_pirma_esama_reiksme(eilute, ["saltinynu_proc"])
    pievu_ganyklu_proc = gauti_pirma_esama_reiksme(eilute, ["pievu_ganyklu_proc"])
    drenazo_plotu_proc = gauti_pirma_esama_reiksme(eilute, ["drenazo_plotu_proc"])
    rinktuvu_apsaugos_zonu_proc = gauti_pirma_esama_reiksme(eilute, ["rinktuvu_apsaugos_zonu_proc"])
    gelezinkelio_ribojimo_zonos_proc = gauti_pirma_esama_reiksme(eilute, ["gelezinkelio_ribojimo_zonos_proc"])

    db_duomenys = {
        "sklypo_id": str(sklypo_id) if sklypo_id is not None else None,
        "unik_id": str(unik_id) if unik_id is not None else None,
        "adresas": adresas,
        "pask_tip": str(pask_tip) if pask_tip is not None else None,
        "plotas_reg": float(plotas_reg) if plotas_reg is not None else 0.0,
        "sklypo_plotas_m2": float(sklypo_plotas_m2) if sklypo_plotas_m2 is not None else 0.0,
        "duomenu_failas": duomenu_failo_pavadinimas,
        "zonu_kiekis": nustatyti_zonu_kieki(pagrindine_zona_kodas, antra_zona_kodas, antra_zona_proc),

        "pagrindine_zona_pavadinimas": pagrindine_zona_pavadinimas,
        "pagrindine_zona_kodas": pagrindine_zona_kodas,
        "pagrindine_zona_proc": float(pagrindine_zona_proc) if pagrindine_zona_proc is not None else 0.0,
        "pagrindine_u_intens": str(pagrindine_u_intens) if pagrindine_u_intens is not None else None,
        "pagrindine_max_auk_sk": str(pagrindine_max_auk_sk) if pagrindine_max_auk_sk is not None else None,
        "pagrindine_pagr_pask": str(pagrindine_pagr_pask) if pagrindine_pagr_pask is not None else None,

        "antra_zona_pavadinimas": antra_zona_pavadinimas,
        "antra_zona_kodas": antra_zona_kodas,
        "antra_zona_proc": float(antra_zona_proc) if antra_zona_proc is not None else 0.0,

        "ar_yra_gyvenamoji_zona": i_int_0_1(gauti_pirma_esama_reiksme(eilute, ["ar_gyvenamoji_zona"])),
        "ar_yra_zemes_ukio_zona": i_int_0_1(gauti_pirma_esama_reiksme(eilute, ["ar_zemes_ukio_zona"])),
        "ar_yra_misku_zona": i_int_0_1(gauti_pirma_esama_reiksme(eilute, ["ar_misku_zona"])),
        "ar_yra_pramones_zona": i_int_0_1(gauti_pirma_esama_reiksme(eilute, ["ar_pramones_zona"])),

        "draustiniu_proc": float(draustiniu_proc) if draustiniu_proc is not None else 0.0,
        "rezervatu_proc": float(rezervatu_proc) if rezervatu_proc is not None else 0.0,
        "parku_proc": float(parku_proc) if parku_proc is not None else 0.0,
        "biosferos_poligonu_proc": float(biosferos_poligonu_proc) if biosferos_poligonu_proc is not None else 0.0,
        "bast_proc": float(bast_proc) if bast_proc is not None else 0.0,
        "past_proc": float(past_proc) if past_proc is not None else 0.0,
        "pajurio_juostos_proc": float(pajurio_juostos_proc) if pajurio_juostos_proc is not None else 0.0,
        "buferiniu_apsaugos_zonu_proc": float(buferiniu_apsaugos_zonu_proc) if buferiniu_apsaugos_zonu_proc is not None else 0.0,

        "misko_proc": float(misko_proc) if misko_proc is not None else 0.0,
        "ar_yra_miskas_proc": i_int_0_1(misko_proc),

        "kvr_poligonu_proc": float(kvr_poligonu_proc) if kvr_poligonu_proc is not None else 0.0,
        "kvr_apsaugos_zonu_proc": float(kvr_apsaugos_zonu_proc) if kvr_apsaugos_zonu_proc is not None else 0.0,
        "ar_yra_kvr_poligonas": i_int_0_1(kvr_poligonu_proc),
        "ar_yra_kvr_apsaugos_zona": i_int_0_1(kvr_apsaugos_zonu_proc),

        "pelkiu_proc": float(pelkiu_proc) if pelkiu_proc is not None else 0.0,
        "saltinynu_proc": float(saltinynu_proc) if saltinynu_proc is not None else 0.0,
        "pievu_ganyklu_proc": float(pievu_ganyklu_proc) if pievu_ganyklu_proc is not None else 0.0,
        "ar_yra_pelke": i_int_0_1(pelkiu_proc),
        "ar_yra_saltinynas": i_int_0_1(saltinynu_proc),
        "ar_yra_pievos_ganyklos": i_int_0_1(pievu_ganyklu_proc),

        "drenazo_plotu_proc": float(drenazo_plotu_proc) if drenazo_plotu_proc is not None else 0.0,
        "rinktuvu_apsaugos_zonu_proc": float(rinktuvu_apsaugos_zonu_proc) if rinktuvu_apsaugos_zonu_proc is not None else 0.0,
        "ar_yra_drenazo_plotai": i_int_0_1(drenazo_plotu_proc),
        "ar_yra_rinktuvu_apsaugos_zona": i_int_0_1(rinktuvu_apsaugos_zonu_proc),

        "gelezinkelio_ribojimo_zonos_proc": float(gelezinkelio_ribojimo_zonos_proc) if gelezinkelio_ribojimo_zonos_proc is not None else 0.0,
        "ar_yra_gelezinkelio_ribojimo_zona": i_int_0_1(gelezinkelio_ribojimo_zonos_proc),

        "automatines_analizes_rezultatas": str(vystymo_target) if vystymo_target is not None else None,

        "reikia_rankines_validacijos": 1,
        "rankines_validacijos_statusas": "neatlikta",

        "pastabos": "Masinis importas iš modelio_duomenys_10000.csv",
        "analizes_laikas": datetime.utcnow(),
    }

    return db_duomenys


# ============================================================
# PAGRINDINĖ LOGIKA
# ============================================================

def main():
    print("=== MASINIS MODELIO DUOMENŲ IMPORTAS Į DB ===")
    print()

    if not DB_KELIAS.exists():
        raise FileNotFoundError(f"Nerastas DB failas: {DB_KELIAS}")

    if not CSV_KELIAS.exists():
        raise FileNotFoundError(f"Nerastas CSV failas: {CSV_KELIAS}")

    print(f"DB failas: {DB_KELIAS}")
    print(f"CSV failas: {CSV_KELIAS}")
    print()

    df = pd.read_csv(CSV_KELIAS)
    print(f"Nuskaityta CSV eilučių: {len(df)}")
    print(f"Nuskaityta CSV stulpelių: {len(df.columns)}")
    print()

    engine = create_engine(f"sqlite:///{DB_KELIAS}")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        esami_irasa = session.query(SklypoAnalize).all()
        esami_pagal_sklypo_id = {irasas.sklypo_id: irasas for irasas in esami_irasa}

        print(f"DB prieš importą turi įrašų: {len(esami_irasa)}")
        print()

        sukurta = 0
        atnaujinta = 0
        praleista = 0

        for _, eilute in df.iterrows():
            eilute_dict = eilute.to_dict()
            db_duomenys = suformuoti_db_duomenis_is_csv_eilutes(
                eilute_dict,
                duomenu_failo_pavadinimas=CSV_KELIAS.name,
            )

            sklypo_id = db_duomenys.get("sklypo_id")

            if not sklypo_id:
                praleista += 1
                continue

            esamas = esami_pagal_sklypo_id.get(sklypo_id)

            if esamas is None:
                naujas = SklypoAnalize(**db_duomenys)
                session.add(naujas)
                sukurta += 1
            else:
                for laukas, reiksme in db_duomenys.items():
                    setattr(esamas, laukas, reiksme)
                atnaujinta += 1

        session.commit()

        galutinis_kiekis = session.query(SklypoAnalize).count()

        print("=== IMPORTAS BAIGTAS ===")
        print(f"Sukurta naujų įrašų: {sukurta}")
        print(f"Atnaujinta esamų įrašų: {atnaujinta}")
        print(f"Praleista eilučių be sklypo_id: {praleista}")
        print(f"DB po importo turi įrašų: {galutinis_kiekis}")
        print()

        print("Pirmos 5 DB eilutės po importo:")
        pavyzdziai = (
            session.query(SklypoAnalize)
            .order_by(SklypoAnalize.id.asc())
            .limit(5)
            .all()
        )

        for irasas in pavyzdziai:
            print(
                irasas.id,
                irasas.sklypo_id,
                irasas.unik_id,
                irasas.pagrindine_zona_kodas,
                irasas.automatines_analizes_rezultatas,
            )

    except Exception as klaida:
        session.rollback()
        raise klaida

    finally:
        session.close()


if __name__ == "__main__":
    main()