from pathlib import Path
import tempfile
import uuid

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString
from shapely.ops import unary_union, polygonize

from features_ruosimas import paruosti_features


# ============================================================
# 1. BENDRI NUSTATYMAI
# ============================================================

PROJEKTO_KATALOGAS = Path(__file__).resolve().parents[2]

# SVARBU:
# Čia įrašyk tikrą savo BP sluoksnio kelią.
# Jei pas tave jis yra kitur – pakeisk šitą kelią.
NUMATYTAS_BP_KELIAS = PROJEKTO_KATALOGAS / "01_duomenys" / "bp" / "bp_funkc.shp"


# ============================================================
# 2. PAGALBINĖS FUNKCIJOS
# ============================================================

def gauti_saugia_geometrija(geometrija):
    """
    Bando iš įvairių geometrijų gauti poligoną.

    Palaikomi atvejai:
    - Polygon
    - MultiPolygon
    - LineString
    - MultiLineString

    Jei geometrija yra linijinė, bandome ją paversti poligonu.
    """
    if geometrija is None:
        raise ValueError("Gauta tuščia geometrija.")

    geom_tip = geometrija.geom_type

    if geom_tip == "Polygon":
        return geometrija

    if geom_tip == "MultiPolygon":
        # Jei keli poligonai, sujungiame į vieną bendrą geometriją
        return unary_union(geometrija)

    if geom_tip == "LineString":
        # Jei tai uždaras kontūras – bandom formuoti poligoną
        try:
            return Polygon(geometrija.coords)
        except Exception:
            sugeneruoti_poligonai = list(polygonize(geometrija))
            if sugeneruoti_poligonai:
                return unary_union(sugeneruoti_poligonai)
            raise ValueError("LineString geometrijos nepavyko paversti poligonu.")

    if geom_tip == "MultiLineString":
        sujungta = unary_union(geometrija)
        sugeneruoti_poligonai = list(polygonize(sujungta))
        if sugeneruoti_poligonai:
            return unary_union(sugeneruoti_poligonai)
        raise ValueError("MultiLineString geometrijos nepavyko paversti poligonu.")

    raise ValueError(f"Nepalaikomas geometrijos tipas: {geom_tip}")


def paruosti_vieno_sklypo_gdf(sklypo_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Paruošia vieno sklypo GeoDataFrame analizei:
    - patikrina, ar nėra tuščias
    - paima pirmą geometriją
    - paverčia ją poligonu, jei reikia
    - išlaiko CRS
    """
    if sklypo_gdf is None or sklypo_gdf.empty:
        raise ValueError("Sklypo GeoDataFrame tuščias.")

    if sklypo_gdf.crs is None:
        raise ValueError("Sklypo GeoDataFrame neturi CRS.")

    pirma_geometrija = sklypo_gdf.geometry.iloc[0]

    if pirma_geometrija is None:
        raise ValueError("Pirmo įrašo geometrija yra tuščia.")

    saugi_geometrija = gauti_saugia_geometrija(pirma_geometrija)

    rezultatas_gdf = gpd.GeoDataFrame(
        {"objekto_tipas": ["sklypas"]},
        geometry=[saugi_geometrija],
        crs=sklypo_gdf.crs,
    )

    return rezultatas_gdf


def issaugoti_laikina_sklypo_faila(sklypo_gdf: gpd.GeoDataFrame) -> Path:
    """
    Išsaugo vieno sklypo GeoDataFrame kaip laikiną GPKG failą.
    """
    laikinas_katalogas = Path(tempfile.gettempdir()) / "baigiamasis_laikini_sklypai"
    laikinas_katalogas.mkdir(parents=True, exist_ok=True)

    failo_pavadinimas = f"sklypas_{uuid.uuid4().hex}.gpkg"
    failo_kelias = laikinas_katalogas / failo_pavadinimas

    sklypo_gdf.to_file(failo_kelias, driver="GPKG")

    return failo_kelias


def normalizuoti_rezultato_stulpelius(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sutvarko stulpelių pavadinimus į vienodesnį, UI draugiškesnį variantą.
    """
    if df is None or df.empty:
        return df

    pervadinimai = {
        "zona_pavadinimas": "pagrindine_zona_pavadinimas",
        "zonos_kodas": "pagrindine_zona_kodas",
        "uzstatymo_intensyvumas": "pagrindine_u_intens",
        "max_aukstu_skaicius": "pagrindine_max_auk_sk",
        "pagrindine_paskirtis": "pagrindine_pagr_pask",
        "preliminari_klase": "automatines_analizes_rezultatas",
        "objekto_nr": "bp_objekto_nr",
    }

    esami_pervadinimai = {
        senas: naujas
        for senas, naujas in pervadinimai.items()
        if senas in df.columns
    }

    df = df.rename(columns=esami_pervadinimai)

    return df


# ============================================================
# 3. PAGRINDINĖ SERVISO FUNKCIJA
# ============================================================

def analizuoti_sklypa_pagal_geometrija(
    sklypo_gdf: gpd.GeoDataFrame,
    bp_kelias: str | Path | None = None,
):
    """
    Pagrindinė funkcija, kurią vėliau kvies UI.

    Veikimo logika:
    1. paruošia sklypo geometriją
    2. išsaugo laikiną GPKG
    3. paleidžia jau turimą paruosti_features(...)
    4. grąžina rezultatą kaip žodyną

    Grąžinamas žodynas:
    {
        "sekme": True/False,
        "zinute": "...",
        "rezultato_df": DataFrame arba None,
        "rezultato_dict": dict arba None,
        "laikinas_sklypo_failas": "...",
    }
    """
    try:
        if bp_kelias is None:
            bp_kelias = NUMATYTAS_BP_KELIAS

        bp_kelias = Path(bp_kelias)

        if not bp_kelias.exists():
            return {
                "sekme": False,
                "zinute": f"Nerastas BP failas: {bp_kelias}",
                "rezultato_df": None,
                "rezultato_dict": None,
                "laikinas_sklypo_failas": None,
            }

        paruostas_sklypo_gdf = paruosti_vieno_sklypo_gdf(sklypo_gdf)
        laikinas_sklypo_failas = issaugoti_laikina_sklypo_faila(paruostas_sklypo_gdf)

        rezultato_df, klaida = paruosti_features(
            bp_kelias=str(bp_kelias),
            sklypo_kelias=str(laikinas_sklypo_failas),
        )

        if rezultato_df is None:
            return {
                "sekme": False,
                "zinute": f"Analizė nepavyko: {klaida}",
                "rezultato_df": None,
                "rezultato_dict": None,
                "laikinas_sklypo_failas": str(laikinas_sklypo_failas),
            }

        rezultato_df = normalizuoti_rezultato_stulpelius(rezultato_df)

        rezultato_dict = rezultato_df.iloc[0].to_dict()

        return {
            "sekme": True,
            "zinute": "Bazinis sklypo analizės rezultatas sėkmingai apskaičiuotas.",
            "rezultato_df": rezultato_df,
            "rezultato_dict": rezultato_dict,
            "laikinas_sklypo_failas": str(laikinas_sklypo_failas),
        }

    except Exception as klaida:
        return {
            "sekme": False,
            "zinute": f"Įvyko klaida analizuojant sklypą: {klaida}",
            "rezultato_df": None,
            "rezultato_dict": None,
            "laikinas_sklypo_failas": None,
        }


# ============================================================
# 4. TESTAVIMO BLOKAS
# ============================================================

if __name__ == "__main__":
    print("=== ANALIZĖS SERVISO TESTAS ===")

    testinio_sklypo_kelias = PROJEKTO_KATALOGAS / "03_eksportai" / "sklypas.gpkg"

    if not testinio_sklypo_kelias.exists():
        print(f"Nerastas testinis failas: {testinio_sklypo_kelias}")
    else:
        sklypo_gdf = gpd.read_file(testinio_sklypo_kelias)

        rezultatas = analizuoti_sklypa_pagal_geometrija(
            sklypo_gdf=sklypo_gdf,
            bp_kelias=NUMATYTAS_BP_KELIAS,
        )

        print("\n=== SERVISO REZULTATAS ===")
        print("Sekmė:", rezultatas["sekme"])
        print("Žinutė:", rezultatas["zinute"])
        print("Laikinas sklypo failas:", rezultatas["laikinas_sklypo_failas"])

        if rezultatas["rezultato_df"] is not None:
            print("\n=== REZULTATO DATAFRAME ===")
            print(rezultatas["rezultato_df"])