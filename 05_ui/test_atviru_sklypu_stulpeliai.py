from pathlib import Path
import zipfile
import tempfile

import geopandas as gpd
import pandas as pd
import sqlite3


PROJEKTO_KATALOGAS = Path(__file__).resolve().parents[1]

ATVIRU_SKLYPU_ZIP = PROJEKTO_KATALOGAS / "01_duomenys" / "atviri_sklypai" / "klaipedos_rajono_sklypai.zip"
DB_FAILO_KELIAS = PROJEKTO_KATALOGAS / "03_db" / "baigiamasis.db"
PAGRINDINE_LENTELE = "sklypu_analizes"


def nuskaityti_atvirus_duomenis():
    with zipfile.ZipFile(ATVIRU_SKLYPU_ZIP, "r") as zip_obj:
        failai = zip_obj.namelist()

        tinkami = [
            p for p in failai
            if p.lower().endswith(".json") or p.lower().endswith(".geojson")
        ]

        if not tinkami:
            raise FileNotFoundError("ZIP faile nerasta JSON / GeoJSON failo.")

        vidinis_failas = tinkami[0]

        laikinas_katalogas = Path(tempfile.gettempdir()) / "baigiamasis_test_atviri"
        laikinas_katalogas.mkdir(parents=True, exist_ok=True)

        isskleistas_failas = laikinas_katalogas / Path(vidinis_failas).name

        with zip_obj.open(vidinis_failas) as src, open(isskleistas_failas, "wb") as dst:
            dst.write(src.read())

    gdf = gpd.read_file(isskleistas_failas)

    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=3346)

    return gdf, vidinis_failas


def nuskaityti_viena_db_eilute():
    conn = sqlite3.connect(DB_FAILO_KELIAS)
    try:
        df = pd.read_sql_query(
            f"SELECT * FROM {PAGRINDINE_LENTELE} LIMIT 1",
            conn
        )
        return df.iloc[0]
    finally:
        conn.close()


def main():
    gdf, vidinis_failas = nuskaityti_atvirus_duomenis()

    print("\n=== NAUDOTAS FAILAS ZIP VIDUJE ===")
    print(vidinis_failas)

    print("\n=== ATVIRŲ DUOMENŲ STULPELIAI ===")
    for stulpelis in gdf.columns:
        print(stulpelis)

    print("\n=== PIRMOS EILUTĖS REIKŠMĖS (be geometrijos) ===")
    pirma = gdf.iloc[0]
    for stulpelis in gdf.columns:
        if stulpelis == "geometry":
            continue
        print(f"{stulpelis}: {pirma[stulpelis]}")

    db_eilute = nuskaityti_viena_db_eilute()

    print("\n=== VIENA DB EILUTĖ (svarbiausi laukai) ===")
    svarbus = ["sklypo_id", "unik_id", "adresas"]
    for laukas in svarbus:
        if laukas in db_eilute.index:
            print(f"{laukas}: {db_eilute[laukas]}")


if __name__ == "__main__":
    main()