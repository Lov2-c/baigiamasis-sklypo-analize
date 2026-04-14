# =========================================================
# FAILAS: 14_grafikas_modeliu_palyginimas.py
# PASKIRTIS:
# Nubraižyti galutinį RandomForest ir MLP modelių
# palyginimo grafiką pagal svarbiausias metrikas.
# =========================================================

import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    failo_kelias = "06_rezultatai/galutinis_modeliu_palyginimas_10000.csv"

    df = pd.read_csv(failo_kelias, encoding="utf-8-sig")

    print("Modelių palyginimo lentelė:")
    print(df)
    print()

    # Pasiimame tik svarbiausias metrikas
    metrikos = ["accuracy", "balanced_accuracy", "f1_macro"]

    # Modelių pavadinimai x ašiai
    modeliai = df["modelis"].tolist()

    # Paruošiame reikšmes kiekvienai metrikai
    accuracy_reiksmes = df["accuracy"].tolist()
    balanced_acc_reiksmes = df["balanced_accuracy"].tolist()
    f1_macro_reiksmes = df["f1_macro"].tolist()

    x = range(len(modeliai))
    plotis = 0.25

    plt.figure(figsize=(10, 6))

    plt.bar([i - plotis for i in x], accuracy_reiksmes, width=plotis, label="Accuracy")
    plt.bar(x, balanced_acc_reiksmes, width=plotis, label="Balanced accuracy")
    plt.bar([i + plotis for i in x], f1_macro_reiksmes, width=plotis, label="F1 macro")

    plt.title("Galutinis modelių palyginimas")
    plt.xlabel("Modelis")
    plt.ylabel("Metrikos reikšmė")
    plt.xticks(list(x), modeliai)
    plt.ylim(0, 1.05)
    plt.legend()
    plt.tight_layout()

    isvedimo_failas = "06_rezultatai/grafikas_modeliu_palyginimas_10000.png"
    plt.savefig(isvedimo_failas, dpi=200)
    plt.show()

    print("Grafikas išsaugotas:")
    print(isvedimo_failas)
