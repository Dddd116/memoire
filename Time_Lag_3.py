 #==========================================
# ÉTAPE 3 : FEATURE ENGINEERING (LAG FEATURES)
# ==========================================

# Import des meilleures variables sélectionnées (Random Forest)
from Selection_aff_2 import best_features

print("\n" + "="*60)
print(" FEATURE ENGINEERING (LAG FEATURES) ")
print("="*60)

# ------------------------------------------
# 1. Charger les données filtrées (sans bruit)
# ------------------------------------------
from filtrage_aff_1 import df_clean

# ------------------------------------------
# 2. Définir les variables
# ------------------------------------------
features = best_features      # variables importantes
target = 'AL2SO4_FILTER'      # variable cible

# ------------------------------------------
# 3. Créer un dataset avec les variables utiles
# ------------------------------------------
df_features = df_clean[features + [target, 'DATE']].copy()

# ------------------------------------------
# 4. Création des LAG FEATURES
# ------------------------------------------
# Lags = valeurs des jours précédents
lags = [1, 2, 3]

# Copier le dataset
df_with_lag = df_features.copy()

# Boucle pour créer les colonnes lag
for lag in lags:
    for col in features:
        # Ajouter colonne décalée dans le temps
        df_with_lag[f"{col}_lag{lag}"] = df_with_lag[col].shift(lag)

# ------------------------------------------
# 5. Supprimer les valeurs manquantes (NaN)
# ------------------------------------------
# Les premières lignes contiennent NaN car pas d'historique
df_final = df_with_lag.dropna().copy()

# ------------------------------------------
# 6. Séparer X (features) et y (target)
# ------------------------------------------
# Supprimer DATE car inutile pour le modèle
X = df_final.drop(columns=['AL2SO4_FILTER', 'DATE'])
y = df_final['AL2SO4_FILTER']

# ------------------------------------------
# 7. Affichage des dimensions
# ------------------------------------------
print("\n📊 AVANT LAG :", df_features.shape)
print("📊 AVEC LAG :", df_with_lag.shape)
print("📊 FINAL :", df_final.shape)

# Affichage des premières lignes (avec NaN)
print("\nExemple AVEC NaN :")
print(df_with_lag.head())

# Affichage final (propre)
print("\nExemple FINAL :")
print(df_final.head())

# ------------------------------------------
# 8. Sauvegarde des fichiers Excel
# ------------------------------------------
# Dataset avec lag (contient NaN)
df_with_lag.to_excel("dataset_with_lag.xlsx", index=False)

# Dataset final prêt pour ML
df_final.to_excel("dataset_final_ml.xlsx", index=False)

print("\n✅ Fichiers générés :")
print(" - dataset_with_lag.xlsx")
print(" - dataset_final_ml.xlsx")