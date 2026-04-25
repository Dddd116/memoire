

# =======================================================
# ÉTAPE 2: FEATURE SELECTION (Corrélation + Random Forest)
# =======================================================

# Import des bibliothèques nécessaires
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
# Import du dataset déjà filtré (ondelettes)
from filtrage_aff_1 import df_clean

# Affichage titre
print("\n" + "="*60)
print(" FEATURE SELECTION ")
print("="*60)

# ==========================================
# 1. Sélection des variables
# ==========================================
# Variables explicatives (features)
features = ['TUR_FILTER', 'TE_FILTER', 'pH_FILTER', 'SC_FILTER', 'DO_FILTER']
# Variable cible (target)
target = 'AL2SO4_FILTER'
# Suppression des valeurs manquantes
df_ml = df_clean[features + [target]].dropna()
# X = variables d’entrée
X = df_ml[features]
# y = variable à prédire
y = df_ml[target]


# ==========================================
# 2. CORRELATION
# ==========================================
print("\n--- CORRELATION ---")
# Calcul de la corrélation entre chaque variable et la cible
correlations = X.corrwith(y)
# Tri des résultats du plus fort au plus faible
correlations = correlations.sort_values(ascending=False)
# Affichage des valeurs
print(correlations)
# Visualisation graphique
plt.figure(figsize=(8,5))
correlations.plot(kind='bar')
# Rotation des noms pour meilleure lisibilité
plt.xticks(rotation=90, fontsize=8)
# Titre du graphique
plt.title("Corrélation avec AL2SO4")
# Affichage de la grille
plt.grid(True)
# Ajustement automatique
plt.tight_layout()
# Affichage
plt.show()

# ==========================================
# 3. RANDOM FOREST (Importance des variables)
# ==========================================
print("\n--- RANDOM FOREST IMPORTANCE ---")
# Création du modèle Random Forest
model = RandomForestRegressor(
    n_estimators=100,   # Nombre d’arbres
    random_state=42     # Pour reproductibilité
)
# Entraînement du modèle
model.fit(X, y)
# Extraction de l’importance des variables
importances = model.feature_importances_
# Conversion en série pandas
importance_df = pd.Series(importances, index=features)
# Tri décroissant
importance_df = importance_df.sort_values(ascending=False)
# Affichage
print(importance_df)
# Visualisation
plt.figure(figsize=(8,5))
importance_df.plot(kind='bar')
# Rotation des labels
plt.xticks(rotation=90, fontsize=8)
# Titre
plt.title("Importance des variables (Random Forest)")
# Grille
plt.grid(True)
# Ajustement
plt.tight_layout()
# Affichage
plt.show()

# ==========================================
# 4. Sélection des meilleures variables
# ==========================================

print("\n--- BEST FEATURES ---")
# Sélection des variables importantes (seuil > 0.1)
best_features = importance_df[importance_df > 0.1].index.tolist()
# Résultat final
print("Variables sélectionnées :", best_features)