# =========================================================
# FAILAS: 08_mlp_10000.py
# PASKIRTIS:
# Pirmas neuroninio modelio (MLPClassifier) bandymas
# su 10000 sklypų modelio failu Variantui B.
#
# TARGET:
# - vystymas_tiesiogiai_galimas
# - vystymas_galimas_su_salygomis
# - vystymas_labai_apribotas
# =========================================================

import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler


def paleisti_mlp_modeli_10000():
    """
    Funkcija:
    1. nuskaito 10000 sklypų modelio duomenis
    2. užkoduoja target
    3. paruošia X ir y
    4. tekstinius laukus paverčia į one-hot
    5. padalina į train/test
    6. standartizuoja duomenis
    7. apmoko MLPClassifier
    8. parodo metrikas
    9. išsaugo rezultatus
    """

    # ---------------------------------------------------------
    # 1. Nuskaitome duomenis
    # ---------------------------------------------------------
    failo_kelias = "06_rezultatai/modelio_duomenys_10000.csv"
    df = pd.read_csv(failo_kelias, encoding="utf-8-sig")

    print("Duomenys sėkmingai nuskaityti.")
    print(f"Eilučių skaičius: {len(df)}")
    print(f"Stulpelių skaičius: {len(df.columns)}")
    print()

    print("Target klasių pasiskirstymas:")
    print(df["vystymo_target"].value_counts())
    print()

    # ---------------------------------------------------------
    # 2. Target kodavimas
    # ---------------------------------------------------------
    target_zodynas = {
        "vystymas_tiesiogiai_galimas": 0,
        "vystymas_galimas_su_salygomis": 1,
        "vystymas_labai_apribotas": 2,
    }

    df["target_kodas"] = df["vystymo_target"].map(target_zodynas)

    print("Target kodavimo žodynas:")
    print(target_zodynas)
    print()

    # ---------------------------------------------------------
    # 3. Atskiriame X ir y
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

    print("Požymių stulpeliai:")
    print(list(X.columns))
    print()

    print("X forma:", X.shape)
    print("y forma:", y.shape)
    print()

    # ---------------------------------------------------------
    # 4. Train/Test split
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
    # 5. Standartizavimas
    # ---------------------------------------------------------
    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("Standartizavimas atliktas.")
    print()

    # ---------------------------------------------------------
    # 6. MLP modelis
    # ---------------------------------------------------------
    modelis = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver="adam",
        alpha=0.001,
        learning_rate_init=0.001,
        batch_size=32,
        max_iter=10000,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.2,
        n_iter_no_change=20,
    )

    # ---------------------------------------------------------
    # 7. Apmokymas
    # ---------------------------------------------------------
    modelis.fit(X_train_scaled, y_train)

    print("MLP modelis apmokytas.")
    print(f"Realios iteracijos: {modelis.n_iter_}")
    print()

    # ---------------------------------------------------------
    # 8. Prognozės
    # ---------------------------------------------------------
    y_pred = modelis.predict(X_test_scaled)

    # ---------------------------------------------------------
    # 9. Metrikos
    # ---------------------------------------------------------
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

    klasiu_pavadinimai = [
        "vystymas_tiesiogiai_galimas",
        "vystymas_galimas_su_salygomis",
        "vystymas_labai_apribotas",
    ]

    print("=" * 80)
    print("MLP 10000 REZULTATAI")
    print("=" * 80)
    print(f"Accuracy:           {accuracy:.4f}")
    print(f"Balanced accuracy:  {balanced_acc:.4f}")
    print(f"Precision macro:    {precision_macro:.4f}")
    print(f"Recall macro:       {recall_macro:.4f}")
    print(f"F1 macro:           {f1_macro:.4f}")
    print(f"Precision weighted: {precision_weighted:.4f}")
    print(f"Recall weighted:    {recall_weighted:.4f}")
    print(f"F1 weighted:        {f1_weighted:.4f}")
    print()

    print("Classification report:")
    print(classification_report(y_test, y_pred, target_names=klasiu_pavadinimai, zero_division=0))

    print("Confusion matrix:")
    print(confusion_matrix(y_test, y_pred))
    print()

    # ---------------------------------------------------------
    # 10. Išsaugome rezultatus
    # ---------------------------------------------------------
    rezultatu_df = pd.DataFrame([{
        "modelis": "MLP_10000",
        "hidden_layer_sizes": str((64, 32)),
        "activation": "relu",
        "solver": "adam",
        "alpha": 0.001,
        "learning_rate_init": 0.001,
        "batch_size": 32,
        "max_iter": 10000,
        "early_stopping": True,
        "validation_fraction": 0.2,
        "n_iter_no_change": 20,
        "realios_iteracijos": modelis.n_iter_,
        "accuracy": round(accuracy, 4),
        "balanced_accuracy": round(balanced_acc, 4),
        "precision_macro": round(precision_macro, 4),
        "recall_macro": round(recall_macro, 4),
        "f1_macro": round(f1_macro, 4),
        "precision_weighted": round(precision_weighted, 4),
        "recall_weighted": round(recall_weighted, 4),
        "f1_weighted": round(f1_weighted, 4),
        "train_eilutes": len(X_train),
        "test_eilutes": len(X_test),
    }])

    rezultatu_failas = "06_rezultatai/mlp_10000_rezultatai.csv"
    rezultatu_df.to_csv(rezultatu_failas, index=False, encoding="utf-8-sig")

    prognoziu_df = pd.DataFrame({
        "tikra_reiksme": y_test.values,
        "prognozuota_reiksme": y_pred,
    })

    prognoziu_failas = "06_rezultatai/mlp_10000_test_prognozes.csv"
    prognoziu_df.to_csv(prognoziu_failas, index=False, encoding="utf-8-sig")

    print("Išsaugoti failai:")
    print(rezultatu_failas)
    print(prognoziu_failas)


if __name__ == "__main__":
    paleisti_mlp_modeli_10000()