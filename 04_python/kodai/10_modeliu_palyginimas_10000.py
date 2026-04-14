import pandas as pd

# ============================================
# 1. NUSKAITOME RANDOM FOREST REZULTATUS
# ============================================
rf_kelias = "06_rezultatai/random_forest_10000_rezultatai.csv"
rf_df = pd.read_csv(rf_kelias)

print("RandomForest rezultatų failas nuskaitytas.")
print(rf_df)
print()

# ============================================
# 2. NUSKAITOME VISŲ MLP BANDYMŲ LENTELĘ
# ============================================
mlp_bandymu_kelias = "06_rezultatai/mlp_10000_bandymu_lentele.csv"
mlp_bandymu_df = pd.read_csv(mlp_bandymu_kelias)

print("MLP bandymų failas nuskaitytas.")
print("Bandymų skaičius:", len(mlp_bandymu_df))
print()

# ============================================
# 3. PASIIMAME GERIAUSIĄ MLP BANDYMĄ
# ============================================
# Geriausią renkamės pagal macro F1, nes tai svarbi metrika kelių klasių uždaviniui
geriausias_mlp = mlp_bandymu_df.sort_values(
    by=["f1_macro", "balanced_accuracy", "accuracy"],
    ascending=False
).iloc[[0]].copy()

# Pervadiname modelio pavadinimą, kad būtų aiškiau lentelėje
geriausias_mlp["modelis"] = "MLP_10000_best"

print("Geriausias MLP bandymas:")
print(geriausias_mlp)
print()

# ============================================
# 4. SUVIENODINAME STULPELIUS
# ============================================
# Pasiimame visų stulpelių sąjungą
visi_stulpeliai = sorted(set(rf_df.columns).union(set(geriausias_mlp.columns)))

rf_df = rf_df.reindex(columns=visi_stulpeliai)
geriausias_mlp = geriausias_mlp.reindex(columns=visi_stulpeliai)

# ============================================
# 5. SUJUNGIAME Į GALUTINĘ LENTELĘ
# ============================================
galutinis_df = pd.concat([rf_df, geriausias_mlp], ignore_index=True)

print("=" * 80)
print("GALUTINIS MODELIŲ PALYGINIMAS")
print("=" * 80)
print(galutinis_df)
print()

# ============================================
# 6. IŠSAUGOME
# ============================================
isvedimo_kelias = "06_rezultatai/galutinis_modeliu_palyginimas_10000.csv"
galutinis_df.to_csv(isvedimo_kelias, index=False, encoding="utf-8-sig")

print("Galutinė modelių palyginimo lentelė išsaugota:")
print(isvedimo_kelias)