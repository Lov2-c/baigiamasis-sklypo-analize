import folium
import streamlit as st
from folium.plugins import MousePosition

from ui_config import RC_WMS_URL, RC_WMS_LAYERS, PRADINIS_ZOOM


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
            style_function=lambda _: {
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
            style_function=lambda _: {
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
            style_function=lambda _: {
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


def sukurti_automatines_analizes_zemelapi(
    centras: list[float],
    sklypo_geojson: dict,
    automatiniai_sluoksniai: list[dict],
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

    for sluoksnis in automatiniai_sluoksniai:
        folium.GeoJson(
            sluoksnis["geojson"],
            name=sluoksnis["pavadinimas"],
            style_function=lambda _, spalva=sluoksnis["spalva"]: {
                "color": spalva,
                "weight": 2,
                "fillColor": spalva,
                "fillOpacity": 0.35,
            },
        ).add_to(zemelapis)

    folium.GeoJson(
        sklypo_geojson,
        name="Analizuojamas sklypas",
        style_function=lambda _: {
            "color": "#cc0000",
            "weight": 4,
            "fillColor": "#cc0000",
            "fillOpacity": 0.08,
        },
    ).add_to(zemelapis)

    MousePosition(
        position="topright",
        separator=" | ",
        prefix="Koordinatės",
    ).add_to(zemelapis)

    folium.LayerControl().add_to(zemelapis)
    return zemelapis


def parodyti_automatines_vizualizacijos_legenda(automatiniai_sluoksniai: list[dict]):
    if not automatiniai_sluoksniai:
        return

    st.markdown("#### Legenda")

    for sluoksnis in automatiniai_sluoksniai:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; margin-bottom:6px;">
                <div style="
                    width:18px;
                    height:18px;
                    background:{sluoksnis['spalva']};
                    border:1px solid #333;
                    margin-right:8px;
                "></div>
                <div><strong>{sluoksnis['pavadinimas']}</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )