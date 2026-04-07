from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_modeliai import SklypoAnalize


def gauti_ribojimu_priezastis(irasas):
    """
    Grąžina sąrašą konkrečių ribojimų, kurie šiam įrašui yra > 0.
    """

    priezastys = []

    # Stiprūs ribojimai
    if (irasas.draustiniu_proc or 0) > 0:
        priezastys.append(f"draustiniu_proc={irasas.draustiniu_proc}")

    if (irasas.rezervatu_proc or 0) > 0:
        priezastys.append(f"rezervatu_proc={irasas.rezervatu_proc}")

    if (irasas.pajurio_juostos_proc or 0) > 0:
        priezastys.append(f"pajurio_juostos_proc={irasas.pajurio_juostos_proc}")

    if (irasas.kvr_poligonu_proc or 0) > 0:
        priezastys.append(f"kvr_poligonu_proc={irasas.kvr_poligonu_proc}")

    if (irasas.pelkiu_proc or 0) > 0:
        priezastys.append(f"pelkiu_proc={irasas.pelkiu_proc}")

    if (irasas.saltinynu_proc or 0) > 0:
        priezastys.append(f"saltinynu_proc={irasas.saltinynu_proc}")

    # Papildomi ribojimai
    if (irasas.misko_proc or 0) > 0:
        priezastys.append(f"misko_proc={irasas.misko_proc}")

    if (irasas.kvr_apsaugos_zonu_proc or 0) > 0:
        priezastys.append(f"kvr_apsaugos_zonu_proc={irasas.kvr_apsaugos_zonu_proc}")

    if (irasas.pievu_ganyklu_proc or 0) > 0:
        priezastys.append(f"pievu_ganyklu_proc={irasas.pievu_ganyklu_proc}")

    if (irasas.drenazo_plotu_proc or 0) > 0:
        priezastys.append(f"drenazo_plotu_proc={irasas.drenazo_plotu_proc}")

    if (irasas.rinktuvu_apsaugos_zonu_proc or 0) > 0:
        priezastys.append(f"rinktuvu_apsaugos_zonu_proc={irasas.rinktuvu_apsaugos_zonu_proc}")

    if (irasas.gelezinkelio_ribojimo_zonos_proc or 0) > 0:
        priezastys.append(f"gelezinkelio_ribojimo_zonos_proc={irasas.gelezinkelio_ribojimo_zonos_proc}")

    if (irasas.buferiniu_apsaugos_zonu_proc or 0) > 0:
        priezastys.append(f"buferiniu_apsaugos_zonu_proc={irasas.buferiniu_apsaugos_zonu_proc}")

    if (irasas.bast_proc or 0) > 0:
        priezastys.append(f"bast_proc={irasas.bast_proc}")

    if (irasas.past_proc or 0) > 0:
        priezastys.append(f"past_proc={irasas.past_proc}")

    if (irasas.biosferos_poligonu_proc or 0) > 0:
        priezastys.append(f"biosferos_poligonu_proc={irasas.biosferos_poligonu_proc}")

    if (irasas.parku_proc or 0) > 0:
        priezastys.append(f"parku_proc={irasas.parku_proc}")

    return priezastys


def tikrinti_ribotai_galimus():
    """
    Parodo tik tuos įrašus, kurie gavo 'ribotai_galima',
    ir išvardija konkrečias priežastis.
    """

    engine = create_engine("sqlite:///03_db/baigiamasis.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    irasai = (
        session.query(SklypoAnalize)
        .filter(SklypoAnalize.automatines_analizes_rezultatas == "ribotai_galima")
        .all()
    )

    print(f"Rasta 'ribotai_galima' įrašų: {len(irasai)}")
    print("-" * 120)

    for irasas in irasai:
        priezastys = gauti_ribojimu_priezastis(irasas)

        print(f"ID: {irasas.id}")
        print(f"Sklypo ID: {irasas.sklypo_id}")
        print(f"Adresas: {irasas.adresas}")
        print(f"Pagrindinė zona: {irasas.pagrindine_zona_pavadinimas}")
        print(f"Ribojimų priežastys: {', '.join(priezastys) if priezastys else 'Nerasta'}")
        print("-" * 120)

    session.close()


if __name__ == "__main__":
    tikrinti_ribotai_galimus()