import json
import re

import geopandas as gpd
import pandas as pd
import streamlit as st

from ui_config import LAUKU_PAVADINIMAI


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


def gauti_centra_is_geometrijos(gdf_4326: gpd.GeoDataFrame) -> list[float]:
    centroid = gdf_4326.geometry.iloc[0].centroid
    return [centroid.y, centroid.x]


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