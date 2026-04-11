from pathlib import Path

import geopandas as gpd
import streamlit as st

from ui_config import AUTOMATINES_VIZUALIZACIJOS_SLUOKSNIAI
from ui_helpers import sukurti_geojson_is_gdf, uzpildyti_ploto_sablona
from ui_layer_texts import SLUOKSNIU_TEKSTAI


def gauti_pirma_esanti_kelia(galimi_keliai: list[Path]) -> Path | None:
    for kelias in galimi_keliai:
        if kelias.exists():
            return kelias
    return None


@st.cache_resource(show_spinner=False)
def uzkrauti_automatines_vizualizacijos_sluoksni(sluoksnio_kelias: str) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(sluoksnio_kelias)

    if gdf.empty:
        return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:3346")

    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=3346)

    gdf = gdf[gdf.geometry.notna()].copy()
    gdf = gdf[~gdf.geometry.is_empty].copy()

    if gdf.empty:
        return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:3346")

    gdf_3346 = gdf.to_crs(epsg=3346).copy()

    try:
        gdf_3346.geometry = gdf_3346.geometry.buffer(0)
    except Exception:
        pass

    gdf_3346 = gdf_3346[gdf_3346.geometry.notna()].copy()
    gdf_3346 = gdf_3346[~gdf_3346.geometry.is_empty].copy()

    return gdf_3346


def apskaiciuoti_sluoksnio_sankirta(sklypo_gdf_3346: gpd.GeoDataFrame, sluoksnio_gdf_3346: gpd.GeoDataFrame):
    if sklypo_gdf_3346 is None or sklypo_gdf_3346.empty:
        return None

    if sluoksnio_gdf_3346 is None or sluoksnio_gdf_3346.empty:
        return None

    sklypas = sklypo_gdf_3346.copy()
    sklypas = sklypas[sklypas.geometry.notna()].copy()
    sklypas = sklypas[~sklypas.geometry.is_empty].copy()

    if sklypas.empty:
        return None

    try:
        sklypas.geometry = sklypas.geometry.buffer(0)
    except Exception:
        pass

    sklypo_geometrija = sklypas.geometry.iloc[0]

    kandidatai = sluoksnio_gdf_3346[sluoksnio_gdf_3346.geometry.intersects(sklypo_geometrija)].copy()

    if kandidatai.empty:
        return None

    try:
        kandidatai.geometry = kandidatai.geometry.buffer(0)
    except Exception:
        pass

    try:
        sankirta = gpd.overlay(
            sklypas[["geometry"]],
            kandidatai[["geometry"]],
            how="intersection",
        )
    except Exception:
        return None

    if sankirta.empty:
        return None

    sankirta = sankirta[sankirta.geometry.notna()].copy()
    sankirta = sankirta[~sankirta.geometry.is_empty].copy()

    if sankirta.empty:
        return None

    sankirtos_plotas_m2 = float(sankirta.geometry.area.sum())
    sklypo_plotas_m2 = float(sklypas.geometry.area.sum())

    if sklypo_plotas_m2 <= 0 or sankirtos_plotas_m2 <= 0:
        return None

    procentas = round((sankirtos_plotas_m2 / sklypo_plotas_m2) * 100, 2)

    return {
        "sankirta_3346": sankirta,
        "plotas_m2": round(sankirtos_plotas_m2, 2),
        "procentas": procentas,
    }


def parengti_automatines_vizualizacijos_duomenis(sklypo_gdf_3346: gpd.GeoDataFrame):
    rezultatai = []
    nerasti_failai = []

    for sluoksnis in AUTOMATINES_VIZUALIZACIJOS_SLUOKSNIAI:
        rastas_kelias = gauti_pirma_esanti_kelia(sluoksnis["galimi_keliai"])

        if rastas_kelias is None:
            nerasti_failai.append(sluoksnis["pavadinimas"])
            continue

        try:
            sluoksnio_gdf_3346 = uzkrauti_automatines_vizualizacijos_sluoksni(str(rastas_kelias))
            sankirta_info = apskaiciuoti_sluoksnio_sankirta(
                sklypo_gdf_3346=sklypo_gdf_3346,
                sluoksnio_gdf_3346=sluoksnio_gdf_3346,
            )

            if not sankirta_info:
                continue

            sankirta_4326 = sankirta_info["sankirta_3346"].to_crs(epsg=4326)

            tekstu_blokas = SLUOKSNIU_TEKSTAI.get(
                sluoksnis["kodas"],
                {
                    "trumpas": sluoksnis["pavadinimas"],
                    "ataskaitai": "Šiam sluoksniui ataskaitinis tekstas dar neparengtas.",
                },
            )

            ataskaitos_tekstas = uzpildyti_ploto_sablona(
                tekstu_blokas["ataskaitai"],
                sankirta_info["plotas_m2"],
                sankirta_info["procentas"],
            )

            rezultatai.append(
                {
                    "kodas": sluoksnis["kodas"],
                    "pavadinimas": sluoksnis["pavadinimas"],
                    "grupe": sluoksnis["grupe"],
                    "spalva": sluoksnis["spalva"],
                    "trumpas_aprasymas": tekstu_blokas["trumpas"],
                    "ataskaitos_tekstas": ataskaitos_tekstas,
                    "sluoksnio_kelias": str(rastas_kelias),
                    "plotas_m2": sankirta_info["plotas_m2"],
                    "procentas": sankirta_info["procentas"],
                    "geojson": sukurti_geojson_is_gdf(sankirta_4326),
                }
            )
        except Exception:
            continue

    rezultatai = sorted(
        rezultatai,
        key=lambda x: (-x["procentas"], x["pavadinimas"]),
    )

    return rezultatai, nerasti_failai