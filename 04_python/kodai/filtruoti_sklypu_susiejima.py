from pathlib import Path
import pandas as pd


PROJEKTO_KATALOGAS = Path(__file__).resolve().parents[2]

IVESTIES_CSV = PROJEKTO_KATALOGAS / "06_rezultatai" / "sklypu_susiejimas_2019_su_atvirais.csv"
ISVESTIES_CSV = PROJEKTO_KATALOGAS / "06_rezultatai" / "sklypu_susiejimas_2019_su_atvirais_patvirtintas.csv"


def main():
    df = pd.read_csv(IVESTIES_CSV)

    print("\n=== PRADINIS EILUČIŲ SKAIČIUS ===")
    print(len(df))

    # Paliekam tik tas eilutes, kur senas sklypas turi DB ID
    df = df[df["db_sklypo_id"].notna()].copy()

    print("\n=== PO db_sklypo_id FILTRO ===")
    print(len(df))

    # Patikimas erdvinis susiejimas
    df = df[
        (df["persidengimo_proc_nuo_seno"] >= 95)
        & (df["persidengimo_proc_nuo_naujo"] >= 95)
    ].copy()

    print("\n=== PO PATIKIMUMO FILTRO (>=95% ir >=95%) ===")
    print(len(df))

    # Susitvarkom tekstinius formatus
    df["db_sklypo_id"] = df["db_sklypo_id"].astype(str).str.replace(r"\.0$", "", regex=True)
    df["atviru_unikalus_nr"] = df["atviru_unikalus_nr"].astype(str).str.replace(r"\.0$", "", regex=True)
    df["atviru_kadastro_nr"] = df["atviru_kadastro_nr"].astype(str).str.strip()

    # Paliekam tik svarbiausius laukus UI susiejimui
    galutinis = df[
        [
            "db_sklypo_id",
            "atviru_unikalus_nr",
            "atviru_kadastro_nr",
            "persidengimo_proc_nuo_seno",
            "persidengimo_proc_nuo_naujo",
        ]
    ].copy()

    # Jei tas pats atviras sklypas kartojasi, paliekam geriausią variantą
    galutinis = galutinis.sort_values(
        by=["persidengimo_proc_nuo_seno", "persidengimo_proc_nuo_naujo"],
        ascending=False
    )

    galutinis = galutinis.drop_duplicates(subset=["atviru_unikalus_nr"], keep="first")
    galutinis = galutinis.drop_duplicates(subset=["atviru_kadastro_nr"], keep="first")

    ISVESTIES_CSV.parent.mkdir(parents=True, exist_ok=True)
    galutinis.to_csv(ISVESTIES_CSV, index=False, encoding="utf-8-sig")

    print("\n=== BAIGTA ===")
    print(f"Išsaugota: {ISVESTIES_CSV}")
    print("\nPirmos 5 eilutės:")
    print(galutinis.head())


if __name__ == "__main__":
    main()