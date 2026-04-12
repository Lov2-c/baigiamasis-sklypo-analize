# =========================================================
# FAILAS: 10_modeliu_palyginimas.py
# PASKIRTIS:
# Vienoje vietoje palyginti klasikinį modelį
# (RandomForest) ir geriausią neuroninį modelį (MLP)
# naudojant jau išsaugotus rezultatų CSV failus.
# =========================================================

import pandas as pd


if __name__ == "__main__":
    rf_failas = "06_rezultatai/random_forest_1000_rezultatai.csv"
    mlp_failas = "06_rezultatai/mlp_1000_rezultatai.csv"
    isvedimo_failas = "06_rezultatai/galutinis_modeliu_palyginimas.csv"

    # -----------------------------------------------------
    # 1. Nuskaitome modelių rezultatų failus
    # -----------------------------------------------------
    rf_df = pd.read_csv(rf_failas, encoding="utf-8-sig")
    mlp_df = pd.read_csv(mlp_failas, encoding="utf-8-sig")

    print("RandomForest rezultatų failas nuskaitytas.")
    print(rf_df)
    print()

    print("MLP rezultatų failas nuskaitytas.")
    print(mlp_df)
    print()

    # -----------------------------------------------------
    # 2. Sujungiame į vieną lentelę
    # -----------------------------------------------------
    palyginimo_df = pd.concat([rf_df, mlp_df], ignore_index=True)

    # -----------------------------------------------------
    # 3. Išrikiuojame pagal svarbiausias metrikas
    # -----------------------------------------------------
    palyginimo_df = palyginimo_df.sort_values(
        by=["f1_macro", "balanced_accuracy", "accuracy"],
        ascending=False
    ).reset_index(drop=True)

    print("=" * 80)
    print("GALUTINIS MODELIŲ PALYGINIMAS")
    print("=" * 80)
    print(palyginimo_df)
    print()

    # -----------------------------------------------------
    # 4. Išsaugome
    # -----------------------------------------------------
    palyginimo_df.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

    print("Galutinė modelių palyginimo lentelė išsaugota:")
    print(isvedimo_failas)