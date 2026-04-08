# =========================================================
# FAILAS: 01_random_forest_pirmas_bandymas.py
# PASKIRTIS:
# Pirmas bazinis RandomForestClassifier modelio bandymas
# su mūsų paruoštu modelio CSV failu.
# =========================================================

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


def paleisti_random_forest_modeli():
    """
    Funkcija:
    1. nuskaito modelio duomenis
    2. atskiria požymius ir target
    3. paverčia target į skaitines reikšmes
    4. padalina duomenis į train ir test
    5. apmoko RandomForestClassifier
    6. parodo rezultatus
    """

    # ---------------------------------------------------------
    # 1. Nuskaitome paruoštą modelio failą
    # ---------------------------------------------------------
    failo_kelias = "06_rezultatai/modelio_duomenys_is_db.csv"

    df = pd.read_csv(failo_kelias, encoding="utf-8-sig")

    print("Duomenys sėkmingai nuskaityti.")
    print(f"Eilučių skaičius: {len(df)}")
    print(f"Stulpelių skaičius: {len(df.columns)}")
    print("\nPirmos 5 eilutės:")
    print(df.head())

    # ---------------------------------------------------------
    # 2. Target užkodavimas į skaičius
    # ---------------------------------------------------------
    # Pasirenkame aiškią rankinę kodavimo tvarką
    target_zodynas = {
        "galima_tiesiogiai": 0,
        "ribotai_galima": 1,
        "preliminariai_negalima": 2
    }

    df["target_kodas"] = df["automatines_analizes_rezultatas"].map(target_zodynas)

    print("\nTarget kodavimo žodynas:")
    print(target_zodynas)

    print("\nTarget reikšmės po užkodavimo:")
    print(df[["automatines_analizes_rezultatas", "target_kodas"]].head())

    # ---------------------------------------------------------
    # 3. Atskiriame X ir y
    # ---------------------------------------------------------
    X = df.drop(columns=["automatines_analizes_rezultatas", "target_kodas"])
    y = df["target_kodas"]

    print("\nPožymių (X) stulpeliai:")
    print(list(X.columns))

    print("\nX forma:", X.shape)
    print("y forma:", y.shape)

    # ---------------------------------------------------------
    # 4. Padaliname į train ir test dalis
    # ---------------------------------------------------------
    # stratify=y padeda išlaikyti panašų klasių pasiskirstymą
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
    # 5. Sukuriame RandomForest modelį
    # ---------------------------------------------------------
    modelis = RandomForestClassifier(
        n_estimators=200,      # kiek medžių miške
        max_depth=None,        # leidžiame medžiams augti laisvai
        random_state=42,
        class_weight="balanced"  # padeda, kai klasės nesubalansuotos
    )

    # ---------------------------------------------------------
    # 6. Apmokome modelį
    # ---------------------------------------------------------
    modelis.fit(X_train, y_train)

    print("\nModelis apmokytas.")

    # ---------------------------------------------------------
    # 7. Darome prognozes
    # ---------------------------------------------------------
    y_pred = modelis.predict(X_test)

    # ---------------------------------------------------------
    # 8. Vertiname modelį
    # ---------------------------------------------------------
    tikslumas = accuracy_score(y_test, y_pred)

    print("\n" + "=" * 80)
    print("MODELIO REZULTATAI")
    print("=" * 80)
    print(f"Accuracy: {tikslumas:.4f}")

    # Kad ataskaita būtų aiškesnė, turime ir klasių pavadinimus
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
    # 9. Parodome požymių svarbą
    # ---------------------------------------------------------
    svarbos_df = pd.DataFrame({
        "pozymis": X.columns,
        "svarba": modelis.feature_importances_
    })

    svarbos_df = svarbos_df.sort_values(by="svarba", ascending=False)

    print("\n" + "=" * 80)
    print("POŽYMIŲ SVARBA")
    print("=" * 80)
    print(svarbos_df)

    # ---------------------------------------------------------
    # 10. Išsaugome požymių svarbą į CSV
    # ---------------------------------------------------------
    isvedimo_failas = "06_rezultatai/random_forest_pozymiu_svarba.csv"
    svarbos_df.to_csv(isvedimo_failas, index=False, encoding="utf-8-sig")

    print(f"\nPožymių svarba išsaugota: {isvedimo_failas}")


if __name__ == "__main__":
    paleisti_random_forest_modeli()