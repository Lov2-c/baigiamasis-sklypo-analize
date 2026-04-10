from pathlib import Path
import sqlite3
import tempfile
import zipfile

import geopandas as gpd
import pandas as pd
import streamlit as st
from shapely.ops import unary_union, polygonize

from ui_config import PAGRINDINE_LENTELE, ARTIMU_SKLYPU_ATSTUMAS_M
from ui_helpers import (
    gauti_plota_m2,
    normalizuoti_identifikatoriu,
    sukurti_geojson_is_gdf,
)


@st.cache_data(show_spinner=False)
def nuskaityti_stulpelius_db(db_kelias: str, lenteles_pavadinimas: str) -> list[str]:
    conn = sqlite3.connect(db_kelias)
    try:
        df = pd.read_sql_query(f"PRAGMA table_info({lenteles_pavadinimas})", conn)
        return df["name"].tolist()
    finally:
        conn.close()


@st.cache_data(show_spinner=False)
def ieskoti_db_pagal_sklypo_id(db_kelias: str, sklypo_id: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_kelias)
    try:
        uzklausa = f"SELECT * FROM {PAGRINDINE_LENTELE} WHERE CAST(sklypo_id AS TEXT) = ?"
        return pd.read_sql_query(uzklausa, conn, params=[str(sklypo_id)])
    finally:
        conn.close()


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
    if not uploaded_files:
        return None, None, None

    laikinas_katalogas = Path(tempfile.mkdtemp(prefix="baigiamasis_ikeltos_ribos_"))

    for failas in uploaded_files:
        failo_kelias = laikinas_katalogas / failas.name
        failo_kelias.write_bytes(failas.getbuffer())

    visi_failai = [p for p in laikinas_katalogas.rglob("*") if p.is_file()]

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

    ar_yra_poligonu = gdf_3346.geometry.geom_type.isin(["Polygon", "MultiPolygon"]).any()

    if ar_yra_poligonu:
        poligonai = gdf_3346[gdf_3346.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].copy()

        if poligonai.empty:
            raise ValueError("Nerasta poligoninių geometrijų.")

        bendra_geometrija = unary_union(poligonai.geometry.tolist())
    else:
        sujungta_geometrija = unary_union(gdf_3346.geometry.tolist())
        sugeneruoti_poligonai = list(polygonize(sujungta_geometrija))

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