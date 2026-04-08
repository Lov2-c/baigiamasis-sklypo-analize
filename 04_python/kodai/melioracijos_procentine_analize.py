# =========================================================
# FAILAS: melioracijos_procentine_analize.py
# PASKIRTIS:
# Apskaičiuoti, kokia kiekvieno sklypo dalis (%) patenka
# į drenažo plotus ir preliminarias rinktuvų apsaugos zonas.
# =========================================================

import geopandas as gpd
from pathlib import Path


def apskaiciuoti_procentus(sklypu_failas, sluoksnio_failas, isvedimo_failas, procento_stulpelis):
    """
    Apskaičiuoja, kokia kiekvieno sklypo dalis (%) patenka į pasirinktą sluoksnį.
    """

    print("\n" + "=" * 60)
    print(f"Pradedama analizė: {procento_stulpelis}")
    print("=" * 60)

    print("1. Nuskaitomi failai...")
    sklypai = gpd.read_file(sklypu_failas)
    sluoksnis = gpd.read_file(sluoksnio_failas)
    print("1. Failai nuskaityti.")

    print(f"Sklypų kiekis prieš filtravimą: {len(sklypai)}")
    print(f"Sluoksnio objektų kiekis: {len(sluoksnis)}")

    print(f"Sklypų CRS: {sklypai.crs}")
    print(f"Sluoksnio CRS: {sluoksnis.crs}")

    if sklypai.crs != sluoksnis.crs:
        print("2. CRS nesutampa, perprojektuojama...")
        sluoksnis = sluoksnis.to_crs(sklypai.crs)
        print("2. Perprojektavimas baigtas.")

    # ---------------------------------------------------------
    # 3. Sujungiame persidengiančias sluoksnio geometrijas
    # ---------------------------------------------------------
    print("3. Pradedamas sluoksnio geometrijų sujungimas (union_all)...")
    sujungta_sluoksnio_geometrija = sluoksnis.geometry.union_all()

    sluoksnis = gpd.GeoDataFrame(
        geometry=[sujungta_sluoksnio_geometrija],
        crs=sluoksnis.crs
    )
    print("3. Sluoksnio geometrijos sujungtos.")

    if "SKLYPO_ID" not in sklypai.columns:
        raise ValueError("Sklypų sluoksnyje nerastas stulpelis 'SKLYPO_ID'.")

    # ---------------------------------------------------------
    # 4. Paruošiame sklypų sluoksnį
    # ---------------------------------------------------------
    print("4. Atrenkami reikalingi sklypų stulpeliai...")
    sklypai = sklypai[["SKLYPO_ID", "geometry"]].copy()
    sklypai = sklypai.dropna(subset=["SKLYPO_ID"]).copy()
    print(f"4. Sklypų kiekis po tuščių SKLYPO_ID pašalinimo: {len(sklypai)}")

    # ---------------------------------------------------------
    # 5. SVARBUS PATAISYMAS:
    # Sujungiame to paties SKLYPO_ID geometrijas į vieną
    # ---------------------------------------------------------
    print("5. Pradedamas sklypų sujungimas pagal SKLYPO_ID...")
    sklypai = sklypai.dissolve(by="SKLYPO_ID").reset_index()
    print(f"5. Sklypų kiekis po sujungimo pagal SKLYPO_ID: {len(sklypai)}")

    # ---------------------------------------------------------
    # 6. Skaičiuojame sklypų plotus
    # ---------------------------------------------------------
    print("6. Skaičiuojami sklypų plotai...")
    sklypai["sklypo_plotas"] = sklypai.geometry.area
    print("6. Sklypų plotai apskaičiuoti.")

    # ---------------------------------------------------------
    # 7. Skaičiuojame susikirtimus
    # ---------------------------------------------------------
    print("7. Pradedami skaičiuoti susikirtimai (overlay intersection)...")
    susikirtimai = gpd.overlay(sklypai, sluoksnis, how="intersection")
    print("7. Susikirtimai apskaičiuoti.")

    print(f"Susikirtimų kiekis: {len(susikirtimai)}")

    if len(susikirtimai) == 0:
        print("8. Susikirtimų nerasta, visiems įrašams priskiriamas 0.")
        rezultatas = sklypai[["SKLYPO_ID"]].copy()
        rezultatas[procento_stulpelis] = 0.0
    else:
        print("8. Skaičiuojami susikirtimų plotai...")
        susikirtimai["susikirtimo_plotas"] = susikirtimai.geometry.area

        print("9. Grupavimas pagal SKLYPO_ID...")
        susikirtimu_suma = (
            susikirtimai.groupby("SKLYPO_ID")["susikirtimo_plotas"]
            .sum()
            .reset_index()
        )
        print("9. Grupavimas baigtas.")

        print("10. Sujungiami sklypų plotai su susikirtimų suma...")
        rezultatas = sklypai[["SKLYPO_ID", "sklypo_plotas"]].merge(
            susikirtimu_suma,
            on="SKLYPO_ID",
            how="left"
        )
        print("10. Sujungimas baigtas.")

        rezultatas["susikirtimo_plotas"] = rezultatas["susikirtimo_plotas"].fillna(0)

        print("11. Skaičiuojami procentai...")
        rezultatas[procento_stulpelis] = (
            rezultatas["susikirtimo_plotas"] / rezultatas["sklypo_plotas"] * 100
        ).round(2)
        print("11. Procentai apskaičiuoti.")

        # Diagnostika
        blogi_irasai = rezultatas[rezultatas[procento_stulpelis] > 100]

        if len(blogi_irasai) > 0:
            print(f"\nĮSPĖJIMAS: rasta {len(blogi_irasai)} įrašų, kur {procento_stulpelis} > 100")
            print("Pirmi probleminiai įrašai:")
            print(blogi_irasai[["SKLYPO_ID", "sklypo_plotas", "susikirtimo_plotas", procento_stulpelis]].head(10))
        else:
            print(f"12. Viskas gerai: įrašų su {procento_stulpelis} > 100 nerasta.")

        rezultatas = rezultatas[["SKLYPO_ID", procento_stulpelis]].copy()

    print("13. Išsaugomas CSV failas...")
    Path(isvedimo_failas).parent.mkdir(parents=True, exist_ok=True)
    rezultatas.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")
    print(f"13. Rezultatas išsaugotas: {isvedimo_failas}")

    print("Pirmos 5 eilutės:")
    print(rezultatas.head())


if __name__ == "__main__":
    sklypu_failas = r"01_duomenys/sklypai/klaipedos_raj_ribos_2019.gpkg"

    sluoksniai = [
        {
            "failas": r"01_duomenys/papildomi/melioracija/dren_p.gpkg",
            "csv": r"06_rezultatai/drenazo_plotu_proc.csv",
            "stulpelis": "drenazo_plotu_proc"
        },
        {
            "failas": r"01_duomenys/papildomi/melioracija/rinkt_l_125plus_buffer_15m.gpkg",
            "csv": r"06_rezultatai/rinktuvu_apsaugos_zonu_proc.csv",
            "stulpelis": "rinktuvu_apsaugos_zonu_proc"
        }
    ]

    for sluoksnis in sluoksniai:
        apskaiciuoti_procentus(
            sklypu_failas=sklypu_failas,
            sluoksnio_failas=sluoksnis["failas"],
            isvedimo_failas=sluoksnis["csv"],
            procento_stulpelis=sluoksnis["stulpelis"]
        )

    print("\nMelioracijos sluoksnių analizė baigta.")