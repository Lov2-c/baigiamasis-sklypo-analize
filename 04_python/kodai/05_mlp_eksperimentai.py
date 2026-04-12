# =========================================================
# FAILAS: 05_mlp_eksperimentai.py
# PASKIRTIS:
# Atlikti 24 skirtingus MLPClassifier bandymus su skirtingais
# hyperparametrais ir išsaugoti visų bandymų rezultatus į CSV.
#
# Šis failas reikalingas baigiamojo darbo reikalavimui, kad
# neuroniniam modeliui būtų atlikta bent 20-30 įvairių pakeitimų.
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
    1. nuskaito modelio duomenų CSV
    2. užkoduoja target į skaitines reikšmes
    3. atskiria X ir y
    4. padalina duomenis į train ir test
    5. standartizuoja požymius

    Grąžina:
    X_train_scaled, X_test_scaled, y_train, y_test, originalų DataFrame
    """

    df = pd.read_csv(failo_kelias, encoding="utf-8-sig")

    print("Duomenys sėkmingai nuskaityti.")
    print(f"Eilučių skaičius: {len(df)}")
    print(f"Stulpelių skaičius: {len(df.columns)}")

    print("\nTarget klasių pasiskirstymas:")
    print(df["automatines_analizes_rezultatas"].value_counts())

    # ---------------------------------------------------------
    # Target kodavimas
    # ---------------------------------------------------------
    target_zodynas = {
        "galima_tiesiogiai": 0,
        "ribotai_galima": 1,
        "preliminariai_negalima": 2,
    }

    df["target_kodas"] = df["automatines_analizes_rezultatas"].map(target_zodynas)

    # ---------------------------------------------------------
    # Atskiriame požymius ir target
    # ---------------------------------------------------------
    X = df.drop(columns=["automatines_analizes_rezultatas", "target_kodas"])
    y = df["target_kodas"]

    print("\nPožymių stulpeliai:")
    print(list(X.columns))

    print("\nX forma:", X.shape)
    print("y forma:", y.shape)

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

    print("\nTrain/Test padalinimas atliktas.")
    print(f"X_train dydis: {X_train.shape}")
    print(f"X_test dydis: {X_test.shape}")
    print(f"y_train dydis: {y_train.shape}")
    print(f"y_test dydis: {y_test.shape}")

    # ---------------------------------------------------------
    # Standartizavimas
    # ---------------------------------------------------------
    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("\nStandartizavimas atliktas.")

    return X_train_scaled, X_test_scaled, y_train, y_test, df


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
    Sukuria 24 MLP bandymų kombinacijas.

    Kombinacijos parinktos taip, kad:
    - būtų pakankamai įvairios
    - bet ne per daug, kad būtų galima kontroliuoti rezultatų lentelę
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

    # Iš viso čia gauname 6 * 2 * 2 * 2 = 48 kombinacijas.
    # Kad bandymų nebūtų per daug, pasiimame pirmas 24.
    return visos_kombinacijos[:24]


def paleisti_mlp_eksperimentus():
    """
    Pagrindinė funkcija:
    1. paruošia duomenis
    2. sugeneruoja 24 MLP bandymus
    3. kiekvienam bandymui apmoko modelį
    4. išsaugo visų bandymų rezultatus į CSV
    5. parodo geriausius bandymus
    """

    failo_kelias = "06_rezultatai/modelio_duomenys_is_db.csv"

    X_train_scaled, X_test_scaled, y_train, y_test, df = paruosti_duomenis(failo_kelias)

    bandymu_sarasas = gauti_mlp_bandymu_sarasa()

    print("\n" + "=" * 80)
    print("PRADedami MLP bandymai")
    print("=" * 80)
    print(f"Iš viso suplanuota bandymų: {len(bandymu_sarasas)}")

    rezultatai = []

    # Kad console nebūtų užversta perspėjimais apie nesukonvergavimą
    warnings.filterwarnings("ignore", category=ConvergenceWarning)

    for bandymo_nr, kombinacija in enumerate(bandymu_sarasas, start=1):
        hidden_layer_sizes, activation, alpha, learning_rate_init = kombinacija

        print("\n" + "-" * 80)
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
                batch_size=16,
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
                "batch_size": 16,
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

        except Exception as klaida:
            print(f"Klaida bandyme nr. {bandymo_nr}: {klaida}")

            rezultatai.append(
                {
                    "bandymo_nr": bandymo_nr,
                    "hidden_layer_sizes": str(hidden_layer_sizes),
                    "activation": activation,
                    "solver": "adam",
                    "alpha": alpha,
                    "learning_rate_init": learning_rate_init,
                    "batch_size": 16,
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

    # Pirmiausia rikiuojame pagal svarbiausią metriką
    # Siūlau naudoti f1_macro, nes klasės nesubalansuotos
    rezultatu_df = rezultatu_df.sort_values(
        by=["f1_macro", "balanced_accuracy", "accuracy"],
        ascending=False,
        na_position="last",
    )

    isvedimo_failas = "06_rezultatai/mlp_bandymu_lentele.csv"
    rezultatu_df.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 80)
    print("VISI BANDYMAI BAIGTI")
    print("=" * 80)
    print(f"Rezultatų lentelė išsaugota: {isvedimo_failas}")

    print("\nTOP 10 geriausių bandymų:")
    print(rezultatu_df.head(10))

    # ---------------------------------------------------------
    # Išsaugome ir atskirą TOP 5 failą
    # ---------------------------------------------------------
    top5_failas = "06_rezultatai/mlp_top5_bandymu_lentele.csv"
    rezultatu_df.head(5).to_csv(top5_failas, index=False, encoding="utf-8-sig")

    print(f"\nTOP 5 bandymų lentelė išsaugota: {top5_failas}")


if __name__ == "__main__":
    paleisti_mlp_eksperimentus()