from sqlalchemy import create_engine, Column, Integer, Float, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

# Sukuriame bazinę klasę, nuo kurios paveldės mūsų lentelės
Base = declarative_base()


class SklypoAnalize(Base):
    """
    Ši klasė aprašo pagrindinę lentelę, kurioje saugosime:
    1. sklypo identifikaciją
    2. BP / TPD požymius
    3. automatinei analizei naudojamus GIS požymius
    4. automatinės analizės rezultatą
    5. rankinės validacijos rezultatą
    6. papildomas pastabas
    """

    __tablename__ = "sklypu_analizes"

    # ---------------------------------------------------------
    # 1. Identifikaciniai laukai
    # ---------------------------------------------------------

    id = Column(Integer, primary_key=True, autoincrement=True)

    sklypo_id = Column(String(50), nullable=False, index=True)
    unik_id = Column(String(50), nullable=True)
    adresas = Column(String(255), nullable=True)

    # Sklypo tipinė informacija
    pask_tip = Column(String(50), nullable=True)
    plotas_reg = Column(Float, default=0.0)
    sklypo_plotas_m2 = Column(Float, default=0.0)

    # Iš kokio failo įkelti duomenys
    duomenu_failas = Column(String(255), nullable=True)

    # ---------------------------------------------------------
    # 2. BP / TPD informacija
    # ---------------------------------------------------------

    zonu_kiekis = Column(Integer, default=0)

    pagrindine_zona_pavadinimas = Column(String(255), nullable=True)
    pagrindine_zona_kodas = Column(String(100), nullable=True)
    pagrindine_zona_proc = Column(Float, default=0.0)
    pagrindine_u_intens = Column(String(100), nullable=True)
    pagrindine_max_auk_sk = Column(String(50), nullable=True)
    pagrindine_pagr_pask = Column(String(100), nullable=True)

    antra_zona_pavadinimas = Column(String(255), nullable=True)
    antra_zona_kodas = Column(String(100), nullable=True)
    antra_zona_proc = Column(Float, default=0.0)

    # Pagalbiniai loginiai BP laukai
    ar_yra_gyvenamoji_zona = Column(Integer, default=0)
    ar_yra_zemes_ukio_zona = Column(Integer, default=0)
    ar_yra_misku_zona = Column(Integer, default=0)
    ar_yra_pramones_zona = Column(Integer, default=0)

    # ---------------------------------------------------------
    # 3. Automatinės analizės GIS požymiai
    # ---------------------------------------------------------

    # Saugomos teritorijos
    draustiniu_proc = Column(Float, default=0.0)
    rezervatu_proc = Column(Float, default=0.0)
    parku_proc = Column(Float, default=0.0)
    biosferos_poligonu_proc = Column(Float, default=0.0)
    bast_proc = Column(Float, default=0.0)
    past_proc = Column(Float, default=0.0)
    pajurio_juostos_proc = Column(Float, default=0.0)
    buferiniu_apsaugos_zonu_proc = Column(Float, default=0.0)

    # Miškai
    misko_proc = Column(Float, default=0.0)
    ar_yra_miskas_proc = Column(Integer, default=0)

    # Kultūros paveldas
    kvr_poligonu_proc = Column(Float, default=0.0)
    kvr_apsaugos_zonu_proc = Column(Float, default=0.0)
    ar_yra_kvr_poligonas = Column(Integer, default=0)
    ar_yra_kvr_apsaugos_zona = Column(Integer, default=0)

    # SŽNS / gamtiniai ribojimai, kurie jau įtraukti į automatinę analizę
    pelkiu_proc = Column(Float, default=0.0)
    saltinynu_proc = Column(Float, default=0.0)
    pievu_ganyklu_proc = Column(Float, default=0.0)
    ar_yra_pelke = Column(Integer, default=0)
    ar_yra_saltinynas = Column(Integer, default=0)
    ar_yra_pievos_ganyklos = Column(Integer, default=0)

    # Melioracija
    drenazo_plotu_proc = Column(Float, default=0.0)
    rinktuvu_apsaugos_zonu_proc = Column(Float, default=0.0)
    ar_yra_drenazo_plotai = Column(Integer, default=0)
    ar_yra_rinktuvu_apsaugos_zona = Column(Integer, default=0)

    # Geležinkelio ribojimo zona
    gelezinkelio_ribojimo_zonos_proc = Column(Float, default=0.0)
    ar_yra_gelezinkelio_ribojimo_zona = Column(Integer, default=0)

    # ---------------------------------------------------------
    # 4. Automatinės analizės išvada
    # ---------------------------------------------------------

    # Galimos reikšmės:
    # - galima_tiesiogiai
    # - ribotai_galima
    # - preliminariai_negalima
    automatines_analizes_rezultatas = Column(String(50), nullable=True)

    # Galimos reikšmės:
    # - netaikoma
    # - reikia_tikrinti_tpd
    ukininko_sodybos_isvestis = Column(String(50), nullable=True)

    # Paaiškinimas, kodėl priskirtas toks rezultatas
    automatines_analizes_paaiskinimas = Column(Text, nullable=True)

    # ---------------------------------------------------------
    # 5. Rankinė validacija
    # ---------------------------------------------------------

    # 1 = reikia, 0 = nereikia
    reikia_rankines_validacijos = Column(Integer, default=1)

    # Galimos reikšmės:
    # - neatlikta
    # - atlikta
    # - pakoreguota
    rankines_validacijos_statusas = Column(String(50), default="neatlikta")

    # Galimos reikšmės:
    # - galima_tiesiogiai
    # - ribotai_galima
    # - preliminariai_negalima
    galutinis_validuotas_rezultatas = Column(String(50), nullable=True)

    validacijos_pastabos = Column(Text, nullable=True)

    # ---------------------------------------------------------
    # 6. Bendros pastabos
    # ---------------------------------------------------------

    pastabos = Column(Text, nullable=True)

    analizes_laikas = Column(DateTime, default=datetime.utcnow)


if __name__ == "__main__":
    # Sukuriame ryšį su SQLite duomenų baze
    engine = create_engine("sqlite:///03_db/baigiamasis.db")

    # Sukuriame visas lenteles, jei jų dar nėra
    Base.metadata.create_all(engine)

    print("Duomenų bazė ir lentelės sukurtos sėkmingai.")