# 05_ui/app.py

from pathlib import Path
import json
import re
import sqlite3
import tempfile
import zipfile

import folium
import geopandas as gpd
import pandas as pd
import streamlit as st

from folium.plugins import MousePosition
from shapely.ops import unary_union, polygonize
from streamlit_folium import st_folium


# ============================================================
# 1. BENDRI NUSTATYMAI
# ============================================================

PROJEKTO_KATALOGAS = Path(__file__).resolve().parents[1]

DB_FAILO_KELIAS = PROJEKTO_KATALOGAS / "03_db" / "baigiamasis.db"
PAGRINDINE_LENTELE = "sklypu_analizes"

ATVIRU_SKLYPU_ZIP = PROJEKTO_KATALOGAS / "01_duomenys" / "atviri_sklypai" / "klaipedos_rajono_sklypai.zip"
SUSIEJIMO_CSV = PROJEKTO_KATALOGAS / "06_rezultatai" / "sklypu_susiejimas_2019_su_atvirais_patvirtintas.csv"

# Foniniam vaizdui
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
    "pelkiu_proc": "Pelkių plotas, %",
    "saltinynu_proc": "Šaltinynų plotas, %",
    "pievu_ganyklu_proc": "Pievų ir ganyklų plotas, %",
    "drenazo_plotu_proc": "Drenažo plotų dalis, %",
    "rinktuvu_apsaugos_zonu_proc": "Rinktuvų apsaugos zonų plotas, %",
    "gelezinkelio_ribojimo_zonos_proc": "Geležinkelio ribojimo zonos plotas, %",
}


# ============================================================
# 2. PAGALBINĖS FUNKCIJOS
# ============================================================

def sutvarkyti_lietuviskus_rasmenis(tekstas: str) -> str:
    try:
        return tekstas.encode("latin1").decode("cp775")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return tekstas


def rodyti_reiksme(reiksme) -> str:
    if reiksme is None:
        return "—"

    try:
        if pd.isna(reiksme):
            return "—"
    except Exception:
        pass

    tekstas = str(reiksme).strip()
    if tekstas == "":
        return "—"

    return sutvarkyti_lietuviskus_rasmenis(tekstas)


def gauti_lauko_pavadinima(lauko_vardas: str) -> str:
    if lauko_vardas in LAUKU_PAVADINIMAI:
        return LAUKU_PAVADINIMAI[lauko_vardas]

    tekstas = lauko_vardas.replace("_", " ").strip()
    return tekstas[:1].upper() + tekstas[1:]


def ar_reiksme_reiksminga(reiksme) -> bool:
    if reiksme is None:
        return False

    try:
        if pd.isna(reiksme):
            return False
    except Exception:
        pass

    if isinstance(reiksme, (int, float)):
        return reiksme != 0

    tekstas = str(reiksme).strip()
    return tekstas not in {"", "0", "0.0", "None", "nan"}


def normalizuoti_identifikatoriu(reiksme):
    if reiksme is None:
        return None

    tekstas = str(reiksme).strip()
    if tekstas.endswith(".0"):
        tekstas = tekstas[:-2]

    return tekstas


def normalizuoti_unikalu_nr_ivesti(ivestis: str) -> str:
    """
    Iš palikto teksto palieka tik skaičius.
    Pvz. ' 44 000 168 9389 ' -> '440001689389'
    """
    return re.sub(r"\D", "", ivestis or "")


def paruosti_gdf_jsonui(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    gdf_json = gdf.copy()

    for stulpelis in gdf_json.columns:
        if stulpelis == "geometry":
            continue

        def konvertuoti_reiksme(x):
            if x is None:
                return None

            try:
                if pd.isna(x):
                    return None
            except Exception:
                pass

            if isinstance(x, pd.Timestamp):
                return x.isoformat()

            if hasattr(x, "isoformat"):
                try:
                    return x.isoformat()
                except Exception:
                    return str(x)

            return x

        gdf_json[stulpelis] = gdf_json[stulpelis].apply(konvertuoti_reiksme)

    return gdf_json


def sukurti_geojson_is_gdf(gdf_4326: gpd.GeoDataFrame) -> dict:
    gdf_jsonui = paruosti_gdf_jsonui(gdf_4326)
    return json.loads(gdf_jsonui.to_json())


def gauti_plota_m2(gdf_3346: gpd.GeoDataFrame) -> float:
    return float(gdf_3346.geometry.area.sum())

@st.cache_data(show_spinner=False)
def nuskaityti_stulpelius_db(db_kelias: str, lenteles_pavadinimas: str) -> list[str]:
    """
    Nuskaito lentelės stulpelius iš SQLite DB.
    """
    conn = sqlite3.connect(db_kelias)
    try:
        df = pd.read_sql_query(f"PRAGMA table_info({lenteles_pavadinimas})", conn)
        return df["name"].tolist()
    finally:
        conn.close()


def gauti_centra_is_geometrijos(gdf_4326: gpd.GeoDataFrame) -> list[float]:
    centroid = gdf_4326.geometry.iloc[0].centroid
    return [centroid.y, centroid.x]


def atrinkti_artimus_sklypus(
    gdf_3346: gpd.GeoDataFrame,
    pasirinkto_gdf_3346: gpd.GeoDataFrame,
    atstumas_metrais: float = ARTIMU_SKLYPU_ATSTUMAS_M,
) -> dict | None:
    buferis = pasirinkto_gdf_3346.geometry.iloc[0].buffer(atstumas_metrais)
    kandidatai = gdf_3346[gdf_3346.geometry.intersects(buferis)].copy()

    if kandidatai.empty:
        return None

    kandidatai_4326 = kandidatai.to_crs(epsg=4326)
    return sukurti_geojson_is_gdf(kandidatai_4326)


def nuskaityti_ikeltas_ribas(uploaded_files):
    """
    Nuskaito įkeltus failus.

    Palaikoma:
    - GPKG
    - GeoJSON / JSON
    - ZIP su SHP
    - SHP rinkinio failai atskirai
    - DXF
    """
    if not uploaded_files:
        return None, None, None

    laikinas_katalogas = Path(tempfile.mkdtemp(prefix="baigiamasis_ikeltos_ribos_"))

    for failas in uploaded_files:
        failo_kelias = laikinas_katalogas / failas.name
        failo_kelias.write_bytes(failas.getbuffer())

    visi_failai = [p for p in laikinas_katalogas.rglob("*") if p.is_file()]

    # Jei vienas ZIP, išskleidžiam
    if len(visi_failai) == 1 and visi_failai[0].suffix.lower() == ".zip":
        with zipfile.ZipFile(visi_failai[0], "r") as zip_obj:
            zip_obj.extractall(laikinas_katalogas)
        visi_failai = [p for p in laikinas_katalogas.rglob("*") if p.is_file()]

    prioritetai = [".gpkg", ".geojson", ".json", ".shp", ".dxf"]
    kandidatas = None

    for suffix in prioritetai:
        for p in visi_failai:
            if p.suffix.lower() == suffix:
                kandidatas = p
                break
        if kandidatas is not None:
            break

    if kandidatas is None:
        raise ValueError("Nerastas tinkamas failas. Įkelk GPKG, GeoJSON/JSON, ZIP SHP, SHP rinkinį arba DXF.")

    gdf = gpd.read_file(kandidatas)

    if gdf.empty:
        raise ValueError("Įkeltame faile nerasta geometrijų.")

    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=3346)

    gdf = gdf[gdf.geometry.notna()].copy()
    gdf = gdf[~gdf.geometry.is_empty].copy()

    if gdf.empty:
        raise ValueError("Po filtravimo neliko geometrijų.")

    gdf_3346 = gdf.to_crs(epsg=3346)

    # Jei tai poligonai, imame juos
    jei_poligonai = gdf_3346.geometry.geom_type.isin(["Polygon", "MultiPolygon"]).any()

    if jei_poligonai:
        poligonai = gdf_3346[gdf_3346.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].copy()

        if poligonai.empty:
            raise ValueError("Nerasta poligoninių geometrijų.")

        bendra_geometrija = unary_union(poligonai.geometry.tolist())
    else:
        # Bandome poligonizuoti iš linijų
        sujungta = unary_union(gdf_3346.geometry.tolist())
        sugeneruoti_poligonai = list(polygonize(sujungta))

        if not sugeneruoti_poligonai:
            raise ValueError(
                "Įkelta geometrija nėra poligoninė. Jei tai DXF, linijos turi sudaryti uždarą kontūrą."
            )

        bendra_geometrija = unary_union(sugeneruoti_poligonai)

    vienas_gdf_3346 = gpd.GeoDataFrame(
        {"saltinis": ["ikeltas_failas"]},
        geometry=[bendra_geometrija],
        crs="EPSG:3346",
    )
    vienas_gdf_4326 = vienas_gdf_3346.to_crs(epsg=4326)

    info = {
        "failo_pavadinimai": [f.name for f in uploaded_files],
        "plotas_m2": round(gauti_plota_m2(vienas_gdf_3346), 2),
        "crs": str(vienas_gdf_3346.crs),
        "geom_tipai": list(gdf.geometry.geom_type.unique()),
    }

    return vienas_gdf_3346, vienas_gdf_4326, info


def sukurti_zemelapi(
    centras: list[float],
    pradinis_sklypo_geojson=None,
    ikeltu_ribu_geojson=None,
    artimu_sklypu_geojson=None,
):
    zemelapis = folium.Map(
        location=centras,
        zoom_start=PRADINIS_ZOOM,
        control_scale=True,
        tiles="OpenStreetMap",
    )

    folium.raster_layers.WmsTileLayer(
        url=RC_WMS_URL,
        name="RC kadastro žemėlapis",
        layers=RC_WMS_LAYERS,
        fmt="image/png",
        transparent=True,
        version="1.1.1",
        attr="Geoportal / Registrų centras",
        overlay=True,
        control=True,
        show=True,
    ).add_to(zemelapis)

    if artimu_sklypu_geojson:
        folium.GeoJson(
            artimu_sklypu_geojson,
            name="Aplinkiniai sklypai",
            style_function=lambda _:{
                "color": "#666666",
                "weight": 1,
                "fillColor": "#999999",
                "fillOpacity": 0.03,
            },
        ).add_to(zemelapis)

    if pradinis_sklypo_geojson:
        folium.GeoJson(
            pradinis_sklypo_geojson,
            name="Pradinis sklypas",
            style_function=lambda _:{
                "color": "red",
                "weight": 4,
                "fillColor": "red",
                "fillOpacity": 0.12,
            },
        ).add_to(zemelapis)

    if ikeltu_ribu_geojson:
        folium.GeoJson(
            ikeltu_ribu_geojson,
            name="Įkeltos aktualios ribos",
            style_function=lambda _:{
                "color": "green",
                "weight": 4,
                "fillColor": "green",
                "fillOpacity": 0.12,
            },
        ).add_to(zemelapis)

    MousePosition(
        position="topright",
        separator=" | ",
        prefix="Koordinatės",
    ).add_to(zemelapis)

    folium.LayerControl().add_to(zemelapis)
    return zemelapis


def parodyti_laukus_is_eilutes(eilute: pd.Series, laukai: list[str]):
    paruosta = []

    for laukas in laukai:
        if laukas in eilute.index:
            paruosta.append((gauti_lauko_pavadinima(laukas), rodyti_reiksme(eilute[laukas])))

    if not paruosta:
        st.info("Rodomų laukų nerasta.")
        return

    col1, col2 = st.columns(2)
    per_puse = (len(paruosta) + 1) // 2

    with col1:
        for pavadinimas, reiksme in paruosta[:per_puse]:
            st.markdown(f"**{pavadinimas}:** {reiksme}")

    with col2:
        for pavadinimas, reiksme in paruosta[per_puse:]:
            st.markdown(f"**{pavadinimas}:** {reiksme}")


def isvalyti_rezultatus():
    raktai = [
        "rasto_db_irasa_dict",
        "rasto_atviro_sklypo_info",
        "rasto_atviro_sklypo_atributai",
        "pradinio_sklypo_geojson",
        "artimu_sklypu_geojson",
        "zemelapio_centras",
        "db_busena",
    ]
    for raktas in raktai:
        if raktas in st.session_state:
            del st.session_state[raktas]


# ============================================================
# 3. DUOMENŲ UŽKROVIMAS
# ============================================================

@st.cache_resource(show_spinner=True)
def uzkrauti_atvirus_sklypus(zip_kelias: str):
    zip_path = Path(zip_kelias)

    if not zip_path.exists():
        raise FileNotFoundError(f"Nerastas ZIP failas: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as zip_obj:
        failai = zip_obj.namelist()
        tinkami = [p for p in failai if p.lower().endswith(".json") or p.lower().endswith(".geojson")]

        if not tinkami:
            raise FileNotFoundError("ZIP faile nerasta JSON / GeoJSON rinkmenos.")

        vidinis_failas = tinkami[0]

        laikinas_katalogas = Path(tempfile.gettempdir()) / "baigiamasis_atviri_sklypai_ui"
        laikinas_katalogas.mkdir(parents=True, exist_ok=True)

        isskleisto_failo_kelias = laikinas_katalogas / Path(vidinis_failas).name

        with zip_obj.open(vidinis_failas) as src, open(isskleisto_failo_kelias, "wb") as dst:
            dst.write(src.read())

    gdf = gpd.read_file(isskleisto_failo_kelias)

    if gdf.empty:
        raise ValueError("Atvirų sklypų sluoksnis tuščias.")

    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=3346)

    gdf_3346 = gdf.to_crs(epsg=3346)
    gdf_4326 = gdf_3346.to_crs(epsg=4326)

    if "unikalus_nr" in gdf_3346.columns:
        gdf_3346["__unikalus_nr_text"] = gdf_3346["unikalus_nr"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
        gdf_4326["__unikalus_nr_text"] = gdf_4326["unikalus_nr"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()

    if "kadastro_nr" in gdf_3346.columns:
        gdf_3346["__kadastro_nr_text"] = gdf_3346["kadastro_nr"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
        gdf_4326["__kadastro_nr_text"] = gdf_4326["kadastro_nr"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()

    minx, miny, maxx, maxy = gdf_4326.total_bounds
    centro_lat = (miny + maxy) / 2
    centro_lon = (minx + maxx) / 2

    return {
        "gdf_3346": gdf_3346,
        "gdf_4326": gdf_4326,
        "centras": [centro_lat, centro_lon],
        "stulpeliai": list(gdf_4326.columns),
    }


@st.cache_data(show_spinner=False)
def uzkrauti_susiejimo_csv(csv_kelias: str) -> pd.DataFrame:
    df = pd.read_csv(csv_kelias)

    for stulpelis in ["db_sklypo_id", "atviru_unikalus_nr", "atviru_kadastro_nr"]:
        if stulpelis in df.columns:
            df[stulpelis] = df[stulpelis].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()

    return df


# ============================================================
# 4. PAGRINDINĖS PAIEŠKOS FUNKCIJOS
# ============================================================

def ieskoti_aktualiame_sluoksnyje_pagal_unikalu_nr(
    unikalus_nr: str,
    gdf_3346: gpd.GeoDataFrame,
    gdf_4326: gpd.GeoDataFrame,
):
    if "__unikalus_nr_text" not in gdf_3346.columns:
        return None, None, None

    rasti_3346 = gdf_3346[gdf_3346["__unikalus_nr_text"] == str(unikalus_nr)]
    rasti_4326 = gdf_4326[gdf_4326["__unikalus_nr_text"] == str(unikalus_nr)]

    if rasti_3346.empty or rasti_4326.empty:
        return None, None, None

    return rasti_3346.iloc[[0]], rasti_4326.iloc[[0]], {
        "atviru_unikalus_nr": str(unikalus_nr),
        "atviru_kadastro_nr": normalizuoti_identifikatoriu(rasti_3346.iloc[0].get("kadastro_nr")),
    }


def rasti_db_sklypo_id_per_susiejima(
    susiejimo_df: pd.DataFrame,
    atviru_unikalus_nr: str | None,
    atviru_kadastro_nr: str | None,
):
    if atviru_unikalus_nr:
        rasti = susiejimo_df[susiejimo_df["atviru_unikalus_nr"] == str(atviru_unikalus_nr)]
        if not rasti.empty:
            return str(rasti.iloc[0]["db_sklypo_id"]), "atviru_unikalus_nr", str(atviru_unikalus_nr)

    if atviru_kadastro_nr:
        rasti = susiejimo_df[susiejimo_df["atviru_kadastro_nr"] == str(atviru_kadastro_nr)]
        if not rasti.empty:
            return str(rasti.iloc[0]["db_sklypo_id"]), "atviru_kadastro_nr", str(atviru_kadastro_nr)

    return None, None, None


# ============================================================
# 5. STREAMLIT PUSLAPIS
# ============================================================

st.set_page_config(
    page_title="Sklypo analizės sistema",
    page_icon="🏡",
    layout="wide",
)

st.title("🏡 Automatinė sklypo statybos galimybių analizės sistema")
st.caption("Paieška pirmiausia pagal aktualų sklypų sluoksnį")

st.markdown(
    """
    Ši versija veikia teisinga logika:

    1. pirmiausia ieškoma **aktualiame sklypų sluoksnyje** pagal unikalų numerį;
    2. jei sklypas randamas, jis rodomas žemėlapyje;
    3. po to tikrinama, ar šiam sklypui jau yra analizė DB;
    4. jei DB įrašo nėra, rodoma aiški būsena: **sklypas rastas, analizė dar nesukurta**.
    """
)

# Patikrinimai
if not DB_FAILO_KELIAS.exists():
    st.error(f"Nerastas DB failas: {DB_FAILO_KELIAS}")
    st.stop()

if not ATVIRU_SKLYPU_ZIP.exists():
    st.error(f"Nerastas atvirų sklypų ZIP: {ATVIRU_SKLYPU_ZIP}")
    st.stop()

if not SUSIEJIMO_CSV.exists():
    st.error(f"Nerastas susiejimo CSV: {SUSIEJIMO_CSV}")
    st.stop()

try:
    db_stulpeliai = nuskaityti_stulpelius_db(str(DB_FAILO_KELIAS), PAGRINDINE_LENTELE)
    atviri_duomenys = uzkrauti_atvirus_sklypus(str(ATVIRU_SKLYPU_ZIP))
    susiejimo_df = uzkrauti_susiejimo_csv(str(SUSIEJIMO_CSV))
except Exception as klaida:
    st.error(f"Nepavyko užkrauti duomenų: {klaida}")
    st.stop()

gdf_3346 = atviri_duomenys["gdf_3346"]
gdf_4326 = atviri_duomenys["gdf_4326"]
zemelapio_pradinis_centras = atviri_duomenys["centras"]
atviru_stulpeliai = atviri_duomenys["stulpeliai"]

# Šoninė juosta
st.sidebar.header("Naudojami nustatymai")
st.sidebar.write("**DB failas:**")
st.sidebar.code(str(DB_FAILO_KELIAS), language="text")
st.sidebar.write("**Atvirų sklypų ZIP:**")
st.sidebar.code(str(ATVIRU_SKLYPU_ZIP), language="text")
st.sidebar.write("**Susiejimo CSV:**")
st.sidebar.code(str(SUSIEJIMO_CSV), language="text")
st.sidebar.write("**Atvirų sklypų skaičius:**")
st.sidebar.write(len(gdf_4326))
st.sidebar.write("**Patvirtintų susiejimų skaičius:**")
st.sidebar.write(len(susiejimo_df))

if st.sidebar.button("Išvalyti rezultatą", use_container_width=True):
    isvalyti_rezultatus()
    st.rerun()

with st.sidebar.expander("Rodyti DB stulpelius"):
    st.write(db_stulpeliai)

with st.sidebar.expander("Rodyti atvirų duomenų stulpelius"):
    st.write(atviru_stulpeliai)

# ============================================================
# 6. AKTUALAUS SKLYPO PAIEŠKA
# ============================================================

st.subheader("1. Aktualaus sklypo paieška pagal unikalų numerį")

with st.form("aktualaus_sklypo_paieska"):
    ivestas_unikalus_nr = st.text_input(
        "Unikalus numeris",
        placeholder="Pvz. 440001689389",
    )
    ieskoti_paspausta = st.form_submit_button("Ieškoti aktualiame sluoksnyje", use_container_width=True)

if ieskoti_paspausta:
    unikalus_nr = normalizuoti_unikalu_nr_ivesti(ivestas_unikalus_nr)

    if not unikalus_nr:
        st.warning("Pirmiausia įvesk unikalų numerį.")
        st.stop()

    rastas_3346, rastas_4326, atviro_info = ieskoti_aktualiame_sluoksnyje_pagal_unikalu_nr(
        unikalus_nr=unikalus_nr,
        gdf_3346=gdf_3346,
        gdf_4326=gdf_4326,
    )

    if rastas_3346 is None or rastas_4326 is None:
        st.session_state["rasto_db_irasa_dict"] = None
        st.session_state["rasto_atviro_sklypo_info"] = None
        st.session_state["rasto_atviro_sklypo_atributai"] = None
        st.session_state["pradinio_sklypo_geojson"] = None
        st.session_state["artimu_sklypu_geojson"] = None
        st.session_state["zemelapio_centras"] = zemelapio_pradinis_centras
        st.session_state["db_busena"] = "aktualiame_sluoksnyje_nerastas"
        st.warning("Sklypas pagal šį unikalų numerį aktualiame sluoksnyje nerastas.")
    else:
        st.session_state["rasto_atviro_sklypo_info"] = atviro_info
        st.session_state["rasto_atviro_sklypo_atributai"] = rastas_3346.iloc[0].drop(labels="geometry").to_dict()
        st.session_state["pradinio_sklypo_geojson"] = sukurti_geojson_is_gdf(rastas_4326)
        st.session_state["artimu_sklypu_geojson"] = atrinkti_artimus_sklypus(
            gdf_3346=gdf_3346,
            pasirinkto_gdf_3346=rastas_3346,
            atstumas_metrais=ARTIMU_SKLYPU_ATSTUMAS_M,
        )
        st.session_state["zemelapio_centras"] = gauti_centra_is_geometrijos(rastas_4326)

        db_sklypo_id, susiejimo_laukas, susiejimo_reiksme = rasti_db_sklypo_id_per_susiejima(
            susiejimo_df=susiejimo_df,
            atviru_unikalus_nr=atviro_info.get("atviru_unikalus_nr"),
            atviru_kadastro_nr=atviro_info.get("atviru_kadastro_nr"),
        )

        if db_sklypo_id:
            db_df = ieskoti_db_pagal_sklypo_id(str(DB_FAILO_KELIAS), db_sklypo_id)

            if not db_df.empty:
                st.session_state["rasto_db_irasa_dict"] = db_df.iloc[0].to_dict()
                st.session_state["db_busena"] = "analize_rasta"
            else:
                st.session_state["rasto_db_irasa_dict"] = None
                st.session_state["db_busena"] = "susiejimas_yra_bet_analizes_nera"
        else:
            st.session_state["rasto_db_irasa_dict"] = None
            st.session_state["db_busena"] = "analizes_nera"

# ============================================================
# 7. RASTO SKLYPO INFORMACIJA
# ============================================================

st.subheader("2. Rasto aktualaus sklypo informacija")

rasto_atviro_sklypo_info = st.session_state.get("rasto_atviro_sklypo_info")
rasto_atviro_sklypo_atributai = st.session_state.get("rasto_atviro_sklypo_atributai")
db_busena = st.session_state.get("db_busena")

if not rasto_atviro_sklypo_info:
    st.info("Dar neieškotas aktualus sklypas.")
else:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Atvirų duomenų unikalus_nr:** {rodyti_reiksme(rasto_atviro_sklypo_info.get('atviru_unikalus_nr'))}")
        st.markdown(f"**Atvirų duomenų kadastro_nr:** {rodyti_reiksme(rasto_atviro_sklypo_info.get('atviru_kadastro_nr'))}")

    with col2:
        if rasto_atviro_sklypo_atributai:
            st.markdown(f"**Plotas (skl_plotas):** {rodyti_reiksme(rasto_atviro_sklypo_atributai.get('skl_plotas'))} ha")
            st.markdown(f"**Paskirties tipas:** {rodyti_reiksme(rasto_atviro_sklypo_atributai.get('pask_tipas'))}")

    if db_busena == "analize_rasta":
        st.success("Šiam aktualiam sklypui DB analizė rasta.")
    elif db_busena == "analizes_nera":
        st.warning("Sklypas rastas, bet analizė šiam aktualiam sklypui dar nesukurta.")
    elif db_busena == "susiejimas_yra_bet_analizes_nera":
        st.warning("Susiejimas su DB rastas, bet analizės įrašo lentelėje nerasta.")
    elif db_busena == "aktualiame_sluoksnyje_nerastas":
        st.warning("Sklypas aktualiame sluoksnyje nerastas.")

    if rasto_atviro_sklypo_atributai:
        with st.expander("Rodyti visus aktualaus sklypo atributus"):
            df_atributai = pd.DataFrame(
                [{"Laukas": k, "Reikšmė": rodyti_reiksme(v)} for k, v in rasto_atviro_sklypo_atributai.items()]
            )
            st.dataframe(df_atributai, use_container_width=True)

# ============================================================
# 8. ŽEMĖLAPIS
# ============================================================

st.subheader("3. Sklypo vaizdas žemėlapyje")

pradinio_sklypo_geojson = st.session_state.get("pradinio_sklypo_geojson")
artimu_sklypu_geojson = st.session_state.get("artimu_sklypu_geojson")
zemelapio_centras = st.session_state.get("zemelapio_centras", zemelapio_pradinis_centras)

ikeltos_ribos_3346 = None
ikeltos_ribos_4326 = None
ikeltu_ribu_info = None
ikeltu_ribu_geojson = None

uploaded_files = st.file_uploader(
    "Jei reikia atnaujinti sklypo ribas, įkelk GPKG / GeoJSON / ZIP SHP / SHP rinkmenas / DXF",
    type=["gpkg", "geojson", "json", "zip", "shp", "dbf", "shx", "prj", "cpg", "dxf"],
    accept_multiple_files=True,
)

if uploaded_files:
    try:
        ikeltos_ribos_3346, ikeltos_ribos_4326, ikeltu_ribu_info = nuskaityti_ikeltas_ribas(uploaded_files)
        ikeltu_ribu_geojson = sukurti_geojson_is_gdf(ikeltos_ribos_4326)
        st.success("Įkeltos ribos sėkmingai nuskaitytos ir parodytos žemėlapyje.")
    except Exception as klaida:
        st.error(f"Nepavyko nuskaityti įkeltų ribų: {klaida}")

zemelapis = sukurti_zemelapi(
    centras=zemelapio_centras,
    pradinis_sklypo_geojson=pradinio_sklypo_geojson,
    ikeltu_ribu_geojson=ikeltu_ribu_geojson,
    artimu_sklypu_geojson=artimu_sklypu_geojson,
)

st_folium(
    zemelapis,
    height=ZEMELAPIO_AUKSTIS,
    width=ZEMELAPIO_PLOTIS,
    returned_objects=[],
    key="zemelapis_su_ribomis",
)

if pradinio_sklypo_geojson:
    st.caption("Raudonai rodomas rastas aktualus sklypas, pilkai – aplinkiniai sklypai, žaliai – įkeltos aktualios ribos.")

if ikeltu_ribu_info:
    st.markdown("### Įkeltų ribų suvestinė")
    st.write(f"**Failai:** {', '.join(ikeltu_ribu_info['failo_pavadinimai'])}")
    st.write(f"**CRS:** {ikeltu_ribu_info['crs']}")
    st.write(f"**Pradiniai geometrijų tipai:** {', '.join(ikeltu_ribu_info['geom_tipai'])}")
    st.write(f"**Įkeltų ribų plotas:** {ikeltu_ribu_info['plotas_m2']} m²")

# ============================================================
# 9. PERSKAIČIAVIMO BLOKAS
# ============================================================

st.subheader("4. Perskaičiavimas pagal aktualias ribas")

if not rasto_atviro_sklypo_info:
    st.info("Pirmiausia rask aktualų sklypą pagal unikalų numerį.")
elif ikeltos_ribos_3346 is None:
    st.info("Įkelk aktualias ribas, kad būtų galima paruošti perskaičiavimą.")
else:
    pradinis_plotas_m2 = None

    if rasto_atviro_sklypo_atributai and rasto_atviro_sklypo_atributai.get("skl_plotas") is not None:
        try:
            pradinis_plotas_m2 = float(rasto_atviro_sklypo_atributai["skl_plotas"]) * 10000
        except Exception:
            pradinis_plotas_m2 = None

    perskaiciuoti_paspausta = st.button("Perskaičiuoti pagal įkeltas ribas", use_container_width=True)

    if perskaiciuoti_paspausta:
        naujas_plotas_m2 = gauti_plota_m2(ikeltos_ribos_3346)

        st.success("Įkeltos ribos priimtos perskaičiavimui.")
        st.write(f"**Naujų ribų plotas:** {round(naujas_plotas_m2, 2)} m²")

        if pradinis_plotas_m2 is not None:
            skirtumas = naujas_plotas_m2 - pradinis_plotas_m2
            st.write(f"**Ankstesnis plotas:** {round(pradinis_plotas_m2, 2)} m²")
            st.write(f"**Ploto skirtumas:** {round(skirtumas, 2)} m²")

        st.info(
            "Šiame etape jau veikia realus ribų įkėlimas, nuskaitymas ir ploto palyginimas. "
            "Kitas žingsnis – prijungti tikrą GIS perskaičiavimą prie tavo esamos analizės funkcijos."
        )

# ============================================================
# 10. DB ANALIZĖ
# ============================================================

st.subheader("5. Vidinės DB atitikmuo ir preliminari analizė")

rasto_db_irasa_dict = st.session_state.get("rasto_db_irasa_dict")

if not rasto_db_irasa_dict:
    if db_busena in ["analizes_nera", "susiejimas_yra_bet_analizes_nera"]:
        st.info("Aktualus sklypas rastas, bet jo analizė DB dar nesukurta.")
    else:
        st.info("Kol kas DB analizės įrašas nerastas.")
else:
    db_eilute = pd.Series(rasto_db_irasa_dict)

    st.success("Rastas atitikmuo vidinėje analizės DB.")

    st.markdown("### Sklypo suvestinė")
    parodyti_laukus_is_eilutes(db_eilute, SVARBIAUSI_DB_LAUKAI)

    st.markdown("---")

    st.markdown("### Pagrindiniai ribojimai")
    ribojimai_rodymui = []

    for laukas in RIBOJIMU_LAUKAI:
        if laukas in db_eilute.index and ar_reiksme_reiksminga(db_eilute[laukas]):
            ribojimai_rodymui.append(
                (gauti_lauko_pavadinima(laukas), rodyti_reiksme(db_eilute[laukas]))
            )

    if ribojimai_rodymui:
        for pavadinimas, reiksme in ribojimai_rodymui:
            st.write(f"- **{pavadinimas}:** {reiksme}")
    else:
        st.write("Reikšmingų ribojimų šiame bloke nerasta arba jie DB dar neužpildyti.")

# ============================================================
# 11. PAPILDOMA RANKINĖ VALIDACIJA
# ============================================================

st.subheader("6. Papildoma rankinė validacija")

if not rasto_atviro_sklypo_info:
    st.info("Pirmiausia rask aktualų sklypą.")
else:
    col1, col2 = st.columns(2)

    with col1:
        szns_rezultatas = st.selectbox(
            "Ar SŽNS riboja statybą?",
            options=["neperžiūrėta", "ne", "taip", "dalinai"],
            index=0,
        )

        papildomi_sluoksniai = st.multiselect(
            "Kokie papildomi sluoksniai buvo peržiūrėti?",
            options=[
                "SŽNS",
                "Kultūros paveldo objektai",
                "Drenažas",
                "Miško plotai",
                "Kelių / geležinkelio ribojimai",
                "Vandens telkinių apsaugos zonos",
                "Kiti",
            ],
        )

    with col2:
        galutinis_sprendimas = st.selectbox(
            "Galutinis specialisto sprendimas",
            options=[
                "nepriimtas",
                "galima",
                "galima su sąlygomis",
                "negalima",
                "reikia papildomų duomenų",
            ],
            index=0,
        )

        reikia_papildomos_rankines_patiktros = st.checkbox(
            "Reikia papildomos rankinės patikros",
            value=False,
        )

    rankines_validacijos_pastaba = st.text_area(
        "Rankinės validacijos pastaba",
        placeholder="Pvz. Įvertinus papildomus sluoksnius nustatyta, kad sklypo dalyje galioja papildomos sąlygos.",
        height=120,
    )

    galutinio_sprendimo_paaiskinimas = st.text_area(
        "Galutinio sprendimo paaiškinimas",
        placeholder="Pvz. Statyba galima tik ne SŽNS dalyje, būtina papildoma projektinė analizė.",
        height=120,
    )

    st.markdown("### Rankinės validacijos santrauka")
    st.write(f"**SŽNS vertinimas:** {szns_rezultatas}")
    st.write(f"**Peržiūrėti papildomi sluoksniai:** {', '.join(papildomi_sluoksniai) if papildomi_sluoksniai else '—'}")
    st.write(f"**Galutinis sprendimas:** {galutinis_sprendimas}")
    st.write(f"**Reikia papildomos rankinės patikros:** {'Taip' if reikia_papildomos_rankines_patiktros else 'Ne'}")
    st.write(f"**Rankinės validacijos pastaba:** {rankines_validacijos_pastaba if rankines_validacijos_pastaba.strip() else '—'}")
    st.write(f"**Galutinio sprendimo paaiškinimas:** {galutinio_sprendimo_paaiskinimas if galutinio_sprendimo_paaiskinimas.strip() else '—'}")

# ============================================================
# 12. PDF KRYPTIS
# ============================================================

st.subheader("7. Ataskaitos kryptis")

st.info(
    """
    Kitas žingsnis:
    - generuoti PDF ataskaitą;
    - į ją įdėti sklypo identifikaciją;
    - automatinę analizę;
    - rankinės validacijos išvadą;
    - žemėlapio vaizdą su sklypo ribomis, o vėliau ir SŽNS sluoksniais.
    """
)

# ============================================================
# 13. APAČIOS INFORMACIJA
# ============================================================

st.markdown("---")
st.caption(
    "Dabartinė versija: paieška pagal aktualų sklypų sluoksnį + sklypo vaizdas žemėlapyje + "
    "aktualių ribų įkėlimas + DB analizės patikra + rankinė validacija."
)