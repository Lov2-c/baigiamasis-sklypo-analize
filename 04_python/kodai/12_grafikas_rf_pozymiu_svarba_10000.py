# =========================================================
# FAILAS: 12_grafikas_rf_pozymiu_svarba.py
# PASKIRTIS:
# Nubraižyti RandomForest modelio požymių svarbos grafiką.
# Rodomi 15 svarbiausių požymių.
# =========================================================

import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    failo_kelias = "06_rezultatai/random_forest_10000_pozymiu_svarba.csv"

    df = pd.read_csv(failo_kelias, encoding="utf-8-sig")

    # Pasiimame 15 svarbiausių požymių
    top_df = df.head(15).copy()

    print("15 svarbiausių požymių:")
    print(top_df)
    print()

    # Kad grafike svarbiausias požymis būtų viršuje
    top_df = top_df.sort_values("svarba", ascending=True)

    plt.figure(figsize=(10, 7))
    plt.barh(top_df["pozymis"], top_df["svarba"])

    plt.title("RandomForest požymių svarba")
    plt.xlabel("Svarba")
    plt.ylabel("Požymis")
    plt.tight_layout()

    isvedimo_failas = "06_rezultatai/grafikas_rf_pozymiu_svarba_10000.png"
    plt.savefig(isvedimo_failas, dpi=200)
    plt.show()

    print("Grafikas išsaugotas:")
    print(isvedimo_failas)