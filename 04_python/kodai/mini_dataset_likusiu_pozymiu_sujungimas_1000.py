# =========================================================
# FAILAS: mini_dataset_likusiu_pozymiu_sujungimas_1000.py
# PASKIRTIS:
# Prijungti likusius gamtinius ir inžinerinius požymius
# prie 1000 sklypų mini dataset, kuris jau turi:
# - BP
# - saugomas teritorijas
# - mišką
# - KVR
# =========================================================

import pandas as pd


def paruosti_pozymio_lentele(df: pd.DataFrame, stulpelio_vardas: str) -> pd.DataFrame:
    """
    Užtikrina, kad vienam SKLYPO_ID būtų viena eilutė.
    Jei randami pasikartojimai, paliekama didžiausia reikšmė.
    """

    if "SKLYPO_ID" not in df.columns or stulpelio_vardas not in df.columns:
        raise ValueError(f"Nerasti būtini stulpeliai: SKLYPO_ID arba {stulpelio_vardas}")

    return (
        df.groupby("SKLYPO_ID", as_index=False)[stulpelio_vardas]
        .max()
    )


if __name__ == "__main__":
    pagrindinis_failas = "06_rezultatai/mini_dataset_bp_1000_su_saugomomis_misku_ir_kvr.csv"

    papildomi_failai = [
        ("06_rezultatai/pelkiu_proc.csv", "pelkiu_proc"),
        ("06_rezultatai/saltinynu_proc.csv", "saltinynu_proc"),
        ("06_rezultatai/pievu_ganyklu_proc.csv", "pievu_ganyklu_proc"),
        ("06_rezultatai/drenazo_plotu_proc.csv", "drenazo_plotu_proc"),
        ("06_rezultatai/rinktuvu_apsaugos_zonu_proc.csv", "rinktuvu_apsaugos_zonu_proc"),
        ("06_rezultatai/gelezinkelio_ribojimo_zonos_proc.csv", "gelezinkelio_ribojimo_zonos_proc"),
    ]

    df = pd.read_csv(pagrindinis_failas, encoding="utf-8-sig")

    print("Pagrindinis dataset nuskaitytas.")
    print("Eilučių:", len(df))
    print()

    for failo_kelias, stulpelio_vardas in papildomi_failai:
        print("=" * 80)
        print(f"Jungiamas požymis: {stulpelio_vardas}")
        print(f"Failas: {failo_kelias}")

        pozymio_df = pd.read_csv(failo_kelias, encoding="utf-8-sig")
        print("Nuskaityta eilučių:", len(pozymio_df))
        print("Stulpeliai:", list(pozymio_df.columns))

        pozymio_df = paruosti_pozymio_lentele(pozymio_df, stulpelio_vardas)
        print("Po agregavimo eilučių:", len(pozymio_df))

        df = df.merge(
            pozymio_df,
            on="SKLYPO_ID",
            how="left"
        )

        df[stulpelio_vardas] = df[stulpelio_vardas].fillna(0)

        print("Po sujungimo bendrame dataset eilučių:", len(df))
        print()

    print("=" * 80)
    print("Galutinis rezultatas")
    print("Eilučių:", len(df))
    print("Stulpelių:", len(df.columns))
    print()
    print(df.head())

    isvedimo_kelias = "06_rezultatai/mini_dataset_bp_1000_pilnas.csv"
    df.to_csv(isvedimo_kelias, index=False, encoding="utf-8-sig")

    print()
    print("Failas išsaugotas:")
    print(isvedimo_kelias)