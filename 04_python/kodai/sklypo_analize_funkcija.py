import geopandas as gpd
from shapely.geometry import Polygon


def analizuoti_sklypa(bp_kelias, sklypo_kelias):
    """
    Ši funkcija:
    1. nuskaito BP sluoksnį
    2. nuskaito sklypo sluoksnį
    3. paverčia sklypo liniją į poligoną
    4. suranda, su kuriuo BP objektu sklypas kertasi
    5. grąžina rezultatą kaip žodyną
    """

    # -----------------------------
    # Nuskaitome duomenis
    # -----------------------------
    bp_gdf = gpd.read_file(bp_kelias)
    sklypas_gdf = gpd.read_file(sklypo_kelias)

    # -----------------------------
    # Paimame sklypo geometriją
    # -----------------------------
    sklypo_geometrija = sklypas_gdf.geometry.iloc[0]

    # Jei geometrija yra linija, paverčiame ją į poligoną
    if sklypo_geometrija.geom_type == "LineString":
        sklypo_poligonas = Polygon(sklypo_geometrija.coords)
    else:
        sklypo_poligonas = sklypo_geometrija

    # Sukuriame GeoDataFrame su poligonu
    sklypas_poly_gdf = gpd.GeoDataFrame(
        {"id": [1]},
        geometry=[sklypo_poligonas],
        crs=sklypas_gdf.crs
    )

    # -----------------------------
    # Randame BP objektus, kurie kertasi su sklypu
    # -----------------------------
    susikirtimai = bp_gdf[bp_gdf.intersects(sklypas_poly_gdf.geometry.iloc[0])]

    # Jei nieko nerandame, grąžiname žinutę
    if len(susikirtimai) == 0:
        return {
            "sekme": False,
            "zinute": "Nepavyko rasti BP zonos, kuri kirstųsi su sklypu."
        }

    # Paimame pirmą rastą objektą
    rastas_objektas = susikirtimai.iloc[0]

    # -----------------------------
    # Sudedame rezultatą į žodyną
    # -----------------------------
    rezultatas = {
        "sekme": True,
        "zona_pavadinimas": rastas_objektas["F_ZON_APR"],
        "zonos_kodas": rastas_objektas["FUNKC_ZON"],
        "uzstatymo_intensyvumas": rastas_objektas["U_INTENS"],
        "max_aukstu_skaicius": rastas_objektas["MAX_AUK_SK"],
        "pagrindine_paskirtis": rastas_objektas["PAGR_PASK"],
        "objekto_nr": rastas_objektas["NR"]
    }

    return rezultatas


# ---------------------------------
# PALEIDIMAS TESTAVIMUI
# ---------------------------------
if __name__ == "__main__":
    bp_kelias = "01_duomenys/bp/bp_funkc.shp"
    sklypo_kelias = "03_eksportai/sklypas.gpkg"

    rezultatas = analizuoti_sklypa(bp_kelias, sklypo_kelias)

    print("=== FUNKCIJOS REZULTATAS ===")
    for raktas, reiksme in rezultatas.items():
        print(f"{raktas}: {reiksme}")