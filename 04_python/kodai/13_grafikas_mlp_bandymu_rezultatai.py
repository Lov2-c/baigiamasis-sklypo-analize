# =========================================================
# FAILAS: 13_grafikas_mlp_bandymu_rezultatai.py
# PASKIRTIS:
# Nubraižyti MLP bandymų rezultatų grafiką.
# Rodomas kiekvieno bandymo macro F1 įvertis.
# =========================================================

import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    failo_kelias = "06_rezultatai/mlp_1000_bandymu_lentele.csv"

    df = pd.read_csv(failo_kelias, encoding="utf-8-sig")

    # Išrikiuojame pagal bandymo numerį, kad grafikas eitų natūralia seka
    df = df.sort_values("bandymo_nr").copy()

    print("MLP bandymų rezultatai:")
    print(df[["bandymo_nr", "hidden_layer_sizes", "activation", "alpha", "learning_rate_init", "f1_macro"]])
    print()

    plt.figure(figsize=(11, 6))
    plt.plot(df["bandymo_nr"], df["f1_macro"], marker="o")

    plt.title("MLP bandymų macro F1 rezultatai")
    plt.xlabel("Bandymo numeris")
    plt.ylabel("Macro F1")
    plt.xticks(df["bandymo_nr"])
    plt.ylim(0, 1.05)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    isvedimo_failas = "06_rezultatai/grafikas_mlp_bandymu_rezultatai.png"
    plt.savefig(isvedimo_failas, dpi=200)
    plt.show()

    print("Grafikas išsaugotas:")
    print(isvedimo_failas)