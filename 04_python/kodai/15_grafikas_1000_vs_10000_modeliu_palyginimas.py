import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# 1. FAILŲ KELIAI
# ============================================================
# Jei pas tave failų pavadinimai šiek tiek skiriasi,
# pataisyk tik šią vietą.

RF_1000_KELIAS = "06_rezultatai/random_forest_1000_rezultatai.csv"
MLP_1000_BANDYMU_KELIAS = "06_rezultatai/mlp_bandymu_lentele.csv"

RF_10000_KELIAS = "06_rezultatai/random_forest_10000_rezultatai.csv"
MLP_10000_BANDYMU_KELIAS = "06_rezultatai/mlp_10000_bandymu_lentele.csv"

ISVEDIMO_CSV = "06_rezultatai/modeliu_palyginimas_1000_vs_10000.csv"
GRAFIKAS_BENDRAS = "06_rezultatai/grafikas_1000_vs_10000_modeliu_palyginimas.png"
GRAFIKAS_MACRO_F1 = "06_rezultatai/grafikas_1000_vs_10000_macro_f1.png"


# ============================================================
# 2. PAGALBINĖS FUNKCIJOS
# ============================================================

def nuskaityti_random_forest_faila(kelias: str, naujas_pavadinimas: str) -> pd.DataFrame:
    """
    Nuskaito RandomForest rezultatų failą
    ir pervadina modelio pavadinimą taip, kaip norime galutinėje lentelėje.
    """
    df = pd.read_csv(kelias)
    df = df.copy()
    df["modelis"] = naujas_pavadinimas
    return df


def nuskaityti_geriausia_mlp_is_bandymu(
    kelias: str,
    naujas_pavadinimas: str,
) -> pd.DataFrame:
    """
    Nuskaito visų MLP bandymų lentelę
    ir paima geriausią bandymą pagal:
    1. f1_macro
    2. balanced_accuracy
    3. accuracy
    """
    df = pd.read_csv(kelias)

    geriausias = (
        df.sort_values(
            by=["f1_macro", "balanced_accuracy", "accuracy"],
            ascending=False,
        )
        .iloc[[0]]
        .copy()
    )

    geriausias["modelis"] = naujas_pavadinimas
    return geriausias


def palikti_svarbiausius_stulpelius(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pasiliekame tik tuos stulpelius, kurių reikia
    palyginimui ir grafikams.
    """
    reikalingi = [
        "modelis",
        "accuracy",
        "balanced_accuracy",
        "precision_macro",
        "recall_macro",
        "f1_macro",
        "precision_weighted",
        "recall_weighted",
        "f1_weighted",
    ]

    esami = [st for st in reikalingi if st in df.columns]
    return df[esami].copy()


def nubraizyti_bendra_grafika(df: pd.DataFrame, isvedimo_kelias: str):
    """
    Nubraižo pagrindinį grafiką, kuriame lyginamos 3 metrikos:
    - accuracy
    - balanced_accuracy
    - f1_macro
    """
    modeliai = df["modelis"].tolist()

    accuracy = df["accuracy"].tolist()
    balanced_accuracy = df["balanced_accuracy"].tolist()
    f1_macro = df["f1_macro"].tolist()

    x = list(range(len(modeliai)))
    plotis = 0.22

    plt.figure(figsize=(11, 6))

    plt.bar([i - plotis for i in x], accuracy, width=plotis, label="Accuracy")
    plt.bar(x, balanced_accuracy, width=plotis, label="Balanced accuracy")
    plt.bar([i + plotis for i in x], f1_macro, width=plotis, label="Macro F1")

    plt.xticks(x, modeliai, rotation=15)
    plt.ylim(0.95, 1.001)
    plt.ylabel("Reikšmė")
    plt.title("1000 vs 10000 modelių palyginimas")
    plt.legend()
    plt.tight_layout()
    plt.savefig(isvedimo_kelias, dpi=200)
    plt.close()


def nubraizyti_macro_f1_grafika(df: pd.DataFrame, isvedimo_kelias: str):
    """
    Nubraižo papildomą paprastesnį grafiką,
    kuriame lyginamas tik Macro F1.
    """
    modeliai = df["modelis"].tolist()
    f1_macro = df["f1_macro"].tolist()

    x = list(range(len(modeliai)))

    plt.figure(figsize=(9, 5))
    plt.bar(x, f1_macro)

    plt.xticks(x, modeliai, rotation=15)
    plt.ylim(0.95, 1.001)
    plt.ylabel("Macro F1")
    plt.title("1000 vs 10000 modelių Macro F1 palyginimas")
    plt.tight_layout()
    plt.savefig(isvedimo_kelias, dpi=200)
    plt.close()


# ============================================================
# 3. NUSKAITOME 1000 REZULTATUS
# ============================================================
print("Nuskaitomi 1000 modelių rezultatai...")

rf_1000_df = nuskaityti_random_forest_faila(
    RF_1000_KELIAS,
    "RandomForest_1000",
)

mlp_1000_best_df = nuskaityti_geriausia_mlp_is_bandymu(
    MLP_1000_BANDYMU_KELIAS,
    "MLP_1000_best",
)

print("1000 rezultatai nuskaityti.")
print()


# ============================================================
# 4. NUSKAITOME 10000 REZULTATUS
# ============================================================
print("Nuskaitomi 10000 modelių rezultatai...")

rf_10000_df = nuskaityti_random_forest_faila(
    RF_10000_KELIAS,
    "RandomForest_10000",
)

mlp_10000_best_df = nuskaityti_geriausia_mlp_is_bandymu(
    MLP_10000_BANDYMU_KELIAS,
    "MLP_10000_best",
)

print("10000 rezultatai nuskaityti.")
print()


# ============================================================
# 5. SUJUNGIAME Į VIENĄ LENTELĘ
# ============================================================
visi_df = pd.concat(
    [
        rf_1000_df,
        mlp_1000_best_df,
        rf_10000_df,
        mlp_10000_best_df,
    ],
    ignore_index=True,
)

visi_df = palikti_svarbiausius_stulpelius(visi_df)

print("=" * 80)
print("GALUTINĖ 1000 VS 10000 PALYGINIMO LENTELĖ")
print("=" * 80)
print(visi_df)
print()


# ============================================================
# 6. IŠSAUGOME CSV
# ============================================================
visi_df.to_csv(ISVEDIMO_CSV, index=False, encoding="utf-8-sig")

print("Išsaugota lentelė:")
print(ISVEDIMO_CSV)
print()


# ============================================================
# 7. BRAIŽOME GRAFIKUS
# ============================================================
nubraizyti_bendra_grafika(visi_df, GRAFIKAS_BENDRAS)
nubraizyti_macro_f1_grafika(visi_df, GRAFIKAS_MACRO_F1)

print("Išsaugoti grafikai:")
print(GRAFIKAS_BENDRAS)
print(GRAFIKAS_MACRO_F1)