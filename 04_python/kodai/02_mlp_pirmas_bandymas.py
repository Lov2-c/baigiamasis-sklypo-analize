# =========================================================
# FAILAS: 02_mlp_pirmas_bandymas.py
# PASKIRTIS:
# Pirmas bazinis neuroninio modelio bandymas naudojant
# sklearn MLPClassifier.
# =========================================================

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


def paleisti_mlp_modeli():
    """
    Funkcija:
    1. nuskaito modelio duomenis
    2. užkoduoja target į skaičius
    3. atskiria X ir y
    4. padalina duomenis į train ir test
    5. standartizuoja požymius
    6. apmoko MLPClassifier
    7. parodo modelio rezultatus
    """

    # ---------------------------------------------------------
    # 1. Nuskaitome paruoštą modelio failą
    # ---------------------------------------------------------
    failo_kelias = "06_rezultatai/modelio_duomenys_is_db.csv"
    df = pd.read_csv(failo_kelias, encoding="utf-8-sig")

    print("Duomenys sėkmingai nuskaityti.")
    print(f"Eilučių skaičius: {len(df)}")
    print(f"Stulpelių skaičius: {len(df.columns)}")

    # ---------------------------------------------------------
    # 2. Target užkodavimas į skaičius
    # ---------------------------------------------------------
    target_zodynas = {
        "galima_tiesiogiai": 0,
        "ribotai_galima": 1,
        "preliminariai_negalima": 2
    }

    df["target_kodas"] = df["automatines_analizes_rezultatas"].map(target_zodynas)

    print("\nTarget kodavimo žodynas:")
    print(target_zodynas)

    print("\nTarget klasių pasiskirstymas:")
    print(df["automatines_analizes_rezultatas"].value_counts())

    # ---------------------------------------------------------
    # 3. Atskiriame X ir y
    # ---------------------------------------------------------
    X = df.drop(columns=["automatines_analizes_rezultatas", "target_kodas"])
    y = df["target_kodas"]

    print("\nX forma:", X.shape)
    print("y forma:", y.shape)

    # ---------------------------------------------------------
    # 4. Padaliname į train ir test
    # ---------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    print("\nTrain/Test padalinimas atliktas.")
    print(f"X_train dydis: {X_train.shape}")
    print(f"X_test dydis: {X_test.shape}")
    print(f"y_train dydis: {y_train.shape}")
    print(f"y_test dydis: {y_test.shape}")

    # ---------------------------------------------------------
    # 5. Standartizuojame duomenis
    # ---------------------------------------------------------
    # Neuroniniams modeliams labai svarbu, kad požymiai būtų panašaus mastelio.
    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("\nDuomenų standartizavimas atliktas.")

    # ---------------------------------------------------------
    # 6. Sukuriame MLP modelį
    # ---------------------------------------------------------
    # hidden_layer_sizes=(32, 16) reiškia:
    # - pirmas paslėptas sluoksnis turi 32 neuronus
    # - antras paslėptas sluoksnis turi 16 neuronų
    modelis = MLPClassifier(
        hidden_layer_sizes=(32, 16),
        activation="relu",
        solver="adam",
        alpha=0.001,
        learning_rate_init=0.001,
        max_iter=1000,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.2,
        n_iter_no_change=20
    )

    # ---------------------------------------------------------
    # 7. Apmokome modelį
    # ---------------------------------------------------------
    modelis.fit(X_train_scaled, y_train)

    print("\nMLP modelis apmokytas.")
    print(f"Mokymosi iteracijų skaičius: {modelis.n_iter_}")

    # ---------------------------------------------------------
    # 8. Prognozės
    # ---------------------------------------------------------
    y_pred = modelis.predict(X_test_scaled)

    # ---------------------------------------------------------
    # 9. Vertinimas
    # ---------------------------------------------------------
    tikslumas = accuracy_score(y_test, y_pred)

    print("\n" + "=" * 80)
    print("MLP MODELIO REZULTATAI")
    print("=" * 80)
    print(f"Accuracy: {tikslumas:.4f}")

    klasiu_pavadinimai = [
        "galima_tiesiogiai",
        "ribotai_galima",
        "preliminariai_negalima"
    ]

    print("\nClassification report:")
    print(classification_report(y_test, y_pred, target_names=klasiu_pavadinimai, zero_division=0))

    print("Confusion matrix:")
    print(confusion_matrix(y_test, y_pred))

    # ---------------------------------------------------------
    # 10. Išsaugome test prognozes
    # ---------------------------------------------------------
    rezultatu_df = pd.DataFrame({
        "tikra_reiksme": y_test.values,
        "prognozuota_reiksme": y_pred
    })

    rezultatu_df.to_csv(
        "06_rezultatai/mlp_test_prognozes.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\nTest prognozės išsaugotos: 06_rezultatai/mlp_test_prognozes.csv")


if __name__ == "__main__":
    paleisti_mlp_modeli()