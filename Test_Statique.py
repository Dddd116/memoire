# ============================================================
#  TEST STATIQUE - XGBoost
# ============================================================

import numpy as np
import joblib
import os
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

print("\n" + "=" * 60)
print("  🔬 TEST STATIQUE - XGBoost")
print("=" * 60)

# ============================================================
#  CHARGEMENT DU MODÈLE 
# ============================================================

# Vérifier si le modèle existe
if not os.path.exists('best_coagulant_model.pkl'):
    print("❌ Modèle non trouvé! Exécutez d'abord Pipline.py")
    exit()

# Charger le modèle entraîné
best_model = joblib.load('best_coagulant_model.pkl')
features = joblib.load('features_list.pkl')

print(f"✅ Modèle chargé: {type(best_model).__name__}")
print(f"📋 Features: {features}")

# ============================================================
#  Définition des cas de test
# ============================================================

test_cases_real = [
    {"name": "1/1/2018", "pH": 8.15, "TUR": 16.0, "TE": 10.9, "SC": 1284, "DO": 8.05, "real_dose": 19.707},
    {"name": "15/1/2018", "pH": 8.34, "TUR": 10.6, "TE": 9.8, "SC": 1287, "DO": 9.47, "real_dose": 16.355},
    {"name": "30/4/2018", "pH": 7.99, "TUR": 8.36, "TE": 14.1, "SC": 1245, "DO": 7.42, "real_dose": 11.756},
    {"name": "12/5/2018", "pH": 7.99, "TUR": 9.37, "TE": 14.6, "SC": 1238, "DO": 7.10, "real_dose": 14.946},
    {"name": "5/6/2018", "pH": 7.81, "TUR": 14.2, "TE": 17.0, "SC": 1221, "DO": 5.88, "real_dose": 21.837},
    {"name": "23/6/2018", "pH": 7.70, "TUR": 6.2, "TE": 17.0, "SC": 1213, "DO": 4.71, "real_dose": 22.337},
    {"name": "12/9/2018", "pH": 7.64, "TUR": 6.73, "TE": 20.4, "SC": 1173, "DO": 1.82, "real_dose": 14.548},
    {"name": "25/10/2018", "pH": 7.73, "TUR": 32.67, "TE": 16.5, "SC": 1154, "DO": 5.26, "real_dose": 32.67},
    {"name": "5/2/2019", "pH": 8.52, "TUR": 38.0, "TE": 8.1, "SC": 1179, "DO": 10.60, "real_dose": 22.016},
    {"name": "25/3/2019", "pH": 8.46, "TUR": 17.1, "TE": 12.2, "SC": 1142, "DO": 9.58, "real_dose": 36.358},
]
# ============================================================
#  Exécution du test
# ============================================================

print("\n📈 RÉSULTATS DES PRÉDICTIONS :")
print("-" * 95)
print(f"{'Cas':<35} {'TUR':>8} {'SC':>8} {'Dose réelle':>12} {'Dose prédite':>12} {'Erreur':>10}")
print("-" * 95)

doses_reelles = []
doses_predites = []

for test in test_cases_real:
    # Préparer les valeurs
    values = np.array([[test['pH'], test['TUR'], test['TE'], test['SC'], test['DO']]])

    # XGBoost: prédiction
    dose_pred = best_model.predict(values)[0]

    # Stocker les valeurs
    doses_reelles.append(test['real_dose'])
    doses_predites.append(dose_pred)

    # Calculer l'erreur
    error = abs(test['real_dose'] - dose_pred)

    # Afficher
    print(f"{test['name']:<35} {test['TUR']:8.1f} {test['SC']:8.1f} "
          f"{test['real_dose']:12.2f} {dose_pred:12.2f} {error:10.2f}")

print("-" * 95)

# ============================================================
#  Calcul des métriques
# ============================================================

r2_real = r2_score(doses_reelles, doses_predites)
mae_real = mean_absolute_error(doses_reelles, doses_predites)
rmse_real = np.sqrt(mean_squared_error(doses_reelles, doses_predites))

print(f"\n📊 MÉTRIQUES SUR DONNÉES RÉELLES ({len(test_cases_real)} échantillons):")
print(f"   R²   = {r2_real:.4f}")
print(f"   MAE  = {mae_real:.2f} mg/L")
print(f"   RMSE = {rmse_real:.2f} mg/L")

# ============================================================
#  Résumé final
# ============================================================

print("\n" + "=" * 60)
print("  ✅ TEST STATIQUE TERMINÉ")
print("=" * 60)
print(f"\n📊 RÉSUMÉ:")
print(f"   Modèle: XGBoost")
print(f"   R² sur test statique: {r2_real:.4f}")
print(f"   Erreur moyenne (MAE): {mae_real:.2f} mg/L")
print("=" * 60)