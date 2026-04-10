from pathlib import Path

PROJEKTO_KATALOGAS = Path(__file__).resolve().parents[1]

DB_FAILO_KELIAS = PROJEKTO_KATALOGAS / "03_db" / "baigiamasis.db"
PAGRINDINE_LENTELE = "sklypu_analizes"

ATVIRU_SKLYPU_ZIP = PROJEKTO_KATALOGAS / "01_duomenys" / "atviri_sklypai" / "klaipedos_rajono_sklypai.zip"
SUSIEJIMO_CSV = PROJEKTO_KATALOGAS / "06_rezultatai" / "sklypu_susiejimas_2019_su_atvirais_patvirtintas.csv"

RC_WMS_URL = "https://www.geoportal.lt/mapproxy/rc_kadastro_zemelapis/MapServer/WMSServer"
RC_WMS_LAYERS = "15,21,27,33"

PRADINIS_ZEMELAPIO_LAT = 55.71
PRADINIS_ZEMELAPIO_LON = 21.39
PRADINIS_ZOOM = 13

ZEMELAPIO_PLOTIS = 1150
ZEMELAPIO_AUKSTIS = 650
ARTIMU_SKLYPU_ATSTUMAS_M = 200

SVARBIAUSI_DB_LAUKAI = [
    "sklypo_id",
    "unik_id",
    "adresas",
    "pask_tip",
    "plotas_reg",
    "sklypo_plotas_m2",
    "pagrindine_zona_pavadinimas",
    "pagrindine_zona_kodas",
    "pagrindine_zona_proc",
    "pagrindine_u_intens",
    "pagrindine_max_auk_sk",
    "pagrindine_pagr_pask",
    "automatines_analizes_rezultatas",
    "automatines_analizes_paaiskinimas",
    "ukininko_sodybos_statusas",
    "ukininko_sodybos_salygos",
    "reikia_rankines_validacijos",
    "rankines_validacijos_statusas",
    "galutinis_validuotas_rezultatas",
    "validacijos_pastabos",
]

RIBOJIMU_LAUKAI = [
    "draustiniu_proc",
    "rezervatu_proc",
    "parku_proc",
    "biosferos_poligonu_proc",
    "bast_proc",
    "past_proc",
    "pajurio_juostos_proc",
    "buferiniu_apsaugos_zonu_proc",
    "misko_proc",
    "kvr_poligonu_proc",
    "kvr_apsaugos_zonu_proc",
    "pelkiu_proc",
    "saltinynu_proc",
    "pievu_ganyklu_proc",
    "drenazo_plotu_proc",
    "rinktuvu_apsaugos_zonu_proc",
    "gelezinkelio_ribojimo_zonos_proc",
]

LAUKU_PAVADINIMAI = {
    "sklypo_id": "Sklypo ID",
    "unik_id": "Unikalus numeris",
    "adresas": "Adresas",
    "pask_tip": "Paskirties tipas",
    "plotas_reg": "Plotas pagal registrą, ha",
    "sklypo_plotas_m2": "Sklypo plotas, m²",
    "pagrindine_zona_pavadinimas": "Pagrindinė BP zona",
    "pagrindine_zona_kodas": "Pagrindinės zonos kodas",
    "pagrindine_zona_proc": "Pagrindinės zonos dalis, %",
    "pagrindine_u_intens": "Užstatymo intensyvumas",
    "pagrindine_max_auk_sk": "Maksimalus aukštų skaičius",
    "pagrindine_pagr_pask": "Pagrindinė paskirtis",
    "automatines_analizes_rezultatas": "Automatinės analizės rezultatas",
    "automatines_analizes_paaiskinimas": "Automatinės analizės paaiškinimas",
    "ukininko_sodybos_statusas": "Ūkininko sodybos statusas",
    "ukininko_sodybos_salygos": "Ūkininko sodybos sąlygos",
    "reikia_rankines_validacijos": "Reikia rankinės validacijos",
    "rankines_validacijos_statusas": "Rankinės validacijos statusas",
    "galutinis_validuotas_rezultatas": "Galutinis validuotas rezultatas",
    "validacijos_pastabos": "Validacijos pastabos",
    "draustiniu_proc": "Draustinių plotas, %",
    "rezervatu_proc": "Rezervatų plotas, %",
    "parku_proc": "Parkų plotas, %",
    "biosferos_poligonu_proc": "Biosferos poligonų plotas, %",
    "bast_proc": "BAST plotas, %",
    "past_proc": "PAST plotas, %",
    "pajurio_juostos_proc": "Pajūrio juostos plotas, %",
    "buferiniu_apsaugos_zonu_proc": "Buferinių apsaugos zonų plotas, %",
    "misko_proc": "Miško plotas, %",
    "kvr_poligonu_proc": "KVR poligonų plotas, %",
    "kvr_apsaugos_zonu_proc": "KVR apsaugos zonų plotas, %",
    "pelkiu_proc": "Pelkų plotas, %",
    "saltinynu_proc": "Šaltinynų plotas, %",
    "pievu_ganyklu_proc": "Pievų ir ganyklų plotas, %",
    "drenazo_plotu_proc": "Drenažo plotų dalis, %",
    "rinktuvu_apsaugos_zonu_proc": "Rinktuvų apsaugos zonų plotas, %",
    "gelezinkelio_ribojimo_zonos_proc": "Geležinkelio ribojimo zonos plotas, %",
}

AUTOMATINES_VIZUALIZACIJOS_SLUOKSNIAI = [
    {
        "kodas": "draustiniai",
        "pavadinimas": "Draustiniai",
        "grupe": "Saugomos teritorijos",
        "spalva": "#d73027",
        "aprasymas_zmogui": "Sklypas patenka į draustinio teritoriją arba ją kerta.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "02_projektas" / "papildomi" / "draustiniai_tpdr.gpkg",
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "saugomos_teritorijos" / "draustiniai.gpkg",
        ],
    },
    {
        "kodas": "rezervatai",
        "pavadinimas": "Rezervatai",
        "grupe": "Saugomos teritorijos",
        "spalva": "#a50026",
        "aprasymas_zmogui": "Sklypas patenka į rezervato teritoriją arba ją kerta.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "02_projektas" / "papildomi" / "rezervatai_tpdr.gpkg",
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "saugomos_teritorijos" / "rezervatai.gpkg",
        ],
    },
    {
        "kodas": "parkai",
        "pavadinimas": "Parkai",
        "grupe": "Saugomos teritorijos",
        "spalva": "#f46d43",
        "aprasymas_zmogui": "Sklypas patenka į saugomos teritorijos ribas.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "02_projektas" / "papildomi" / "parkai_tpdr.gpkg",
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "saugomos_teritorijos" / "parkai.gpkg",
        ],
    },
    {
        "kodas": "biosferos_poligonai",
        "pavadinimas": "Biosferos teritorijos",
        "grupe": "Saugomos teritorijos",
        "spalva": "#fdae61",
        "aprasymas_zmogui": "Sklypas patenka į biosferos teritoriją.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "02_projektas" / "papildomi" / "biosferos_poligonai_tpdr.gpkg",
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "saugomos_teritorijos" / "biosferos_poligonai.gpkg",
        ],
    },
    {
        "kodas": "bast",
        "pavadinimas": "BAST teritorijos",
        "grupe": "Saugomos teritorijos",
        "spalva": "#fee08b",
        "aprasymas_zmogui": "Sklypas patenka į BAST teritoriją.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "02_projektas" / "papildomi" / "bast_tpdr.gpkg",
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "saugomos_teritorijos" / "bast.gpkg",
        ],
    },
    {
        "kodas": "past",
        "pavadinimas": "PAST teritorijos",
        "grupe": "Saugomos teritorijos",
        "spalva": "#ffffbf",
        "aprasymas_zmogui": "Sklypas patenka į PAST teritoriją.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "02_projektas" / "papildomi" / "past_tpdr.gpkg",
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "saugomos_teritorijos" / "past.gpkg",
        ],
    },
    {
        "kodas": "pajurio_juosta",
        "pavadinimas": "Pajūrio juosta",
        "grupe": "Saugomos teritorijos",
        "spalva": "#66bd63",
        "aprasymas_zmogui": "Sklypas patenka į pajūrio juostą.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "02_projektas" / "papildomi" / "pajurio_juosta_tpdr.gpkg",
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "saugomos_teritorijos" / "pajurio_juosta.gpkg",
        ],
    },
    {
        "kodas": "buferines_apsaugos_zonos",
        "pavadinimas": "Buferinės apsaugos zonos",
        "grupe": "Saugomos teritorijos",
        "spalva": "#1a9850",
        "aprasymas_zmogui": "Sklypas patenka į apsauginę buferinę zoną.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "02_projektas" / "papildomi" / "buferines_apsaugos_zonos_sutvarkytos.gpkg",
            PROJEKTO_KATALOGAS / "02_projektas" / "papildomi" / "buferines_apsaugos_zonos_tpdr.gpkg",
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "saugomos_teritorijos" / "buferines_apsaugos_zonos.gpkg",
        ],
    },
    {
        "kodas": "miskas",
        "pavadinimas": "Miško teritorijos",
        "grupe": "Gamtiniai ribojimai",
        "spalva": "#2c7bb6",
        "aprasymas_zmogui": "Dalis sklypo patenka į miško teritoriją.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "miskai" / "misko_sklypai.gpkg",
        ],
    },
    {
        "kodas": "kvr_poligonai",
        "pavadinimas": "Kultūros paveldo objektai",
        "grupe": "Kultūros paveldas",
        "spalva": "#5e4fa2",
        "aprasymas_zmogui": "Sklypas patenka į kultūros paveldo objekto teritoriją.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "kulturos_paveldas" / "kvr_poligonai.gpkg",
        ],
    },
    {
        "kodas": "kvr_apsaugos_zonos",
        "pavadinimas": "Kultūros paveldo apsaugos zonos",
        "grupe": "Kultūros paveldas",
        "spalva": "#3288bd",
        "aprasymas_zmogui": "Sklypas patenka į kultūros paveldo apsaugos zoną.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "kulturos_paveldas" / "kvr_apsaugos_zonos.gpkg",
        ],
    },
    {
        "kodas": "pelkes",
        "pavadinimas": "Pelkės",
        "grupe": "Gamtiniai ribojimai",
        "spalva": "#4575b4",
        "aprasymas_zmogui": "Dalis sklypo patenka į pelkių teritoriją.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "szns" / "pelkes_tpdr.gpkg",
        ],
    },
    {
        "kodas": "saltinynai",
        "pavadinimas": "Šaltinynai",
        "grupe": "Gamtiniai ribojimai",
        "spalva": "#74add1",
        "aprasymas_zmogui": "Sklypas patenka į šaltinynų teritoriją.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "szns" / "saltinynai_tpdr.gpkg",
        ],
    },
    {
        "kodas": "pievos_ganyklos",
        "pavadinimas": "Natūralios pievos ir ganyklos",
        "grupe": "Gamtiniai ribojimai",
        "spalva": "#abd9e9",
        "aprasymas_zmogui": "Dalis sklypo patenka į pievų ar ganyklų teritoriją.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "szns" / "pievos_ganyklos_tpdr.gpkg",
        ],
    },
    {
        "kodas": "drenazo_plotai",
        "pavadinimas": "Drenažo plotai",
        "grupe": "Inžineriniai ribojimai",
        "spalva": "#fdae61",
        "aprasymas_zmogui": "Sklype yra melioracijos infrastruktūros ar su ja susijusių plotų.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "melioracija" / "dren_p.gpkg",
        ],
    },
    {
        "kodas": "rinktuvu_apsaugos_zonos",
        "pavadinimas": "Rinktuvų apsaugos zonos",
        "grupe": "Inžineriniai ribojimai",
        "spalva": "#f46d43",
        "aprasymas_zmogui": "Sklype yra melioracijos rinktuvų apsaugos zona.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "melioracija" / "rinkt_l_buffer_15m.gpkg",
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "melioracija" / "rinkt_l_125plus_buffer_15m.gpkg",
        ],
    },
    {
        "kodas": "gelezinkelio_ribojimo_zonos",
        "pavadinimas": "Geležinkelio ribojimo zona",
        "grupe": "Inžineriniai ribojimai",
        "spalva": "#d73027",
        "aprasymas_zmogui": "Sklypas patenka į geležinkelio ribojimo zoną.",
        "galimi_keliai": [
            PROJEKTO_KATALOGAS / "01_duomenys" / "papildomi" / "grpk" / "gelezink_tpdr_buffer_45m.gpkg",
        ],
    },
]