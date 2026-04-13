from pathlib import Path
import sys

import geopandas as gpd
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from ui_bp_texts import BP_ZONU_TEKSTAI
from ui_pdf_report import generuoti_pdf_ataskaita

from ui_config import (
    PROJEKTO_KATALOGAS,
    DB_FAILO_KELIAS,
    PAGRINDINE_LENTELE,
    ATVIRU_SKLYPU_ZIP,
    SUSIEJIMO_CSV,
    ZEMELAPIO_PLOTIS,
    ZEMELAPIO_AUKSTIS,
    ARTIMU_SKLYPU_ATSTUMAS_M,
    SVARBIAUSI_DB_LAUKAI,
    RIBOJIMU_LAUKAI, 
    RANKINES_SZNS_SLUOKSNIAI,
)
from ui_helpers import (
    rodyti_reiksme,
    ar_reiksme_reiksminga,
    normalizuoti_unikalu_nr_ivesti,
    sukurti_geojson_is_gdf,
    gauti_plota_m2,
    gauti_centra_is_geometrijos,
    parodyti_laukus_is_eilutes,
    gauti_lauko_pavadinima,
    suformuoti_bp_zonos_teksta,
)
from ui_data_loaders import (
    nuskaityti_stulpelius_db,
    ieskoti_db_pagal_sklypo_id,
    uzkrauti_atvirus_sklypus,
    uzkrauti_susiejimo_csv,
    ieskoti_aktualiame_sluoksnyje_pagal_unikalu_nr,
    rasti_db_sklypo_id_per_susiejima,
    atrinkti_artimus_sklypus,
    nuskaityti_ikeltas_ribas,
)
from ui_maps import (
    sukurti_zemelapi,
    sukurti_automatines_analizes_zemelapi,
    sukurti_rankines_validacijos_zemelapi,
    parodyti_automatines_vizualizacijos_legenda,
)
from ui_auto_visualization import (
    parengti_automatines_vizualizacijos_duomenis,
)

KODU_KATALOGAS = PROJEKTO_KATALOGAS / "04_python" / "kodai"

if str(KODU_KATALOGAS) not in sys.path:
    sys.path.insert(0, str(KODU_KATALOGAS))

from analizes_servisas import analizuoti_sklypa_pagal_geometrija, NUMATYTAS_BP_KELIAS


def vykdyti_bazine_analize(sklypo_gdf: gpd.GeoDataFrame, saltinis: str):
    rezultatas = analizuoti_sklypa_pagal_geometrija(
        sklypo_gdf=sklypo_gdf,
        bp_kelias=NUMATYTAS_BP_KELIAS,
    )

    st.session_state["naujos_analizes_rezultatas"] = rezultatas
    st.session_state["naujos_analizes_saltinis"] = saltinis

    return rezultatas


def gauti_analizes_saltinio_pavadinima(saltinis: str | None) -> str:
    if saltinis == "aktualus_sklypas":
        return "aktualų rastą sklypą"
    if saltinis == "ikeltos_ribos":
        return "įkeltas ribas"
    return "nenurodytą šaltinį"


def isvalyti_rezultatus():
    raktai = [
        "rasto_db_irasa_dict",
        "rasto_atviro_sklypo_info",
        "rasto_atviro_sklypo_atributai",
        "rasto_sklypo_gdf_3346",
        "pradinio_sklypo_geojson",
        "artimu_sklypu_geojson",
        "zemelapio_centras",
        "db_busena",
        "naujos_analizes_rezultatas",
        "naujos_analizes_saltinis",
    ]
    for raktas in raktai:
        if raktas in st.session_state:
            del st.session_state[raktas]


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
        st.session_state["rasto_sklypo_gdf_3346"] = None
        st.session_state["pradinio_sklypo_geojson"] = None
        st.session_state["artimu_sklypu_geojson"] = None
        st.session_state["zemelapio_centras"] = zemelapio_pradinis_centras
        st.session_state["db_busena"] = "aktualiame_sluoksnyje_nerastas"
        st.session_state["naujos_analizes_rezultatas"] = None
        st.session_state["naujos_analizes_saltinis"] = None
        st.warning("Sklypas pagal šį unikalų numerį aktualiame sluoksnyje nerastas.")
    else:
        st.session_state["rasto_atviro_sklypo_info"] = atviro_info
        st.session_state["rasto_atviro_sklypo_atributai"] = rastas_3346.iloc[0].drop(labels="geometry").to_dict()
        st.session_state["rasto_sklypo_gdf_3346"] = rastas_3346.copy()
        st.session_state["pradinio_sklypo_geojson"] = sukurti_geojson_is_gdf(rastas_4326)
        st.session_state["naujos_analizes_rezultatas"] = None
        st.session_state["naujos_analizes_saltinis"] = None
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
# 9. ANALIZĖS VYKDYMO BLOKAS
# ============================================================

st.subheader("4. Analizės vykdymas")

rasto_sklypo_gdf_3346 = st.session_state.get("rasto_sklypo_gdf_3346")
naujos_analizes_rezultatas = st.session_state.get("naujos_analizes_rezultatas")
naujos_analizes_saltinis = st.session_state.get("naujos_analizes_saltinis")

if not rasto_atviro_sklypo_info or rasto_sklypo_gdf_3346 is None:
    st.info("Pirmiausia rask aktualų sklypą pagal unikalų numerį.")
else:
    col1, col2 = st.columns(2)

    with col1:
        sukurti_analize_paspausta = st.button(
            "Sukurti analizę šiam sklypui",
            use_container_width=True,
        )

    with col2:
        perskaiciuoti_paspausta = st.button(
            "Perskaičiuoti pagal įkeltas ribas",
            use_container_width=True,
            disabled=ikeltos_ribos_3346 is None,
        )

    if sukurti_analize_paspausta:
        with st.spinner("Vykdoma bazinė analizė pagal rasto sklypo geometriją..."):
            rezultatas = vykdyti_bazine_analize(
                sklypo_gdf=rasto_sklypo_gdf_3346,
                saltinis="aktualus_sklypas",
            )

        naujos_analizes_rezultatas = rezultatas
        naujos_analizes_saltinis = "aktualus_sklypas"

    if perskaiciuoti_paspausta:
        with st.spinner("Vykdoma bazinė analizė pagal įkeltas ribas..."):
            rezultatas = vykdyti_bazine_analize(
                sklypo_gdf=ikeltos_ribos_3346,
                saltinis="ikeltos_ribos",
            )

        naujos_analizes_rezultatas = rezultatas
        naujos_analizes_saltinis = "ikeltos_ribos"

    if ikeltos_ribos_3346 is None:
        st.caption("Norint perskaičiuoti pagal naujas ribas, pirmiausia reikia įkelti ribų failą.")

if not naujos_analizes_rezultatas:
    st.info("Dar nepaleista nauja analizė per analizės servisą.")
else:
    sekme = naujos_analizes_rezultatas.get("sekme", False)
    zinute = naujos_analizes_rezultatas.get("zinute", "")
    rezultato_df = naujos_analizes_rezultatas.get("rezultato_df")
    rezultato_dict = naujos_analizes_rezultatas.get("rezultato_dict")
    laikinas_failas = naujos_analizes_rezultatas.get("laikinas_sklypo_failas")

    st.markdown("### Naujos bazinės analizės rezultatas")
    st.write(f"**Analizės šaltinis:** {gauti_analizes_saltinio_pavadinima(naujos_analizes_saltinis)}")

    if sekme:
        st.success(zinute)

        if rezultato_dict:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Pagrindinė BP zona:** {rodyti_reiksme(rezultato_dict.get('pagrindine_zona_pavadinimas'))}")
                st.markdown(f"**Zonos kodas:** {rodyti_reiksme(rezultato_dict.get('pagrindine_zona_kodas'))}")
                st.markdown(f"**Užstatymo intensyvumas:** {rodyti_reiksme(rezultato_dict.get('pagrindine_u_intens'))}")

            with col2:
                st.markdown(f"**Maks. aukštų sk.:** {rodyti_reiksme(rezultato_dict.get('pagrindine_max_auk_sk'))}")
                st.markdown(f"**Pagrindinė paskirtis:** {rodyti_reiksme(rezultato_dict.get('pagrindine_pagr_pask'))}")
                st.markdown(f"**Automatinės analizės rezultatas:** {rodyti_reiksme(rezultato_dict.get('automatines_analizes_rezultatas'))}")

            bp_aprasymo_tekstas = suformuoti_bp_zonos_teksta(
                zonos_kodas=rezultato_dict.get("pagrindine_zona_kodas"),
                zonos_pavadinimas=rezultato_dict.get("pagrindine_zona_pavadinimas"),
                uzstatymo_intensyvumas=rezultato_dict.get("pagrindine_u_intens"),
                pagrindine_paskirtis=rezultato_dict.get("pagrindine_pagr_pask"),
                bp_tekstu_zodynas=BP_ZONU_TEKSTAI,
            )

            st.markdown("#### Bendrojo plano zonos paaiškinimas")
            st.write(bp_aprasymo_tekstas)

        if rezultato_df is not None:
            st.markdown("#### Pilna serviso grąžinta eilutė")
            st.dataframe(rezultato_df, use_container_width=True)

        if laikinas_failas:
            st.caption(f"Laikinas analizės failas: {laikinas_failas}")
    else:
        st.error(zinute)

# ============================================================
# 10. AUTOMATINĖS ANALIZĖS VIZUALINIS BLOKAS
# ============================================================

st.subheader("5. Automatinės analizės vaizdas žemėlapyje")

if not naujos_analizes_rezultatas:
    st.info("Pirmiausia paleisk automatinę analizę.")
else:
    sekme = naujos_analizes_rezultatas.get("sekme", False)

    if not sekme:
        st.info("Automatinės analizės vaizdas bus rodomas tik tada, kai analizė sėkmingai įvykdyta.")
    else:
        if naujos_analizes_saltinis == "ikeltos_ribos" and ikeltos_ribos_3346 is not None:
            vizualizacijos_sklypas_3346 = ikeltos_ribos_3346
        else:
            vizualizacijos_sklypas_3346 = rasto_sklypo_gdf_3346

        if vizualizacijos_sklypas_3346 is None or vizualizacijos_sklypas_3346.empty:
            st.warning("Nėra geometrijos automatinei vizualizacijai.")
        else:
            with st.spinner("Ruošiamas automatinės analizės vaizdas..."):
                automatiniai_sluoksniai, nerasti_automatiniai_failai = parengti_automatines_vizualizacijos_duomenis(
                    vizualizacijos_sklypas_3346
                )

            vizualizacijos_sklypas_4326 = vizualizacijos_sklypas_3346.to_crs(epsg=4326)
            vizualizacijos_sklypo_geojson = sukurti_geojson_is_gdf(vizualizacijos_sklypas_4326)
            vizualizacijos_centras = gauti_centra_is_geometrijos(vizualizacijos_sklypas_4326)

            if not automatiniai_sluoksniai:
                st.info("Šiam sklypui iš automatinei analizei naudojamų vietinių sluoksnių sankirtų nerasta.")
            else:
                zemelapis_auto = sukurti_automatines_analizes_zemelapi(
                    centras=vizualizacijos_centras,
                    sklypo_geojson=vizualizacijos_sklypo_geojson,
                    automatiniai_sluoksniai=automatiniai_sluoksniai,
                )

                st_folium(
                    zemelapis_auto,
                    height=ZEMELAPIO_AUKSTIS,
                    width=ZEMELAPIO_PLOTIS,
                    returned_objects=[],
                    key="automatines_analizes_zemelapis",
                )

                st.caption(
                    "Žemėlapyje rodomas analizuojamas sklypas ir tie automatinės analizės sluoksniai, "
                    "kurie realiai kertasi su sklypu."
                )

                col1, col2 = st.columns([1, 2])

                with col1:
                    parodyti_automatines_vizualizacijos_legenda(automatiniai_sluoksniai)

                with col2:
                    st.markdown("#### Aptikti sluoksniai")
                    santraukos_df = pd.DataFrame(
                        [
                            {
                                "Sluoksnis": s["pavadinimas"],
                                "Grupė": s["grupe"],
                                "Plotas sklype, m²": s["plotas_m2"],
                                "Dalis sklypo, %": s["procentas"],
                                "Kas nustatyta": s["trumpas_aprasymas"],
                            }
                            for s in automatiniai_sluoksniai
                        ]
                    )
                    st.dataframe(santraukos_df, use_container_width=True)

                with st.expander("Rodyti parengtus ataskaitos tekstus"):
                    for s in automatiniai_sluoksniai:
                        st.markdown(f"**{s['pavadinimas']}**")
                        st.write(s["ataskaitos_tekstas"])
                        st.caption(f"Sankirtos plotas: {s['plotas_m2']} m² | Dalis sklypo: {s['procentas']} %")
                        st.markdown("---")

            if nerasti_automatiniai_failai:
                with st.expander("Rodyti nerastus sluoksnių failus"):
                    st.write(
                        "Šie sluoksniai buvo aprašyti vizualizacijai, bet jų failų šioje projekto versijoje nepavyko rasti:"
                    )
                    st.write(nerasti_automatiniai_failai)

# ============================================================
# 11. DB ANALIZĖ
# ============================================================

st.subheader("6. Vidinės DB atitikmuo ir preliminari analizė")

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
                (laukas, rodyti_reiksme(db_eilute[laukas]))
            )

    if ribojimai_rodymui:
        for laukas, reiksme in ribojimai_rodymui:
            st.write(f"- **{laukas}:** {reiksme}")
    else:
        st.write("Reikšmingų ribojimų šiame bloke nerasta arba jie DB dar neužpildyti.")

# ============================================================
# 12. PAPILDOMA RANKINĖ VALIDACIJA
# ============================================================

st.subheader("7. Papildoma rankinė validacija")

st.markdown("### Rankinės validacijos žemėlapis")

rankines_szns = st.multiselect(
    "Pasirink SŽNS, kurias matai per peržiūros sluoksnį ir kurios aktualios šiam sklypui",
    options=list(RANKINES_SZNS_SLUOKSNIAI.keys()),
)

if not rasto_atviro_sklypo_info or pradinio_sklypo_geojson is None:
    st.info("Pirmiausia rask aktualų sklypą, kad būtų galima rodyti rankinės validacijos žemėlapį.")
else:
    if (
        naujos_analizes_saltinis == "ikeltos_ribos"
        and ikeltu_ribu_geojson is not None
        and ikeltos_ribos_4326 is not None
    ):
        rankinio_zemelapio_geojson = ikeltu_ribu_geojson
        rankinio_zemelapio_centras = gauti_centra_is_geometrijos(ikeltos_ribos_4326)
    else:
        rankinio_zemelapio_geojson = pradinio_sklypo_geojson
        if st.session_state.get("rasto_sklypo_gdf_3346") is not None:
            rankinio_zemelapio_centras = zemelapio_centras
        else:
            rankinio_zemelapio_centras = zemelapio_pradinis_centras

    rankinis_zemelapis = sukurti_rankines_validacijos_zemelapi(
        centras=rankinio_zemelapio_centras,
        sklypo_geojson=rankinio_zemelapio_geojson,
        pasirinktos_rankines_szns=rankines_szns,
        rankiniu_szns_sluoksniai=RANKINES_SZNS_SLUOKSNIAI,
    )

    st_folium(
        rankinis_zemelapis,
        height=ZEMELAPIO_AUKSTIS,
        width=ZEMELAPIO_PLOTIS,
        returned_objects=[],
        key="rankines_validacijos_zemelapis",
    )

    st.caption(
        "Žemėlapyje rodomas sklypas, RC kadastro sluoksnis ir rankiniu būdu pasirinkti SŽNS sluoksniai."
    )

if rankines_szns:
    st.markdown("### Pasirinktos rankinės SŽNS")
    for pavadinimas in rankines_szns:
        st.write(f"- **{pavadinimas}**")

    st.markdown("### Rankinių SŽNS legenda")
    for pavadinimas in rankines_szns:
        info = RANKINES_SZNS_SLUOKSNIAI.get(pavadinimas, {})
        spalva = info.get("spalva", "#999999")

        st.markdown(
            f"""
            <div style="display:flex; align-items:center; margin-bottom:6px;">
                <div style="
                    width:18px;
                    height:18px;
                    background:{spalva};
                    border:1px solid #333;
                    margin-right:8px;
                "></div>
                <div><strong>{pavadinimas}</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info("Kol kas rankiniu būdu nepasirinkta nė viena papildoma SŽNS.")

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
                "SŽNS peržiūros sluoksnis",
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
        placeholder="Pvz. Įvertinus SŽNS peržiūros sluoksnį nustatyta, kad sklypo dalyje galioja papildomos sąlygos.",
        height=120,
    )

    galutinio_sprendimo_paaiskinimas = st.text_area(
        "Galutinio sprendimo paaiškinimas",
        placeholder="Pvz. Statyba galima tik ne apribotoje sklypo dalyje, būtina papildoma projektinė analizė.",
        height=120,
    )

    st.markdown("### Rankinės validacijos santrauka")
    st.write(f"**Pasirinktos rankinės SŽNS:** {', '.join(rankines_szns) if rankines_szns else '—'}")
    st.write(f"**SŽNS vertinimas:** {szns_rezultatas}")
    st.write(f"**Peržiūrėti papildomi sluoksniai:** {', '.join(papildomi_sluoksniai) if papildomi_sluoksniai else '—'}")
    st.write(f"**Galutinis sprendimas:** {galutinis_sprendimas}")
    st.write(f"**Reikia papildomos rankinės patikros:** {'Taip' if reikia_papildomos_rankines_patiktros else 'Ne'}")
    st.write(f"**Rankinės validacijos pastaba:** {rankines_validacijos_pastaba if rankines_validacijos_pastaba.strip() else '—'}")
    st.write(f"**Galutinio sprendimo paaiškinimas:** {galutinio_sprendimo_paaiskinimas if galutinio_sprendimo_paaiskinimas.strip() else '—'}")

# ============================================================
# PDF ATASKAITA
# ============================================================

st.subheader("8. PDF ataskaita")

if not naujos_analizes_rezultatas:
    st.info("Pirmiausia paleisk automatinę analizę, kad būtų galima generuoti PDF ataskaitą.")
else:
    rezultato_dict = naujos_analizes_rezultatas.get("rezultato_dict")

    # Laikinas ML rezultatas PDF blokui.
    # Čia kol kas gali įrašyti reikšmę ranka arba vėliau prijungti realią MLP prognozę.
    # Pvz.:
    ml_prognoze = "vystymas_galimas_su_salygomis"

    # Jei turi sugeneruotą BP tekstą
    bp_zonos_tekstas = None
    if rezultato_dict:
        bp_zonos_tekstas = suformuoti_bp_zonos_teksta(
            zonos_kodas=rezultato_dict.get("pagrindine_zona_kodas"),
            zonos_pavadinimas=rezultato_dict.get("pagrindine_zona_pavadinimas"),
            uzstatymo_intensyvumas=rezultato_dict.get("pagrindine_u_intens"),
            pagrindine_paskirtis=rezultato_dict.get("pagrindine_pagr_pask"),
            bp_tekstu_zodynas=BP_ZONU_TEKSTAI,
        )

    rankines_validacijos_santrauka = {
        "szns_rezultatas": szns_rezultatas if "szns_rezultatas" in locals() else None,
        "galutinis_sprendimas": galutinis_sprendimas if "galutinis_sprendimas" in locals() else None,
        "papildoma_patikra": "Taip" if ("reikia_papildomos_rankines_patiktros" in locals() and reikia_papildomos_rankines_patiktros) else "Ne",
        "pastaba": rankines_validacijos_pastaba if "rankines_validacijos_pastaba" in locals() else None,
        "paaiskinimas": galutinio_sprendimo_paaiskinimas if "galutinio_sprendimo_paaiskinimas" in locals() else None,
    }

    pdf_sklypo_geojson = None
    if "vizualizacijos_sklypo_geojson" in locals():
        pdf_sklypo_geojson = vizualizacijos_sklypo_geojson
    elif naujos_analizes_saltinis == "ikeltos_ribos" and ikeltu_ribu_geojson is not None:
        pdf_sklypo_geojson = ikeltu_ribu_geojson
    else:
        pdf_sklypo_geojson = pradinio_sklypo_geojson

    pdf_bytes = generuoti_pdf_ataskaita(
        rasto_atviro_sklypo_info=rasto_atviro_sklypo_info,
        rasto_atviro_sklypo_atributai=rasto_atviro_sklypo_atributai,
        rezultato_dict=rezultato_dict,
        automatiniai_sluoksniai=automatiniai_sluoksniai if "automatiniai_sluoksniai" in locals() else [],
        ml_prognoze=ml_prognoze,
        bp_zonos_tekstas=bp_zonos_tekstas,
        sklypo_geojson=pdf_sklypo_geojson,
        rankines_validacijos_santrauka=rankines_validacijos_santrauka,
    )

    st.download_button(
        label="Atsisiųsti PDF ataskaitą",
        data=pdf_bytes,
        file_name="sklypo_ataskaita.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

# ============================================================
# 14. APAČIOS INFORMACIJA
# ============================================================

st.markdown("---")
st.caption(
    "Dabartinė versija: paieška pagal aktualų sklypų sluoksnį + sklypo vaizdas žemėlapyje + "
    "aktualių ribų įkėlimas + DB analizės patikra + rankinė validacija."
)