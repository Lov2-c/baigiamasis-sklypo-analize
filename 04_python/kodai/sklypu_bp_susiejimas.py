import geopandas as gpd
import pandas as pd

# -----------------------------------
# FAILŲ KELIAI
# -----------------------------------
sklypu_kelias = "01_duomenys/sklypai/klaipedos_raj_ribos_2019.gpkg"
bp_kelias = "01_duomenys/bp/bp_funkc.shp"

# -----------------------------------
# NUSKAITOME DUOMENIS
# -----------------------------------
sklypai_gdf = gpd.read_file(sklypu_kelias)
bp_gdf = gpd.read_file(bp_kelias)

# -----------------------------------
# PASIIMAME TIK DALĮ SKLYPŲ TESTAVIMUI
# -----------------------------------
# Pradžiai imame pirmus 100 sklypų, kad kodas veiktų greičiau.
sklypai_100 = sklypai_gdf.head(100).copy()

# -----------------------------------
# PASIRUOŠIAME TIK REIKALINGUS BP STULPELIUS
# -----------------------------------
bp_reikalingi = bp_gdf[
    ["F_ZON_APR", "U_INTENS", "MAX_AUK_SK", "PAGR_PASK", "FUNKC_ZON", "NR", "geometry"]
].copy()

# -----------------------------------
# ATLIEKAME ERDVINĮ SUJUNGIMĄ
# -----------------------------------
# Kiekvienam sklypui ieškome BP objekto, su kuriuo jis kertasi.
sujungta = gpd.sjoin(
    sklypai_100,
    bp_reikalingi,
    how="left",
    predicate="intersects"
)

print("=== STULPELIAI PO SUJUNGIMO ===")
print(sujungta.columns.tolist())
print()

# -----------------------------------
# PASILIEKAME SVARBIAUSIUS LAUKUS
# -----------------------------------
galutine_lentele = sujungta[
    [
        "SKLYPO_ID",
        "UNIKAL_ID",
        "PLOTAS_REG",
        "ADRESAS",
        "PASK_TIP",
        "F_ZON_APR",
        "U_INTENS",
        "MAX_AUK_SK",
        "PAGR_PASK",
        "FUNKC_ZON",
        "NR_right"
    ]
].copy()

# -----------------------------------
# PERVADINAME STULPELIUS, KAD BŪTŲ AIŠKIAU
# -----------------------------------
galutine_lentele = galutine_lentele.rename(
    columns={
        "NR_right": "BP_OBJ_NR"
    }
)

# -----------------------------------
# REZULTATŲ PERŽIŪRA
# -----------------------------------
print("=== SUJUNGIMO REZULTATAS ===")
print("Eilučių skaičius po sujungimo:", len(galutine_lentele))
print()

print("=== PIRMOS 10 EILUČIŲ ===")
print(galutine_lentele.head(10))
print()

print("=== KIEK SKLYPŲ GAVO BP ZONĄ ===")
bp_zona_rasta = galutine_lentele["FUNKC_ZON"].notna().sum()
print("Sklypų su rasta BP zona:", bp_zona_rasta)
print("Sklypų be rastos BP zonos:", len(galutine_lentele) - bp_zona_rasta)