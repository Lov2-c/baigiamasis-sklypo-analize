import geopandas as gpd
from shapely.geometry import Polygon

# -----------------------------------
# FAILŲ KELIAI
# -----------------------------------
bp_kelias = "01_duomenys/bp/bp_funkc.shp"
sklypo_kelias = "03_eksportai/sklypas.gpkg"

# -----------------------------------
# DUOMENŲ NUSKAITYMAS
# -----------------------------------
bp_gdf = gpd.read_file(bp_kelias)
sklypas_gdf = gpd.read_file(sklypo_kelias)

# -----------------------------------
# PATIKRINAME PRADINIUS DUOMENIS
# -----------------------------------
print("=== PRADINĖ INFORMACIJA ===")
print("BP CRS:", bp_gdf.crs)
print("Sklypo CRS:", sklypas_gdf.crs)
print("Sklypo geometrijos tipas:", sklypas_gdf.geometry.iloc[0].geom_type)
print()

# -----------------------------------
# LINESTRING -> POLYGON
# -----------------------------------
# Kadangi sklypas yra kontūro linija, iš jos bandome sukurti poligoną.
linija = sklypas_gdf.geometry.iloc[0]

# Paimame linijos koordinates ir iš jų sukuriame poligoną.
sklypo_poligonas = Polygon(linija.coords)

# Sukuriame naują GeoDataFrame su poligonu.
sklypas_poly_gdf = gpd.GeoDataFrame(
    {"id": [1]},
    geometry=[sklypo_poligonas],
    crs=sklypas_gdf.crs
)

print("=== PO PAVERTIMO ===")
print("Naujas geometrijos tipas:", sklypas_poly_gdf.geometry.iloc[0].geom_type)
print()

# -----------------------------------
# PERSIDENGIMO PAIEŠKA
# -----------------------------------
# Ieškome BP objektų, kurie kertasi su sklypo poligonu.
susikirtimai = bp_gdf[bp_gdf.intersects(sklypas_poly_gdf.geometry.iloc[0])]

print("=== SUSIKIRTIMAI SU BP ===")
print("Rastų objektų skaičius:", len(susikirtimai))
print()

# Parodome svarbiausius stulpelius, jei susikirtimų yra.
if len(susikirtimai) > 0:
    svarbus_stulpeliai = ["F_ZON_APR", "U_INTENS", "MAX_AUK_SK", "PAGR_PASK", "FUNKC_ZON", "NR"]
    print(susikirtimai[svarbus_stulpeliai])
    print()
    
    # Pasiimame pirmą rastą BP objektą
    rastas_objektas = susikirtimai.iloc[0]

    print("=== ŽMOGUI SUPRANTAMAS REZULTATAS ===")
    print("Rasta funkcinė zona:", rastas_objektas["F_ZON_APR"])
    print("Funkcinės zonos kodas:", rastas_objektas["FUNKC_ZON"])
    print("Užstatymo intensyvumas:", rastas_objektas["U_INTENS"])
    print("Maksimalus aukštų skaičius:", rastas_objektas["MAX_AUK_SK"])
    print("Pagrindinė paskirtis:", rastas_objektas["PAGR_PASK"])
    print("Objekto numeris:", rastas_objektas["NR"])
else:
    print("Susikirtimų nerasta.")