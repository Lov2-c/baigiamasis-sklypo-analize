# =========================================================
# FAILAS: 09_mlp_eksperimentai_1000.py
# PASKIRTIS:
# Atlikti 24 skirtingus MLPClassifier bandymus su 1000
# sklypų modelio failu Variantui B.
#
# TARGET:
# - vystymas_tiesiogiai_galimas
# - vystymas_galimas_su_salygomis
# - vystymas_labai_apribotas
#
# Šis failas skirtas baigiamojo darbo reikalavimui:
# neuroniniam modeliui atlikti bent 20-30 bandymų.
# =========================================================

import itertools
import warnings

import pandas as pd

from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler


def paruosti_duomenis(failo_kelias: str):
    """
    Funkcija:
    1. nuskaito modelio CSV
    2. užkoduoja target
    3. atskiria X ir y
    4. tekstinius stulpelius paverčia į one-hot
    5. padalina į train/test
    6. standartizuoja požymius

    Grąžina:
    X_train_scaled, X_test_scaled, y_train, y_test
    """

    df = pd.read_csv(failo_kelias, encoding="utf-8-sig")

    print("Duomenys sėkmingai nuskaityti.")
    print(f"Eilučių skaičius: {len(df)}")
    print(f"Stulpelių skaičius: {len(df.columns)}")
    print()

    print("Target klasių pasiskirstymas:")
    print(df["vystymo_target"].value_counts())
    print()

    # ---------------------------------------------------------
    # Target kodavimas
    # ---------------------------------------------------------
    target_zodynas = {
        "vystymas_tiesiogiai_galimas": 0,
        "vystymas_galimas_su_salygomis": 1,
        "vystymas_labai_apribotas": 2,
    }

    df["target_kodas"] = df["vystymo_target"].map(target_zodynas)

    # ---------------------------------------------------------
    # Atskiriame X ir y
    # ---------------------------------------------------------
    X = df.drop(columns=["SKLYPO_ID", "UNIKAL_ID", "vystymo_target", "target_kodas"]).copy()
    y = df["target_kodas"]

    # Tekstinius zonų kodų laukus paverčiame į 0/1 stulpelius
    kategoriniai_stulpeliai = [
        "PAGRINDINE_ZONOS_KODAS",
        "ANTRA_ZONOS_KODAS",
    ]

    esami_kategoriniai = [st for st in kategoriniai_stulpeliai if st in X.columns]

    X = pd.get_dummies(
        X,
        columns=esami_kategoriniai,
        dummy_na=False
    )

    print("Požymių stulpelių kiekis po get_dummies:", len(X.columns))
    print("X forma:", X.shape)
    print("y forma:", y.shape)
    print()

    # ---------------------------------------------------------
    # Train/test split
    # ---------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    print("Train/Test padalinimas atliktas.")
    print(f"X_train dydis: {X_train.shape}")
    print(f"X_test dydis: {X_test.shape}")
    print(f"y_train dydis: {y_train.shape}")
    print(f"y_test dydis: {y_test.shape}")
    print()

    # ---------------------------------------------------------
    # Standartizavimas
    # ---------------------------------------------------------
    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("Standartizavimas atliktas.")
    print()

    return X_train_scaled, X_test_scaled, y_train, y_test


def skaiciuoti_metrikas(y_test, y_pred):
    """
    Apskaičiuoja svarbiausias klasifikacijos metrikas.
    """

    accuracy = accuracy_score(y_test, y_pred)
    balanced_acc = balanced_accuracy_score(y_test, y_pred)

    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        y_test,
        y_pred,
        average="macro",
        zero_division=0,
    )

    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0,
    )

    return {
        "accuracy": round(accuracy, 4),
        "balanced_accuracy": round(balanced_acc, 4),
        "precision_macro": round(precision_macro, 4),
        "recall_macro": round(recall_macro, 4),
        "f1_macro": round(f1_macro, 4),
        "precision_weighted": round(precision_weighted, 4),
        "recall_weighted": round(recall_weighted, 4),
        "f1_weighted": round(f1_weighted, 4),
    }


def gauti_mlp_bandymu_sarasa():
    """
    Sugeneruoja 24 MLP bandymų kombinacijas.

    6 sluoksnių variantai
    2 activation variantai
    2 alpha variantai
    2 learning rate variantai

    Iš viso 6 * 2 * 2 * 2 = 48 kombinacijos,
    bet šiam etapui pasiimame pirmas 24.
    """

    hidden_layer_sizes_variantai = [
        (16,),
        (32,),
        (64,),
        (32, 16),
        (64, 32),
        (64, 32, 16),
    ]

    activation_variantai = ["relu", "tanh"]
    alpha_variantai = [0.0001, 0.001]
    learning_rate_variantai = [0.0005, 0.001]

    visos_kombinacijos = list(
        itertools.product(
            hidden_layer_sizes_variantai,
            activation_variantai,
            alpha_variantai,
            learning_rate_variantai,
        )
    )

    return visos_kombinacijos[:24]


def paleisti_mlp_eksperimentus_1000():
    """
    Pagrindinė funkcija:
    1. paruošia duomenis
    2. paleidžia 24 MLP bandymus
    3. surenka metrikas
    4. išsaugo rezultatų lentelę
    """

    failo_kelias = "06_rezultatai/modelio_duomenys_1000.csv"

    X_train_scaled, X_test_scaled, y_train, y_test = paruosti_duomenis(failo_kelias)

    bandymu_sarasas = gauti_mlp_bandymu_sarasa()

    print("=" * 80)
    print("PRASIDEDA MLP 1000 EKSPERIMENTAI")
    print("=" * 80)
    print(f"Suplanuota bandymų: {len(bandymu_sarasas)}")
    print()

    rezultatai = []

    warnings.filterwarnings("ignore", category=ConvergenceWarning)

    for bandymo_nr, kombinacija in enumerate(bandymu_sarasas, start=1):
        hidden_layer_sizes, activation, alpha, learning_rate_init = kombinacija

        print("-" * 80)
        print(f"BANDYMAS NR. {bandymo_nr}")
        print(f"hidden_layer_sizes = {hidden_layer_sizes}")
        print(f"activation         = {activation}")
        print(f"alpha              = {alpha}")
        print(f"learning_rate_init = {learning_rate_init}")

        try:
            modelis = MLPClassifier(
                hidden_layer_sizes=hidden_layer_sizes,
                activation=activation,
                solver="adam",
                alpha=alpha,
                learning_rate_init=learning_rate_init,
                batch_size=32,
                max_iter=1000,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.2,
                n_iter_no_change=20,
            )

            modelis.fit(X_train_scaled, y_train)
            y_pred = modelis.predict(X_test_scaled)

            metrikos = skaiciuoti_metrikas(y_test, y_pred)

            vieno_bandymo_rezultatas = {
                "bandymo_nr": bandymo_nr,
                "hidden_layer_sizes": str(hidden_layer_sizes),
                "activation": activation,
                "solver": "adam",
                "alpha": alpha,
                "learning_rate_init": learning_rate_init,
                "batch_size": 32,
                "max_iter": 1000,
                "early_stopping": True,
                "validation_fraction": 0.2,
                "n_iter_no_change": 20,
                "realios_iteracijos": modelis.n_iter_,
                **metrikos,
            }

            rezultatai.append(vieno_bandymo_rezultatas)

            print("Rezultatai:")
            print(vieno_bandymo_rezultatas)
            print()

        except Exception as klaida:
            print(f"Klaida bandyme nr. {bandymo_nr}: {klaida}")
            print()

            rezultatai.append(
                {
                    "bandymo_nr": bandymo_nr,
                    "hidden_layer_sizes": str(hidden_layer_sizes),
                    "activation": activation,
                    "solver": "adam",
                    "alpha": alpha,
                    "learning_rate_init": learning_rate_init,
                    "batch_size": 32,
                    "max_iter": 1000,
                    "early_stopping": True,
                    "validation_fraction": 0.2,
                    "n_iter_no_change": 20,
                    "realios_iteracijos": None,
                    "accuracy": None,
                    "balanced_accuracy": None,
                    "precision_macro": None,
                    "recall_macro": None,
                    "f1_macro": None,
                    "precision_weighted": None,
                    "recall_weighted": None,
                    "f1_weighted": None,
                }
            )

    # ---------------------------------------------------------
    # Rezultatų lentelė
    # ---------------------------------------------------------
    rezultatu_df = pd.DataFrame(rezultatai)

    rezultatu_df = rezultatu_df.sort_values(
        by=["f1_macro", "balanced_accuracy", "accuracy"],
        ascending=False,
        na_position="last",
    )

    isvedimo_failas = "06_rezultatai/mlp_1000_bandymu_lentele.csv"
    rezultatu_df.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

    print("=" * 80)
    print("VISI MLP BANDYMAI BAIGTI")
    print("=" * 80)
    print(f"Rezultatų lentelė išsaugota: {isvedimo_failas}")
    print()

    print("TOP 10 geriausių bandymų:")
    print(rezultatu_df.head(10))
    print()

    top5_failas = "06_rezultatai/mlp_1000_top5_bandymu_lentele.csv"
    rezultatu_df.head(5).to_csv(top5_failas, index=False, encoding="utf-8-sig")

    print(f"TOP 5 lentelė išsaugota: {top5_failas}")


if __name__ == "__main__":
    paleisti_mlp_eksperimentus_1000()