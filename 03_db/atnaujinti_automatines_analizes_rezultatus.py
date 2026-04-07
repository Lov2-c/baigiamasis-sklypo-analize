from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_modeliai import SklypoAnalize


def nustatyti_automatines_analizes_rezultata(irasas):
    """
    Funkcija pagal DB įrašo duomenis nustato:
    1. automatinės analizės rezultatą
    2. ūkininko sodybos išvestį
    3. paaiškinimą tekstu
    """

    paaiskinimai = []

    # ---------------------------------------------------------
    # 1. Nustatome, ar yra ribojimų
    # ---------------------------------------------------------

    yra_stipriu_ribojimu = any([
        (irasas.draustiniu_proc or 0) > 0,
        (irasas.rezervatu_proc or 0) > 0,
        (irasas.pajurio_juostos_proc or 0) > 0,
        (irasas.kvr_poligonu_proc or 0) > 0,
        (irasas.pelkiu_proc or 0) > 0,
        (irasas.saltinynu_proc or 0) > 0,
    ])

    yra_papildomu_ribojimu = any([
        (irasas.kvr_apsaugos_zonu_proc or 0) > 0,
        (irasas.pievu_ganyklu_proc or 0) > 0,
        (irasas.rinktuvu_apsaugos_zonu_proc or 0) > 0,
        (irasas.gelezinkelio_ribojimo_zonos_proc or 0) > 0,
        (irasas.buferiniu_apsaugos_zonu_proc or 0) > 0,
        (irasas.bast_proc or 0) > 0,
        (irasas.past_proc or 0) > 0,
        (irasas.biosferos_poligonu_proc or 0) > 0,
        (irasas.parku_proc or 0) > 0,
    ])

    # ---------------------------------------------------------
    # 2. Nustatome zonos tipą
    # ---------------------------------------------------------

    pagrindine_zona = (irasas.pagrindine_zona_pavadinimas or "").strip().lower()

    # Zoną nustatome PIRMIAUSIA pagal patį zonos pavadinimą,
    # nes pagalbiniai loginiai laukai kai kuriose eilutėse yra netikslūs.

    yra_zemes_ukio_zona = (
        "žemės ūkio teritorijų zona" in pagrindine_zona
        or "zemes ukio teritoriju zona" in pagrindine_zona
    )

    yra_misku_zona = (
        "miškų ir miškingų teritorijų zona" in pagrindine_zona
        or "misku ir miskingu teritoriju zona" in pagrindine_zona
    )

    yra_pramones_zona = (
        "pramonės ir sandėliavimo zona" in pagrindine_zona
        or "pramones ir sandeliavimo zona" in pagrindine_zona
    )

    yra_gyvenamoji_zona = "gyvenamoji zona" in pagrindine_zona

    # ---------------------------------------------------------
    # 3. Pritaikome logiką
    # ---------------------------------------------------------

    # 3.1. Žemės ūkio zona
    if yra_zemes_ukio_zona:
        rezultatas = "preliminariai_negalima"
        ukininko_sodybos_isvestis = "reikia_tikrinti_tpd"

        paaiskinimai.append("Pagrindinė zona yra žemės ūkio teritorijų zona")
        paaiskinimai.append("Nauja gyvenamoji statyba preliminariai negalima")
        paaiskinimai.append("Galimas ūkininko sodybos scenarijus, reikia tikrinti TPD sąlygas")

        return rezultatas, ukininko_sodybos_isvestis, "; ".join(paaiskinimai)

    # 3.2. Miškų zona
    if yra_misku_zona:
        rezultatas = "preliminariai_negalima"
        ukininko_sodybos_isvestis = "netaikoma"

        paaiskinimai.append("Pagrindinė zona yra miškų ir miškingų teritorijų zona")
        paaiskinimai.append("Nauja gyvenamoji statyba preliminariai negalima")

        return rezultatas, ukininko_sodybos_isvestis, "; ".join(paaiskinimai)

    # 3.3. Pramonės zona
    if yra_pramones_zona:
        rezultatas = "preliminariai_negalima"
        ukininko_sodybos_isvestis = "netaikoma"

        paaiskinimai.append("Pagrindinė zona yra pramonės ir sandėliavimo zona")
        paaiskinimai.append("Nauja gyvenamoji statyba preliminariai negalima")

        return rezultatas, ukininko_sodybos_isvestis, "; ".join(paaiskinimai)

    # 3.4. Gyvenamoji zona
    if yra_gyvenamoji_zona:
        if yra_stipriu_ribojimu or yra_papildomu_ribojimu:
            rezultatas = "ribotai_galima"
            ukininko_sodybos_isvestis = "netaikoma"

            paaiskinimai.append("Pagrindinė zona yra gyvenamoji")
            paaiskinimai.append("Nustatyti papildomi arba stiprūs teritoriniai ribojimai")
            paaiskinimai.append("Būtina rankinė validacija pagal papildomus sluoksnius")

            return rezultatas, ukininko_sodybos_isvestis, "; ".join(paaiskinimai)

        else:
            rezultatas = "galima_tiesiogiai"
            ukininko_sodybos_isvestis = "netaikoma"

            paaiskinimai.append("Pagrindinė zona yra gyvenamoji")
            paaiskinimai.append("Automatinėje analizėje reikšmingų ribojimų nenustatyta")
            paaiskinimai.append("Būtina rankinė validacija pagal papildomus sluoksnius")

            return rezultatas, ukininko_sodybos_isvestis, "; ".join(paaiskinimai)

    # 3.5. Jei nepavyko aiškiai priskirti zonos
    rezultatas = "ribotai_galima"
    ukininko_sodybos_isvestis = "netaikoma"

    paaiskinimai.append("Nepavyko vienareikšmiškai nustatyti pagrindinės zonos logikos")
    paaiskinimai.append("Reikalinga papildoma rankinė peržiūra")

    return rezultatas, ukininko_sodybos_isvestis, "; ".join(paaiskinimai)


def atnaujinti_automatines_analizes_rezultatus():
    """
    Funkcija paima visus DB įrašus ir kiekvienam užpildo:
    - automatines_analizes_rezultatas
    - ukininko_sodybos_isvestis
    - automatines_analizes_paaiskinimas
    """

    engine = create_engine("sqlite:///03_db/baigiamasis.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    visi_irasai = session.query(SklypoAnalize).all()

    for irasas in visi_irasai:
        rezultatas, ukininko_isvestis, paaiskinimas = nustatyti_automatines_analizes_rezultata(irasas)

        irasas.automatines_analizes_rezultatas = rezultatas
        irasas.ukininko_sodybos_isvestis = ukininko_isvestis
        irasas.automatines_analizes_paaiskinimas = paaiskinimas

        # Kol kas visiems paliekame, kad reikia rankinės validacijos
        irasas.reikia_rankines_validacijos = 1

    session.commit()
    session.close()

    print(f"Automatinės analizės rezultatai atnaujinti {len(visi_irasai)} įrašams.")


if __name__ == "__main__":
    atnaujinti_automatines_analizes_rezultatus()