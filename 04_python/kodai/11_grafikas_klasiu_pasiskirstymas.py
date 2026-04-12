# =========================================================
# FAILAS: 11_grafikas_klasiu_pasiskirstymas.py
# PASKIRTIS:
# Nubraižyti target klasių pasiskirstymo grafiką
# naudojant 1000 sklypų modelio failą.
# =========================================================

import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    failo_kelias = "06_rezultatai/modelio_duomenys_1000.csv"

    df = pd.read_csv(failo_kelias, encoding="utf-8-sig")

    klasiu_sk = df["vystymo_target"].value_counts()

    print("Target klasių pasiskirstymas:")
    print(klasiu_sk)
    print()

    plt.figure(figsize=(10, 6))
    klasiu_sk.plot(kind="bar")

    plt.title("Vystymo target klasių pasiskirstymas")
    plt.xlabel("Klasė")
    plt.ylabel("Sklypų skaičius")
    plt.xticks(rotation=20)
    plt.tight_layout()

    isvedimo_failas = "06_rezultatai/grafikas_klasiu_pasiskirstymas.png"
    plt.savefig(isvedimo_failas, dpi=200)
    plt.show()

    print("Grafikas išsaugotas:")
    print(isvedimo_failas)