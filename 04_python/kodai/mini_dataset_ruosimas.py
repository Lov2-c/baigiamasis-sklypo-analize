import geopandas as gpd
import pandas as pd


# -----------------------------------
# FAILŲ KELIAI
# -----------------------------------
sklypu_kelias = "01_duomenys/sklypai/klaipedos_raj_ribos_2019.gpkg"
bp_kelias = "01_duomenys/bp/bp_funkc.shp"


def paruosti_normalius_sklypus(sklypai_gdf):
    """
    Ši funkcija palieka tik tuos sklypus,
    kurie turi pagrindinius duomenis ir nėra tušti objektai.
    """

    # Pasiliekame tik tas eilutes, kur yra svarbiausi laukai
    filtruoti = sklypai_gdf.copy()

    filtruoti = filtruoti[
        filtruoti["SKLYPO_ID"].notna() &
        filtruoti["UNIKAL_ID"].notna()
    ]

    # PLOTAS_REG turi būti didesnis už 0
    filtruoti = filtruoti[filtruoti["PLOTAS_REG"] > 0]

    # Geometrija turi egzistuoti
    filtruoti = filtruoti[filtruoti.geometry.notna()]

    return filtruoti


def apskaiciuoti_sklypo_bp_procentus(sklypo_eilute, bp_gdf):
    """
    Ši funkcija vienam sklypui:
    1. suranda visas kertančias BP zonas,
    2. apskaičiuoja kiekvienos zonos plotą,
    3. apskaičiuoja procentą nuo viso sklypo ploto,
    4. grąžina rezultatų sąrašą.
    """

    sklypo_geom = sklypo_eilute.geometry
    sklypo_plotas = sklypo_geom.area

    # Randame BP zonas, kurios kertasi su šiuo sklypu
    bp_susikirtimai = bp_gdf[bp_gdf.intersects(sklypo_geom)].copy()

    rezultatai = []

    # Pereiname per visas rastas BP zonas
    for _, bp_eilute in bp_susikirtimai.iterrows():
        susikirtimo_geom = bp_eilute.geometry.intersection(sklypo_geom)
        susikirtimo_plotas = susikirtimo_geom.area

        # Jei dėl kažkokių priežasčių plotas 0, tokios eilutės nepridedame
        if susikirtimo_plotas <= 0:
            continue

        susikirtimo_procentas = (susikirtimo_plotas / sklypo_plotas) * 100

        rezultatai.append({
            "SKLYPO_ID": sklypo_eilute["SKLYPO_ID"],
            "UNIKAL_ID": sklypo_eilute["UNIKAL_ID"],
            "PLOTAS_REG": sklypo_eilute["PLOTAS_REG"],
            "ADRESAS": sklypo_eilute["ADRESAS"],
            "PASK_TIP": sklypo_eilute["PASK_TIP"],
            "BP_ZONA_PAV": bp_eilute["F_ZON_APR"],
            "BP_ZONOS_KODAS": bp_eilute["FUNKC_ZON"],
            "U_INTENS": bp_eilute["U_INTENS"],
            "MAX_AUK_SK": bp_eilute["MAX_AUK_SK"],
            "PAGR_PASK": bp_eilute["PAGR_PASK"],
            "BP_OBJ_NR": bp_eilute["NR"],
            "SKLYPO_PLOTAS_M2": round(sklypo_plotas, 2),
            "SUSIKIRTIMO_PLOTAS_M2": round(susikirtimo_plotas, 2),
            "SUSIKIRTIMO_PROC": round(susikirtimo_procentas, 2)
        })

    return rezultatai


if __name__ == "__main__":
    # -----------------------------------
    # 1. NUSKAITOME DUOMENIS
    # -----------------------------------
    print("Nuskaitomi sklypai...")
    sklypai_gdf = gpd.read_file(sklypu_kelias)

    print("Nuskaitomas BP sluoksnis...")
    bp_gdf = gpd.read_file(bp_kelias)

    print()
    print("=== PRADINĖ INFORMACIJA ===")
    print("Visų sklypų skaičius:", len(sklypai_gdf))
    print("BP objektų skaičius:", len(bp_gdf))
    print()

    # -----------------------------------
    # 2. IŠSIFILTRUOJAME NORMALIUS SKLYPUS
    # -----------------------------------
    tvarkingi_sklypai = paruosti_normalius_sklypus(sklypai_gdf)

    print("=== PO FILTRAVIMO ===")
    print("Tvarkingų sklypų skaičius:", len(tvarkingi_sklypai))
    print()

    # -----------------------------------
    # 3. PASIIMAME TIK PIRMUS 50 SKLYPŲ
    # -----------------------------------
    mini_sklypai = tvarkingi_sklypai.head(50).copy()

    print("Mini-datasetui imami pirmi 50 normalių sklypų.")
    print()

    # -----------------------------------
    # 4. APSKAIČIUOJAME REZULTATUS
    # -----------------------------------
    visos_eilutes = []

    for indeksas, (_, sklypo_eilute) in enumerate(mini_sklypai.iterrows(), start=1):
        print(f"Apdorojamas sklypas {indeksas} iš 50...")

        rezultatai_vienam_sklypui = apskaiciuoti_sklypo_bp_procentus(sklypo_eilute, bp_gdf)
        visos_eilutes.extend(rezultatai_vienam_sklypui)

    # -----------------------------------
    # 5. SUFORMUOJAME GALUTINĘ LENTELĘ
    # -----------------------------------
    mini_dataset_df = pd.DataFrame(visos_eilutes)

    # Išrikiuojame, kad būtų gražiau
    mini_dataset_df = mini_dataset_df.sort_values(
        by=["SKLYPO_ID", "SUSIKIRTIMO_PROC"],
        ascending=[True, False]
    )

    # -----------------------------------
    # 6. IŠVEDAME REZULTATĄ
    # -----------------------------------
    print()
    print("=== MINI-DATASET REZULTATAS ===")
    print("Eilučių skaičius:", len(mini_dataset_df))
    print()

    print("=== PIRMOS 20 EILUČIŲ ===")
    print(mini_dataset_df.head(20))
    print()

    # -----------------------------------
    # 7. IŠSAUGOME Į CSV
    # -----------------------------------
    isvedimo_kelias = "06_rezultatai/mini_dataset_bp_50.csv"
    mini_dataset_df.to_csv(isvedimo_kelias, index=False, encoding="utf-8-sig")

    print("Mini-datasetas išsaugotas faile:")
    print(isvedimo_kelias)