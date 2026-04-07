import geopandas as gpd

# -----------------------------------
# FAILO KELIAS
# -----------------------------------
sklypu_kelias = "01_duomenys/sklypai/klaipedos_raj_ribos_2019.gpkg"

# -----------------------------------
# NUSKAITOME SKLYPŲ SLUOKSNĮ
# -----------------------------------
sklypai_gdf = gpd.read_file(sklypu_kelias)

# -----------------------------------
# BENDRA INFORMACIJA
# -----------------------------------
print("=== SKLYPŲ SLUOKSNIO INFORMACIJA ===")
print("Eilučių skaičius:", len(sklypai_gdf))
print("CRS:", sklypai_gdf.crs)
print("Geometrijos tipas:", sklypai_gdf.geometry.iloc[0].geom_type)
print()

# -----------------------------------
# STULPELIŲ PAVADINIMAI
# -----------------------------------
print("=== STULPELIAI ===")
print(sklypai_gdf.columns.tolist())
print()

# -----------------------------------
# PIRMOS EILUTĖS
# -----------------------------------
print("=== PIRMOS 5 EILUTĖS ===")
print(sklypai_gdf.head())
print()

# -----------------------------------
# PASIRINKTI SVARBŪS LAUKAI
# -----------------------------------
galimi_laukai = ["SKLYPO_ID", "UNIKAL_ID", "PLOTAS_REG", "ADRESAS", "PASK_TIP"]

esami_laukai = [laukas for laukas in galimi_laukai if laukas in sklypai_gdf.columns]

print("=== PASIRINKTI SVARBŪS LAUKAI ===")
print(esami_laukai)
print()

if esami_laukai:
    print(sklypai_gdf[esami_laukai].head())
else:
    print("Nerasta nei vieno iš pasirinktų laukų.")