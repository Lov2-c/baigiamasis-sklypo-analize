from pathlib import Path
import zipfile
import tempfile
import time

import geopandas as gpd
import pandas as pd


# ============================================================
# 1. KELIAI
# ============================================================

PROJEKTO_KATALOGAS = Path(__file__).resolve().parents[2]

SENAS_SKLYPU_SLUOKSNIS = PROJEKTO_KATALOGAS / "01_duomenys" / "sklypai" / "klaipedos_raj_ribos_2019.gpkg"
ATVIRI_SKLYPAI_ZIP = PROJEKTO_KATALOGAS / "01_duomenys" / "atviri_sklypai" / "klaipedos_rajono_sklypai.zip"

REZULTATU_CSV = PROJEKTO_KATALOGAS / "06_rezultatai" / "sklypu_susiejimas_2019_su_atvirais.csv"


# ============================================================
# 2. PAGALBINĖS FUNKCIJOS
# ============================================================

def rasti_stulpeli(stulpeliai: list[str], kandidatai: list[str]):
    """
    Grąžina pirmą rastą stulpelį iš galimų kandidatų sąrašo.
    """
    for kandidatas in kandidatai:
        if kandidatas in stulpeliai:
            return kandidatas
    return None


def isskleisti_json_is_zip(zip_kelias: Path) -> Path:
    """
    Iš ZIP failo išima pirmą JSON / GeoJSON failą ir grąžina jo kelią.
    """
    with zipfile.ZipFile(zip_kelias, "r") as zip_obj:
        failai = zip_obj.namelist()

        tinkami = [
            p for p in failai
            if p.lower().endswith(".json") or p.lower().endswith(".geojson")
        ]

        if not tinkami:
            raise FileNotFoundError("ZIP faile nerasta JSON / GeoJSON failo.")

        vidinis_failas = tinkami[0]

        laikinas_katalogas = Path(tempfile.gettempdir()) / "baigiamasis_atviri_sklypai_susiejimui"
        laikinas_katalogas.mkdir(parents=True, exist_ok=True)

        isskleisto_failo_kelias = laikinas_katalogas / Path(vidinis_failas).name

        with zip_obj.open(vidinis_failas) as src, open(isskleisto_failo_kelias, "wb") as dst:
            dst.write(src.read())

    return isskleisto_failo_kelias


def paruosti_geometrija(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Sutvarko geometrijas:
    - pašalina tuščias
    - bando pataisyti netvarkingas su buffer(0)
    """
    gdf = gdf.copy()

    gdf = gdf[gdf.geometry.notna()].copy()
    gdf = gdf[~gdf.geometry.is_empty].copy()

    # Buffer(0) dažnai padeda pataisyti netvarkingus poligonus
    gdf["geometry"] = gdf.geometry.buffer(0)

    gdf = gdf[gdf.geometry.notna()].copy()
    gdf = gdf[~gdf.geometry.is_empty].copy()

    return gdf


# ============================================================
# 3. DUOMENŲ NUSKAITYMAS
# ============================================================

def nuskaityti_sena_sklypu_sluoksni() -> gpd.GeoDataFrame:
    """
    Nuskaito seną 2019 m. sklypų sluoksnį.
    """
    print("\n=== NUSKAITOMAS SENAS 2019 M. SKLYPŲ SLUOKSNIS ===")
    print(SENAS_SKLYPU_SLUOKSNIS)

    if not SENAS_SKLYPU_SLUOKSNIS.exists():
        raise FileNotFoundError(f"Nerastas failas: {SENAS_SKLYPU_SLUOKSNIS}")

    gdf = gpd.read_file(SENAS_SKLYPU_SLUOKSNIS)

    if gdf.empty:
        raise ValueError("Senas sklypų sluoksnis tuščias.")

    if gdf.crs is None:
        print("Seno sluoksnio CRS nerastas. Nustatomas EPSG:3346")
        gdf = gdf.set_crs(epsg=3346)

    gdf = paruosti_geometrija(gdf)

    print(f"Seno sluoksnio objektų skaičius po valymo: {len(gdf)}")
    print(f"Seno sluoksnio CRS: {gdf.crs}")

    return gdf


def nuskaityti_atvirus_sklypus() -> gpd.GeoDataFrame:
    """
    Nuskaito atvirus sklypų duomenis iš ZIP.
    """
    print("\n=== NUSKAITOMI ATVIRI SKLYPŲ DUOMENYS ===")
    print(ATVIRI_SKLYPAI_ZIP)

    if not ATVIRI_SKLYPAI_ZIP.exists():
        raise FileNotFoundError(f"Nerastas failas: {ATVIRI_SKLYPAI_ZIP}")

    json_kelias = isskleisti_json_is_zip(ATVIRI_SKLYPAI_ZIP)
    print(f"Iš ZIP išskleistas failas: {json_kelias}")

    gdf = gpd.read_file(json_kelias)

    if gdf.empty:
        raise ValueError("Atvirų sklypų sluoksnis tuščias.")

    if gdf.crs is None:
        print("Atvirų duomenų CRS nerastas. Nustatomas EPSG:3346")
        gdf = gdf.set_crs(epsg=3346)

    gdf = paruosti_geometrija(gdf)

    print(f"Atvirų duomenų objektų skaičius po valymo: {len(gdf)}")
    print(f"Atvirų duomenų CRS: {gdf.crs}")

    return gdf


# ============================================================
# 4. STULPELIŲ PARINKIMAS
# ============================================================

def parinkti_seno_sluoksnio_stulpelius(gdf: gpd.GeoDataFrame):
    """
    Parenka svarbius seno sluoksnio stulpelius.
    """
    stulpeliai = list(gdf.columns)

    senas_sklypo_id = rasti_stulpeli(
        stulpeliai,
        ["sklypo_id", "SKLYPO_ID", "id", "ID"]
    )

    senas_unik_id = rasti_stulpeli(
        stulpeliai,
        ["unik_id", "UNIK_ID", "unikalus_nr", "UNIKALUS_NR", "unikalus", "UNIKALUS"]
    )

    senas_kadastro_nr = rasti_stulpeli(
        stulpeliai,
        ["kadastro_nr", "KADASTRO_NR", "kad_nr", "KAD_NR", "kadastrinis_nr"]
    )

    print("\n=== SENO SLUOKSNIO SUSIEJIMO STULPELIAI ===")
    print(f"sklypo_id stulpelis: {senas_sklypo_id}")
    print(f"unik_id stulpelis: {senas_unik_id}")
    print(f"kadastro_nr stulpelis: {senas_kadastro_nr}")

    return senas_sklypo_id, senas_unik_id, senas_kadastro_nr


def parinkti_atviru_sluoksnio_stulpelius(gdf: gpd.GeoDataFrame):
    """
    Parenka svarbius atvirų duomenų stulpelius.
    """
    stulpeliai = list(gdf.columns)

    atviru_unikalus_nr = rasti_stulpeli(
        stulpeliai,
        ["unikalus_nr", "UNIKALUS_NR", "unikalus", "UNIKALUS"]
    )

    atviru_kadastro_nr = rasti_stulpeli(
        stulpeliai,
        ["kadastro_nr", "KADASTRO_NR", "kad_nr", "KAD_NR"]
    )

    atviru_plotas = rasti_stulpeli(
        stulpeliai,
        ["skl_plotas", "SKL_PLOTAS", "plotas", "PLOTAS", "plotas_j", "PLOTAS_J"]
    )

    print("\n=== ATVIRŲ DUOMENŲ SUSIEJIMO STULPELIAI ===")
    print(f"unikalus_nr stulpelis: {atviru_unikalus_nr}")
    print(f"kadastro_nr stulpelis: {atviru_kadastro_nr}")
    print(f"plotas stulpelis: {atviru_plotas}")

    return atviru_unikalus_nr, atviru_kadastro_nr, atviru_plotas


# ============================================================
# 5. SUSIEJIMO LOGIKA
# ============================================================

def sukurti_susiejimo_lentele(
    senas_gdf: gpd.GeoDataFrame,
    atviras_gdf: gpd.GeoDataFrame,
    senas_sklypo_id: str | None,
    senas_unik_id: str | None,
    senas_kadastro_nr: str | None,
    atviru_unikalus_nr: str | None,
    atviru_kadastro_nr: str | None,
    atviru_plotas: str | None,
) -> pd.DataFrame:
    """
    Kiekvienam senam sklypui suranda geriausiai persidengiantį naują sklypą.
    """
    print("\n=== PRADEDAM ERDVINĮ SUSIEJIMĄ ===")

    # Sumažinam laukų skaičių, kad darbas būtų lengvesnis
    seni_laukai = ["geometry"]
    if senas_sklypo_id:
        seni_laukai.append(senas_sklypo_id)
    if senas_unik_id and senas_unik_id not in seni_laukai:
        seni_laukai.append(senas_unik_id)
    if senas_kadastro_nr and senas_kadastro_nr not in seni_laukai:
        seni_laukai.append(senas_kadastro_nr)

    nauji_laukai = ["geometry"]
    if atviru_unikalus_nr:
        nauji_laukai.append(atviru_unikalus_nr)
    if atviru_kadastro_nr and atviru_kadastro_nr not in nauji_laukai:
        nauji_laukai.append(atviru_kadastro_nr)
    if atviru_plotas and atviru_plotas not in nauji_laukai:
        nauji_laukai.append(atviru_plotas)

    seni = senas_gdf[seni_laukai].copy()
    nauji = atviras_gdf[nauji_laukai].copy()

    seni = seni.reset_index(drop=True)
    nauji = nauji.reset_index(drop=True)

    seni["senas_idx"] = seni.index
    nauji["naujas_idx"] = nauji.index

    # Apskaičiuojam plotus
    seni["seno_plotas_m2"] = seni.geometry.area
    nauji["naujo_plotas_m2"] = nauji.geometry.area

    print("Daromas spatial join kandidatų paieškai...")
    kandidatai = gpd.sjoin(
        seni[["senas_idx", "seno_plotas_m2", "geometry"]],
        nauji[["naujas_idx", "naujo_plotas_m2", "geometry"]],
        how="inner",
        predicate="intersects",
        lsuffix="senas",
        rsuffix="naujas",
    )

    print(f"Kandidatinių porų skaičius: {len(kandidatai)}")

    if kandidatai.empty:
        raise ValueError("Po spatial join nerasta nė vienos persidengiančios poros.")

    # Kad būtų galima pasiimti geometrijas pagal indeksus
    seni_geom = seni.set_index("senas_idx").geometry
    nauji_geom = nauji.set_index("naujas_idx").geometry

    rezultatai = []

    start = time.time()

    for i, kandidato_eilute in kandidatai.iterrows():
        senas_idx = kandidato_eilute["senas_idx"]
        naujas_idx = kandidato_eilute["naujas_idx"]

        geom_sena = seni_geom.loc[senas_idx]
        geom_nauja = nauji_geom.loc[naujas_idx]

        persidengimo_plotas = geom_sena.intersection(geom_nauja).area

        seno_plotas_m2 = kandidato_eilute["seno_plotas_m2"]
        naujo_plotas_m2 = kandidato_eilute["naujo_plotas_m2"]

        persidengimo_proc_nuo_seno = 0
        persidengimo_proc_nuo_naujo = 0

        if seno_plotas_m2 > 0:
            persidengimo_proc_nuo_seno = persidengimo_plotas / seno_plotas_m2 * 100

        if naujo_plotas_m2 > 0:
            persidengimo_proc_nuo_naujo = persidengimo_plotas / naujo_plotas_m2 * 100

        irasas = {
            "senas_idx": senas_idx,
            "naujas_idx": naujas_idx,
            "persidengimo_plotas_m2": persidengimo_plotas,
            "persidengimo_proc_nuo_seno": persidengimo_proc_nuo_seno,
            "persidengimo_proc_nuo_naujo": persidengimo_proc_nuo_naujo,
        }

        if senas_sklypo_id:
            irasas["db_sklypo_id"] = seni.loc[senas_idx, senas_sklypo_id]
        else:
            irasas["db_sklypo_id"] = None

        if senas_unik_id:
            irasas["db_unik_id"] = seni.loc[senas_idx, senas_unik_id]
        else:
            irasas["db_unik_id"] = None

        if senas_kadastro_nr:
            irasas["db_kadastro_nr"] = seni.loc[senas_idx, senas_kadastro_nr]
        else:
            irasas["db_kadastro_nr"] = None

        if atviru_unikalus_nr:
            irasas["atviru_unikalus_nr"] = nauji.loc[naujas_idx, atviru_unikalus_nr]
        else:
            irasas["atviru_unikalus_nr"] = None

        if atviru_kadastro_nr:
            irasas["atviru_kadastro_nr"] = nauji.loc[naujas_idx, atviru_kadastro_nr]
        else:
            irasas["atviru_kadastro_nr"] = None

        if atviru_plotas:
            irasas["atviru_plotas"] = nauji.loc[naujas_idx, atviru_plotas]
        else:
            irasas["atviru_plotas"] = None

        rezultatai.append(irasas)

        if (i + 1) % 5000 == 0:
            print(f"Apdorota kandidatų: {i + 1} / {len(kandidatai)}")

    rezultatu_df = pd.DataFrame(rezultatai)

    print(f"Porų apdorojimo trukmė: {time.time() - start:.1f} sek.")

    # Pasiliekam geriausią porą kiekvienam senam sklypui
    rezultatu_df = rezultatu_df.sort_values(
        by=["senas_idx", "persidengimo_plotas_m2", "persidengimo_proc_nuo_seno"],
        ascending=[True, False, False]
    )

    geriausi = rezultatu_df.groupby("senas_idx", as_index=False).first()

    print(f"Geriausių susiejimų skaičius: {len(geriausi)}")

    return geriausi


# ============================================================
# 6. MAIN
# ============================================================

def main():
    senas_gdf = nuskaityti_sena_sklypu_sluoksni()
    atviras_gdf = nuskaityti_atvirus_sklypus()

    # Sulyginam CRS
    if senas_gdf.crs != atviras_gdf.crs:
        print("\nCRS skiriasi, atviri duomenys perprojektuojami į seno sluoksnio CRS...")
        atviras_gdf = atviras_gdf.to_crs(senas_gdf.crs)

    senas_sklypo_id, senas_unik_id, senas_kadastro_nr = parinkti_seno_sluoksnio_stulpelius(senas_gdf)
    atviru_unikalus_nr, atviru_kadastro_nr, atviru_plotas = parinkti_atviru_sluoksnio_stulpelius(atviras_gdf)

    susiejimo_df = sukurti_susiejimo_lentele(
        senas_gdf=senas_gdf,
        atviras_gdf=atviras_gdf,
        senas_sklypo_id=senas_sklypo_id,
        senas_unik_id=senas_unik_id,
        senas_kadastro_nr=senas_kadastro_nr,
        atviru_unikalus_nr=atviru_unikalus_nr,
        atviru_kadastro_nr=atviru_kadastro_nr,
        atviru_plotas=atviru_plotas,
    )

    REZULTATU_CSV.parent.mkdir(parents=True, exist_ok=True)
    susiejimo_df.to_csv(REZULTATU_CSV, index=False, encoding="utf-8-sig")

    print("\n=== BAIGTA ===")
    print(f"Rezultatas išsaugotas čia: {REZULTATU_CSV}")
    print("\nPirmi 5 įrašai:")
    print(susiejimo_df.head())


if __name__ == "__main__":
    main()