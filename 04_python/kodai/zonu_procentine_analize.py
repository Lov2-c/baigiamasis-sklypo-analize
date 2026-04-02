import geopandas as gpd
import pandas as pd


# -----------------------------------
# FAILŲ KELIAI
# -----------------------------------
bp_kelias = "01_duomenys/bp/bp_funkc.shp"
sklypo_kelias = "03_eksportai/sklypas.gpkg"


# -----------------------------------
# 1. NUSKAITOME DUOMENIS
# -----------------------------------
bp_gdf = gpd.read_file(bp_kelias)
sklypas_gdf = gpd.read_file(sklypo_kelias)


# -----------------------------------
# 2. PATIKRINAME CRS
# -----------------------------------
print("=== CRS PATIKRINIMAS ===")
print("BP CRS:", bp_gdf.crs)
print("Sklypo CRS:", sklypas_gdf.crs)
print()


# -----------------------------------
# 3. JEI SKLYPAS YRA LINESTRING,
#    PAVERČIAME JĮ Į POLIGONĄ
# -----------------------------------
sklypo_geometrija = sklypas_gdf.geometry.iloc[0]

if sklypo_geometrija.geom_type == "LineString":
    # Iš linijos taškų sukuriame poligoną
    from shapely.geometry import Polygon
    sklypo_poligonas = Polygon(sklypo_geometrija.coords)

elif sklypo_geometrija.geom_type == "Polygon":
    sklypo_poligonas = sklypo_geometrija

else:
    raise ValueError(f"Nepalaikomas sklypo geometrijos tipas: {sklypo_geometrija.geom_type}")


# Sukuriame naują GeoDataFrame su vienu poligonu
sklypas_poly_gdf = gpd.GeoDataFrame(
    {"id": [1]},
    geometry=[sklypo_poligonas],
    crs=sklypas_gdf.crs
)


# -----------------------------------
# 4. APSKAIČIUOJAME SKLYPO PLOTĄ
# -----------------------------------
viso_sklypo_plotas = sklypas_poly_gdf.geometry.iloc[0].area

print("=== SKLYPO INFORMACIJA ===")
print("Sklypo geometrijos tipas po pavertimo:", sklypas_poly_gdf.geometry.iloc[0].geom_type)
print("Viso sklypo plotas:", round(viso_sklypo_plotas, 2), "kv. m")
print()


# -----------------------------------
# 5. RANDAME TIK TAS BP ZONAS,
#    KURIOS KERTASI SU SKLYPU
# -----------------------------------
bp_susikirtimai = bp_gdf[bp_gdf.intersects(sklypas_poly_gdf.geometry.iloc[0])].copy()

print("=== RASTOS BP ZONOS ===")
print("Kertančių BP objektų skaičius:", len(bp_susikirtimai))
print()


# -----------------------------------
# 6. APSKAIČIUOJAME TIKRĄ SUSIKIRTIMO GEOMETRIJĄ
# -----------------------------------
# Kiekvienai BP zonai apskaičiuojame tik tą dalį,
# kuri realiai patenka į sklypą.
bp_susikirtimai["susikirtimo_geom"] = bp_susikirtimai.geometry.intersection(
    sklypas_poly_gdf.geometry.iloc[0]
)

# Apskaičiuojame kiekvieno susikirtimo plotą
bp_susikirtimai["susikirtimo_plotas"] = bp_susikirtimai["susikirtimo_geom"].area

# Apskaičiuojame procentą nuo viso sklypo ploto
bp_susikirtimai["susikirtimo_procentas"] = (
    bp_susikirtimai["susikirtimo_plotas"] / viso_sklypo_plotas * 100
)


# -----------------------------------
# 7. PALIEKAME SVARBIAUSIUS STULPELIUS
# -----------------------------------
rezultatu_lentele = bp_susikirtimai[
    [
        "F_ZON_APR",
        "FUNKC_ZON",
        "U_INTENS",
        "MAX_AUK_SK",
        "PAGR_PASK",
        "susikirtimo_plotas",
        "susikirtimo_procentas"
    ]
].copy()


# -----------------------------------
# 8. APVALINAME REIKŠMES,
#    KAD BŪTŲ GRAŽIAU
# -----------------------------------
rezultatu_lentele["susikirtimo_plotas"] = rezultatu_lentele["susikirtimo_plotas"].round(2)
rezultatu_lentele["susikirtimo_procentas"] = rezultatu_lentele["susikirtimo_procentas"].round(2)


# -----------------------------------
# 9. IŠRŪŠIUOJAME PAGAL DIDŽIAUSIĄ PROCENTĄ
# -----------------------------------
rezultatu_lentele = rezultatu_lentele.sort_values(
    by="susikirtimo_procentas",
    ascending=False
)


# -----------------------------------
# 10. IŠVEDAME REZULTATĄ
# -----------------------------------
print("=== BP ZONŲ PROCENTINĖ ANALIZĖ ===")
print(rezultatu_lentele)
print()


# -----------------------------------
# 11. ŽMOGUI SUPRANTAMA SANTRAUKA
# -----------------------------------
print("=== SANTRAUKA ===")
for _, eilute in rezultatu_lentele.iterrows():
    print(
        f"{eilute['susikirtimo_procentas']} % sklypo patenka į zoną "
        f"„{eilute['F_ZON_APR']}“ "
        f"(kodas: {eilute['FUNKC_ZON']})"
    )