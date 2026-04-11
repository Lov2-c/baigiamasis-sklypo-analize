import folium
import streamlit as st
from folium.plugins import MousePosition

from ui_config import (
    RC_WMS_URL,
    RC_WMS_LAYERS,
    RC_SZNS_WMS_URL,
    PRADINIS_ZOOM,
)


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


def sukurti_rankines_validacijos_zemelapi(
    centras: list[float],
    sklypo_geojson: dict | None,
    pasirinktos_rankines_szns: list[str],
    rankiniu_szns_sluoksniai: dict,
):
    zemelapis = folium.Map(
        location=centras,
        zoom_start=PRADINIS_ZOOM,
        control_scale=True,
        tiles="OpenStreetMap",
    )

    # RC kadastro sluoksnis
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

    # Rankiniu būdu pasirinkti SŽNS sluoksniai
    for pavadinimas in pasirinktos_rankines_szns:
        info = rankiniu_szns_sluoksniai.get(pavadinimas)

        if not info:
            continue

        folium.raster_layers.WmsTileLayer(
            url=RC_SZNS_WMS_URL,
            name=pavadinimas,
            layers=info["layer_id"],
            fmt="image/png",
            transparent=True,
            version="1.1.1",
            attr="Geoportal / Registrų centras",
            overlay=True,
            control=True,
            show=True,
        ).add_to(zemelapis)

    # Analizuojamo sklypo riba
    if sklypo_geojson:
        folium.GeoJson(
            sklypo_geojson,
            name="Analizuojamas sklypas",
            style_function=lambda _: {
                "color": "#d7191c",
                "weight": 4,
                "fillColor": "#d7191c",
                "fillOpacity": 0.08,
            },
        ).add_to(zemelapis)

    MousePosition(
        position="topright",
        separator=" | ",
        prefix="Koordinatės",
    ).add_to(zemelapis)

    folium.LayerControl(collapsed=False).add_to(zemelapis)

    return zemelapis

    # Bazinis RC kadastro sluoksnis
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

    # Tik rankiniu būdu pasirinkti SŽNS sluoksniai
    for pavadinimas in pasirinktos_rankines_szns:
        info = rankiniu_szns_sluoksniai.get(pavadinimas)
        if not info:
            continue

        folium.raster_layers.WmsTileLayer(
            url=RC_SZNS_WMS_URL,
            name=pavadinimas,
            layers=info["layer_id"],
            fmt="image/png",
            transparent=True,
            version="1.1.1",
            attr="Geoportal / Registrų centras",
            overlay=True,
            control=True,
            show=True,
        ).add_to(zemelapis)

    # Sklypo riba
    if sklypo_geojson:
        folium.GeoJson(
            sklypo_geojson,
            name="Analizuojamas sklypas",
            style_function=lambda _: {
                "color": "#d7191c",
                "weight": 4,
                "fillColor": "#d7191c",
                "fillOpacity": 0.08,
            },
        ).add_to(zemelapis)

    MousePosition(
        position="topright",
        separator=" | ",
        prefix="Koordinatės",
    ).add_to(zemelapis)

    folium.LayerControl(collapsed=False).add_to(zemelapis)
    return zemelapis

    # 1. Tas pats RC kadastro WMS, kuris jau veikia kituose žemėlapiuose
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

    # 2. SŽNS peržiūros sluoksnis per WMS
    folium.raster_layers.WmsTileLayer(
        url=RC_SZNS_WMS_URL,
        name="SŽNS peržiūros sluoksnis",
        layers="0",
        fmt="image/png",
        transparent=True,
        version="1.1.1",
        attr="Geoportal / Registrų centras",
        overlay=True,
        control=True,
        show=True,
    ).add_to(zemelapis)

    # 3. Sklypo riba
    if sklypo_geojson:
        folium.GeoJson(
            sklypo_geojson,
            name="Analizuojamas sklypas",
            style_function=lambda _: {
                "color": "#d7191c",
                "weight": 4,
                "fillColor": "#d7191c",
                "fillOpacity": 0.08,
            },
        ).add_to(zemelapis)

    MousePosition(
        position="topright",
        separator=" | ",
        prefix="Koordinatės",
    ).add_to(zemelapis)

    folium.LayerControl(collapsed=False).add_to(zemelapis)
    return zemelapis

    # 1. Kadastro / sklypų bazinis sluoksnis
    folium.TileLayer(
        tiles=(
            f"{RC_KADASTRO_MAPSERVER_URL}/tile/"
            "{z}/{y}/{x}"
        ),
        name="Kadastro žemėlapis",
        attr="Geoportal / Registrų centras",
        overlay=False,
        control=True,
        show=True,
    ).add_to(zemelapis)

    # 2. SŽNS peržiūros sluoksnis
    folium.TileLayer(
        tiles=(
            f"{RC_SZNS_MAPSERVER_URL}/tile/"
            "{z}/{y}/{x}"
        ),
        name="SŽNS peržiūros sluoksnis",
        attr="Geoportal / Registrų centras",
        overlay=True,
        control=True,
        show=True,
        opacity=0.75,
    ).add_to(zemelapis)

    # 3. Sklypo riba viršuje
    if sklypo_geojson:
        folium.GeoJson(
            sklypo_geojson,
            name="Analizuojamas sklypas",
            style_function=lambda _feature: {
                "color": "#d7191c",
                "weight": 4,
                "fillColor": "#d7191c",
                "fillOpacity": 0.08,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=[],
                aliases=[],
                sticky=False,
                labels=False,
            ),
        ).add_to(zemelapis)

    folium.LayerControl(collapsed=False).add_to(zemelapis)

    return zemelapis