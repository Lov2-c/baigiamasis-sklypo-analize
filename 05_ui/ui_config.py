from pathlib import Path

PROJEKTO_KATALOGAS = Path(__file__).resolve().parents[1]

DB_FAILO_KELIAS = PROJEKTO_KATALOGAS / "03_db" / "baigiamasis.db"
PAGRINDINE_LENTELE = "sklypu_analizes"

ATVIRU_SKLYPU_ZIP = PROJEKTO_KATALOGAS / "01_duomenys" / "atviri_sklypai" / "klaipedos_rajono_sklypai.zip"
SUSIEJIMO_CSV = PROJEKTO_KATALOGAS / "06_rezultatai" / "sklypu_susiejimas_2019_su_atvirais_patvirtintas.csv"

RC_KADASTRO_MAPSERVER_URL = "https://www.geoportal.lt/mapproxy/rc_kadastro_zemelapis/MapServer"
RC_SZNS_MAPSERVER_URL = "https://www.geoportal.lt/mapproxy/rc_szns/MapServer"

RC_WMS_URL = "https://www.geoportal.lt/mapproxy/rc_kadastro_zemelapis/MapServer/WMSServer"
RC_WMS_LAYERS = "15,21,27,33"
RC_SZNS_WMS_URL = "https://www.geoportal.lt/mapproxy/rc_szns/MapServer/WMSServer"
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


RANKINES_SZNS_SLUOKSNIAI = {
    # Inžineriniai objektai
    "Ryšių apsaugos zona": {
        "layer_id": "1",
        "grupe": "Inžineriniai objektai",
        "spalva": "#8dd3c7",
    },
    "Elektros tinklų apsaugos zona": {
        "layer_id": "2",
        "grupe": "Inžineriniai objektai",
        "spalva": "#ffd92f",
    },
    "Magistralinių dujotiekių apsaugos zona": {
        "layer_id": "3",
        "grupe": "Inžineriniai objektai",
        "spalva": "#fb8072",
    },
    "Magistralinių dujotiekių vietovių klasių teritorijos": {
        "layer_id": "4",
        "grupe": "Inžineriniai objektai",
        "spalva": "#fdb462",
    },
    "Naftos įrenginių apsaugos zona": {
        "layer_id": "5",
        "grupe": "Inžineriniai objektai",
        "spalva": "#b15928",
    },
    "Dujotiekių apsaugos zona": {
        "layer_id": "6",
        "grupe": "Inžineriniai objektai",
        "spalva": "#fccde5",
    },
    "Suskystintų dujų įrenginių apsaugos zona": {
        "layer_id": "7",
        "grupe": "Inžineriniai objektai",
        "spalva": "#d9d9d9",
    },
    "Geodezinių ženklų apsaugos zona": {
        "layer_id": "8",
        "grupe": "Inžineriniai objektai",
        "spalva": "#bc80bd",
    },
    "Meteorologinių aikštelių apsaugos zona": {
        "layer_id": "10",
        "grupe": "Inžineriniai objektai",
        "spalva": "#ccebc5",
    },
    "Meteorologinių radiolokatorių apsaugos zona": {
        "layer_id": "11",
        "grupe": "Inžineriniai objektai",
        "spalva": "#80b1d3",
    },
    "Požeminio vandens vandenviečių apsaugos zona": {
        "layer_id": "12",
        "grupe": "Inžineriniai objektai",
        "spalva": "#1f78b4",
    },
    "Vandens stočių apsaugos zona": {
        "layer_id": "13",
        "grupe": "Inžineriniai objektai",
        "spalva": "#33a02c",
    },
    "Šilumos perdavimo tinklų apsaugos zona": {
        "layer_id": "14",
        "grupe": "Inžineriniai objektai",
        "spalva": "#ff7f00",
    },
    "Vandens tiekimo ir nuotėkų apsaugos zona": {
        "layer_id": "15",
        "grupe": "Inžineriniai objektai",
        "spalva": "#6a3d9a",
    },
    "Molėtų observatorijos apsaugos zona": {
        "layer_id": "16",
        "grupe": "Inžineriniai objektai",
        "spalva": "#b2df8a",
    },

    # Susisiekimo objektai
    "Kelių apsaugos zona": {
        "layer_id": "18",
        "grupe": "Susisiekimo objektai",
        "spalva": "#fee08b",
    },
    "Klaipėdos uosto apsaugos zona": {
        "layer_id": "20",
        "grupe": "Susisiekimo objektai",
        "spalva": "#f46d43",
    },
    "Aerodromų apsaugos zona": {
        "layer_id": "21",
        "grupe": "Susisiekimo objektai",
        "spalva": "#e31a1c",
    },
    "Aerodromų triukšmo apsaugos zona": {
        "layer_id": "22",
        "grupe": "Susisiekimo objektai",
        "spalva": "#fb9a99",
    },

    # Kultūros ir gamtos apsauga
    "Biosferos rezervatai": {
        "layer_id": "25",
        "grupe": "Kultūros ir gamtos apsauga",
        "spalva": "#fdae61",
    },
    "Gamtos paveldo objektų teritorijos": {
        "layer_id": "27",
        "grupe": "Kultūros ir gamtos apsauga",
        "spalva": "#66c2a5",
    },

    # Sanitariniai objektai
    "Branduolinių objektų apsaugos zona": {
        "layer_id": "52",
        "grupe": "Sanitariniai objektai",
        "spalva": "#e41a1c",
    },
    "Gamybinių objektų sanitarinė apsaugos zona": {
        "layer_id": "53",
        "grupe": "Sanitariniai objektai",
        "spalva": "#ff7f00",
    },
    "Pastatuose laikomų gyvulių sanitarinė apsaugos zona": {
        "layer_id": "54",
        "grupe": "Sanitariniai objektai",
        "spalva": "#a65628",
    },
    "Komunalinių objektų sanitarinė apsaugos zona": {
        "layer_id": "55",
        "grupe": "Sanitariniai objektai",
        "spalva": "#999999",
    },
    "Juodligės židinių apsaugos zona": {
        "layer_id": "56",
        "grupe": "Sanitariniai objektai",
        "spalva": "#984ea3",
    },

    # Gamtos objektai
    "Žemės gelmių išteklių telkinių apsaugos zona": {
        "layer_id": "59",
        "grupe": "Gamtos objektai",
        "spalva": "#a6d854",
    },
    "Karstinio regiono apsaugos zona": {
        "layer_id": "60",
        "grupe": "Gamtos objektai",
        "spalva": "#ffd92f",
    },
    "Vandens telkiniai": {
        "layer_id": "62",
        "grupe": "Gamtos objektai",
        "spalva": "#1f78b4",
    },
    "Dirvožemio apsauga": {
        "layer_id": "65",
        "grupe": "Gamtos objektai",
        "spalva": "#b2df8a",
    },
    "Akvakultūros tvenkinių apsaugos zona": {
        "layer_id": "66",
        "grupe": "Gamtos objektai",
        "spalva": "#6baed6",
    },
    "Paviršinių vandens telkinių apsaugos zona": {
        "layer_id": "67",
        "grupe": "Gamtos objektai",
        "spalva": "#3288bd",
    },
    "Paviršinių vandens telkinių pakrantės apsaugos juosta": {
        "layer_id": "68",
        "grupe": "Gamtos objektai",
        "spalva": "#74add1",
    },
    "Potvynio grėsmės teritorijos": {
        "layer_id": "69",
        "grupe": "Gamtos objektai",
        "spalva": "#4575b4",
    },

    # Valstybės apsaugos ir panašios
    "Valstybės sienos objektų ir įrenginių apsaugos zona": {
        "layer_id": "71",
        "grupe": "Valstybės apsaugos objektai",
        "spalva": "#b3de69",
    },
    "Radiolokatorių apsaugos zona": {
        "layer_id": "72",
        "grupe": "Valstybės apsaugos objektai",
        "spalva": "#fccde5",
    },
    "Krašto apsaugos objektų apsaugos zona": {
        "layer_id": "73",
        "grupe": "Valstybės apsaugos objektai",
        "spalva": "#bc80bd",
    },
    "VSD saugomų objektų apsaugos zona": {
        "layer_id": "74",
        "grupe": "Valstybės apsaugos objektai",
        "spalva": "#8c510a",
    },
    "Vadovybės apsaugos tarnybos objektų apsaugos zona": {
        "layer_id": "75",
        "grupe": "Valstybės apsaugos objektai",
        "spalva": "#543005",
    },
    "NS teritorijos su statybos apribojimais": {
        "layer_id": "76",
        "grupe": "Valstybės apsaugos objektai",
        "spalva": "#d73027",
    },
}