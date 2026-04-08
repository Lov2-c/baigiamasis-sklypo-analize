from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_modeliai import SklypoAnalize


def nustatyti_ukininko_sodybos_scenariju(irasas):
    """
    Nustato ūkininko sodybos scenarijaus būseną ir grąžina:
    1. statusą
    2. sąlygų tekstą

    Svarbi prielaida:
    laikome, kad 'plotas_reg' yra hektarais.
    """

    pagrindine_zona = (irasas.pagrindine_zona_pavadinimas or "").strip().lower()

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

    # 1. Jei tai ne žemės ūkio zona, ūkininko sodybos scenarijus netaikomas
    if yra_misku_zona or yra_pramones_zona or yra_gyvenamoji_zona or not yra_zemes_ukio_zona:
        return (
            "netaikoma",
            "Ūkininko sodybos scenarijus netaikomas, nes pagrindinė funkcinė zona nėra žemės ūkio teritorijų zona."
        )

    # 2. Jei per mažas plotas
    sklypo_plotas_ha = irasas.plotas_reg or 0

    if sklypo_plotas_ha < 2:
        return (
            "preliminariai_negalima",
            "Ūkininko sodybos scenarijus preliminariai negalimas, nes sklypo plotas mažesnis nei 2 ha."
        )

    # 3. Tikriname, ar yra saugomų / jautrių teritorijų
    yra_jautri_teritorija = any([
        (irasas.draustiniu_proc or 0) > 0,
        (irasas.rezervatu_proc or 0) > 0,
        (irasas.parku_proc or 0) > 0,
        (irasas.biosferos_poligonu_proc or 0) > 0,
        (irasas.bast_proc or 0) > 0,
        (irasas.past_proc or 0) > 0,
        (irasas.pajurio_juostos_proc or 0) > 0,
        (irasas.buferiniu_apsaugos_zonu_proc or 0) > 0,
    ])

    bendra_salyga = (
        "Turi būti tenkinamas ūkininko statuso ir 3 metų pajamų iš žemės ūkio veiklos deklaravimo reikalavimas."
    )

    # 4. Jei yra jautri / saugoma teritorija
    if yra_jautri_teritorija:
        tekstas = (
            "Ūkininko sodybos scenarijus preliminariai galimas, tačiau taikomos papildomos sąlygos. "
            + bendra_salyga
            + " Sklypas patenka į saugomą arba jautrią teritoriją, todėl būtina tikrinti, ar ūkininko sodybos statyba leidžiama pagal teritorijų planavimo dokumentus."
        )

        if (irasas.bast_proc or 0) > 0 or (irasas.past_proc or 0) > 0:
            tekstas += " Taip pat gali būti aktualios papildomos Natura 2000 sąlygos."

        return "galima_su_papildomomis_salygomis", tekstas

    # 5. Jei bazinės sąlygos tenkinamos
    tekstas = (
        "Ūkininko sodybos scenarijus preliminariai galimas. "
        + bendra_salyga
    )

    return "preliminariai_galima", tekstas


def nustatyti_automatines_analizes_rezultata(irasas):
    """
    Funkcija pagal DB įrašo duomenis nustato:
    1. automatinės analizės rezultatą
    2. seną ūkininko sodybos lauką suderinamumui
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
    # 2. Nustatome zonos tipą pagal pavadinimą
    # ---------------------------------------------------------

    pagrindine_zona = (irasas.pagrindine_zona_pavadinimas or "").strip().lower()

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

    if yra_zemes_ukio_zona:
        rezultatas = "preliminariai_negalima"

        paaiskinimai.append("Pagrindinė zona yra žemės ūkio teritorijų zona")
        paaiskinimai.append("Nauja gyvenamoji statyba preliminariai negalima")
        paaiskinimai.append("Ūkininko sodybos scenarijus vertinamas atskirai")

        return rezultatas, "; ".join(paaiskinimai)

    if yra_misku_zona:
        rezultatas = "preliminariai_negalima"

        paaiskinimai.append("Pagrindinė zona yra miškų ir miškingų teritorijų zona")
        paaiskinimai.append("Nauja gyvenamoji statyba preliminariai negalima")

        return rezultatas, "; ".join(paaiskinimai)

    if yra_pramones_zona:
        rezultatas = "preliminariai_negalima"

        paaiskinimai.append("Pagrindinė zona yra pramonės ir sandėliavimo zona")
        paaiskinimai.append("Nauja gyvenamoji statyba preliminariai negalima")

        return rezultatas, "; ".join(paaiskinimai)

    if yra_gyvenamoji_zona:
        if yra_stipriu_ribojimu or yra_papildomu_ribojimu:
            rezultatas = "ribotai_galima"

            paaiskinimai.append("Pagrindinė zona yra gyvenamoji")
            paaiskinimai.append("Nustatyti papildomi arba stiprūs teritoriniai ribojimai")
            paaiskinimai.append("Būtina rankinė validacija pagal papildomus sluoksnius")

            return rezultatas, "; ".join(paaiskinimai)

        else:
            rezultatas = "galima_tiesiogiai"

            paaiskinimai.append("Pagrindinė zona yra gyvenamoji")
            paaiskinimai.append("Automatinėje analizėje reikšmingų ribojimų nenustatyta")
            paaiskinimai.append("Būtina rankinė validacija pagal papildomus sluoksnius")

            return rezultatas, "; ".join(paaiskinimai)

    rezultatas = "ribotai_galima"

    paaiskinimai.append("Nepavyko vienareikšmiškai nustatyti pagrindinės zonos logikos")
    paaiskinimai.append("Reikalinga papildoma rankinė peržiūra")

    return rezultatas, "; ".join(paaiskinimai)


def atnaujinti_automatines_analizes_rezultatus():
    """
    Funkcija paima visus DB įrašus ir kiekvienam užpildo:
    - automatines_analizes_rezultatas
    - ukininko_sodybos_isvestis
    - ukininko_sodybos_statusas
    - ukininko_sodybos_salygos
    - automatines_analizes_paaiskinimas
    """

    engine = create_engine("sqlite:///03_db/baigiamasis.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    visi_irasai = session.query(SklypoAnalize).all()

    for irasas in visi_irasai:
        rezultatas, paaiskinimas = nustatyti_automatines_analizes_rezultata(irasas)

        ukininko_statusas, ukininko_salygos = nustatyti_ukininko_sodybos_scenariju(irasas)

        irasas.automatines_analizes_rezultatas = rezultatas
        irasas.automatines_analizes_paaiskinimas = paaiskinimas

        # Seną lauką paliekame suderinamumui
        irasas.ukininko_sodybos_isvestis = ukininko_statusas

        # Nauji aiškesni laukai
        irasas.ukininko_sodybos_statusas = ukininko_statusas
        irasas.ukininko_sodybos_salygos = ukininko_salygos

        # Kol kas visiems paliekame, kad reikia rankinės validacijos
        irasas.reikia_rankines_validacijos = 1

    session.commit()
    session.close()

    print(f"Automatinės analizės rezultatai atnaujinti {len(visi_irasai)} įrašams.")


if __name__ == "__main__":
    atnaujinti_automatines_analizes_rezultatus()