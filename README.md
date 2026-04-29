from tensorflow.python.keras.metrics import MAE

# 💧 Prédiction de la Dose de Coagulant (Al₂(SO₄)₃) — محطة سيدي خليفة

> **Mémoire de Master** — Traitement et modélisation de données temporelles issues de systèmes réels de traitement des eaux (2018–2019)

---

## 📌 Objectif du projet

Développer un système intelligent capable de **prédire automatiquement la dose optimale de sulfate d'aluminium Al₂(SO₄)₃** (coagulant) à injecter dans la station de traitement des eaux de **Sidi Khelifa**, à partir des cinq paramètres mesurés en temps réel :

| Paramètre | Symbole | Unité |
|-----------|---------|-------|
| Turbidité | TUR | NTU |
| Température | TE | °C |
| pH | pH | — |
| Conductivité électrique | SC | µS/cm |
| Oxygène dissous | DO | mg/L |

La variable cible (sortie) est : **AL2SO4** (mg/L)

---

## ⚙️ Pipeline du projet

Le projet suit un pipeline structuré en **9 étapes** :

```
Données brutes (XLSX)
        │
        ▼
[Étape 1] Chargement & nettoyage des données
        │
        ▼
[Étape 2] Analyse Top 5 MIN / MAX (avant filtrage)
        │
        ▼
[Étape 3] Filtrage par Ondelettes (Wavelet Denoising + Padding)
        │
        ▼
[Étape 3.5] Visualisation : signaux avant/après filtrage
        │
        ▼
[Étape 4] Préparation des données pour ML (X / y)
        │
        ▼
[Étape 5] Train/Test Split (80% / 20%)
        │
        ▼
[Étape 6] Entraînement & évaluation des 4 modèles
        │
        ▼
[Étape 7] Classement des features par importance
        │
        ▼
[Étape 8] Comparaison des modèles
        │
        ▼
[Étape 9] Sauvegarde (pkl, xlsx, png)
        │
        ▼
[Étape 10] Test Statique 

```

---

## 🌊 Filtrage par Ondelettes (Wavelet Denoising)

Le bruit dans les séries temporelles est éliminé **avant** tout apprentissage, grâce au filtrage par ondelettes avec padding symétrique pour éviter les effets de bord.

**Paramètres utilisés :**

| Paramètre | Valeur |
|-----------|--------|
| Ondelette | `db4` (Daubechies 4) |
| Niveau de décomposition | 3 |
| Mode de seuillage | `soft` |
| Mode de padding | `symmetric` |
| Taille du padding | 50 échantillons de chaque côté |

**Fonctions PyWavelets :**
- `pywt.wavedec()` — Décomposition multi-résolution
- `pywt.threshold()` — Seuillage doux (soft thresholding)
- `pywt.waverec()` — Reconstruction du signal filtré
- `np.pad()` — Padding symétrique pour éviter les distorsions aux bords

**Variables filtrées :** TUR, TE, pH, SC, DO, AL2SO4

---

## 🤖 Modèles de Machine Learning utilisés

### Modèles dans `Pipeline.py`

| Modèle | Type | Paramètres clés |
|--------|------|-----------------|
| **Random Forest** | Ensemble (Bagging) | `n_estimators=100`, `max_depth=10` |
| **XGBoost** | Ensemble (Boosting) | `n_estimators=100` |
| **Régression Linéaire** | Linéaire | — |
| **MLP (Réseau de neurones)** | Non-linéaire | `hidden_layer_sizes=(64, 32)`, `max_iter=500` |

---

### Résultats du `Pipeline.py` (pipeline principal)

| Modèle               | R²     | RMSE (mg/L) | MAE (mg/L) |
|----------------------|--------|-------------|------------|
| **Random Forest**    | **0.97** | **1**       | **0.48**   |
| Random Forest        | 0.96   | 1.17        | 0.58       |
| Neural Network (MLP) | 0.85   | 2.35        | 1.53       |
| Linear Regression    | 0.73   | 3.23        | 2.49       |

---

## 🔑 Importance des variables (Feature Importance)

L'importance des variables a été calculée par **4 méthodes** : Random Forest, XGBoost, Régression Linéaire, MLP — puis moyennée. Elle a aussi été validée par **SHAP** (SHapley Additive exPlanations).

### Classement moyen (toutes méthodes confondues)

| Rang | Variable | Importance moyenne |
|------|----------|--------------------|
|  1 | **Conductivité (SC)** | **55.53%**         |
|  2 | Température (TE) | 15.85%             |
|  3 | Oxygène dissous (DO) | 11.69%             |
| 4 | pH | 10.14%             |
| 5 | Turbidité (TUR) | 6.79%              |

> 💡 **Résultat clé** : La conductivité électrique (SC) est le facteur dominant dans la prédiction de la dose de coagulant.

---

## 🧪 Test Statique (`Test_Statique.py`) — Résultats Détaillés

### Description du test

Le script `Test_Statique.py` effectue un **test sur données réelles** en chargeant le modèle XGBoost sauvegardé (`best_coagulant_model.pkl`) et en lui soumettant **10 observations historiques datées** issues de la station Sidi Khelifa. Ce test permet de valider les performances du modèle en conditions réelles, sur des échantillons **non vus pendant l'entraînement**.

---

### 📋 Tableau des 10 échantillons de test — Résultats complets

| Cas (Date) | TUR (NTU) | SC (µS/cm) | Dose réelle (mg/L) | Dose prédite (mg/L) | Erreur absolue (mg/L) |
|---|---|---|---|---|---|
| 01/01/2018 | 16.0 | 1284 | 19.71 | 19.32 | **0.38** |
| 15/01/2018 | 10.6 | 1287 | 16.36 | 19.49 | 3.14 |
| 30/04/2018 | 8.4  | 1245 | 11.76 | 15.54 | 3.79 |
| 12/05/2018 | 9.4  | 1238 | 14.95 | 15.43 | **0.48** |
| 05/06/2018 | 14.2 | 1221 | 21.84 | 20.83 | 1.01 |
| 23/06/2018 | 6.2  | 1213 | 22.34 | 22.15 | **0.19** |
| 12/09/2018 | 6.7  | 1173 | 14.55 | 19.61 | 5.07 |
| 25/10/2018 | 32.7 | 1154 | 32.67 | 26.29 | 6.38 |
| 05/02/2019 | 38.0 | 1179 | 22.02 | 23.49 | 1.47 |
| 25/03/2019 | 17.1 | 1142 | 36.36 | 31.29 | 5.07 |

> 🟢 Les **meilleures prédictions** (erreur < 1 mg/L) : 01/01/2018, 12/05/2018, 23/06/2018  

---

### 📊 Métriques globales sur le test statique (10 échantillons)

| Métrique | Valeur | Interprétation |
|----------|--------|----------------|
| **R²** | **0.7869** | Le modèle explique ~79% de la variance des doses réelles |
| **MAE** | **2.70 mg/L** | Erreur moyenne absolue de 2.70 mg/L par prédiction |
| **RMSE** | **3.46 mg/L** | Erreur quadratique moyenne (plus sensible aux grands écarts) |


---

## 🧩 Explication Étape par Étape du Code `Test_Statique.py`

### Étape 1 — Chargement du modèle et des features

```python
import joblib
model = joblib.load("best_coagulant_model.pkl")
features = joblib.load("features_list.pkl")
```

**Explication :** Le modèle XGBoost entraîné est chargé depuis le fichier `.pkl` généré par `Pipeline.py`. La liste des features (`['pH', 'TUR', 'TE', 'SC', 'DO']`) est également chargée pour garantir que les colonnes d'entrée sont dans le **même ordre** qu'à l'entraînement. C'est une précaution essentielle pour éviter toute erreur de correspondance de variables.

---

### Étape 2 — Définition des 10 cas de test réels

```python
test_cases = [
    {"date": "1/1/2018",  "pH": ..., "TUR": 16.0,  "TE": ..., "SC": 1284.0, "DO": ..., "dose_reelle": 19.71},
    {"date": "15/1/2018", "pH": ..., "TUR": 10.6,  "TE": ..., "SC": 1287.0, "DO": ..., "dose_reelle": 16.36},
    # ....
]
```
**Explication :** Les 10 observations sont définies manuellement à partir des relevés réels de la station Sidi Khelifa (période 2018–2019). Chaque cas contient les 5 paramètres d'entrée (pH, TUR, TE, SC, DO) ainsi que la **dose réelle injectée** ce jour-là, qui sert de référence pour évaluer la prédiction.

---

### Étape 3 — Construction du DataFrame de test

```python
import pandas as pd
df_test = pd.DataFrame(test_cases)
X_test = df_test[features]  # Sélection des colonnes dans le bon ordre
```

**Explication :** Les cas de test sont convertis en DataFrame Pandas. Seules les colonnes correspondant aux features d'entrée du modèle sont sélectionnées, dans le **même ordre** que lors de l'entraînement. Cela garantit la cohérence avec la structure attendue par XGBoost.

---

### Étape 4 — Génération des prédictions

```python
y_pred = model.predict(X_test)
```

**Explication :** Le modèle XGBoost prédit la dose de coagulant (en mg/L) pour chacun des 10 échantillons. Les prédictions sont stockées dans le vecteur `y_pred`. Aucun pré-traitement supplémentaire n'est nécessaire ici, car les données de test statique sont directement dans les unités originales (le modèle a été entraîné sur des données filtrées par ondelettes, mais le test statique utilise les valeurs brutes pour simuler un usage en temps réel).

---

### Étape 5 — Calcul de l'erreur absolue et affichage

```python
y_real = df_test["dose_reelle"].values
erreurs = abs(y_pred - y_real)

for i, row in df_test.iterrows():
    print(f"{row['date']:40s} {row['TUR']:8.1f} {row['SC']:8.0f} {y_real[i]:12.2f} {y_pred[i]:12.2f} {erreurs[i]:10.2f}")
```

**Explication :** Pour chaque observation, on calcule l'**erreur absolue** (|dose prédite − dose réelle|) et on affiche un tableau récapitulatif. L'erreur absolue est préférée ici car elle est directement interprétable en mg/L : par exemple, une erreur de 0.38 mg/L signifie que la prédiction est presque parfaite, tandis qu'une erreur de 6.38 mg/L signifie un écart plus significatif.

---

### Étape 6 — Calcul des métriques globales

```python
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import numpy as np

r2   = r2_score(y_real, y_pred)
mae  = mean_absolute_error(y_real, y_pred)
rmse = np.sqrt(mean_squared_error(y_real, y_pred))

print(f"R²   = {R²:.4f}")
print(f"MAE  = {MAE:.2f} mg/L")
print(f"RMSE = {RMSE:.2f} mg/L")
```

**Explication :** Trois métriques de performance sont calculées :

- **R² (Coefficient de détermination)** : mesure la proportion de la variance de la dose réelle expliquée par le modèle. Un R² de 0.7869 signifie que ~79% de la variabilité est capturée par le modèle sur ces 10 échantillons.
- **MAE (Mean Absolute Error)** : erreur moyenne absolue. Une MAE de 2.70 mg/L signifie qu'en moyenne, la prédiction est à ±2.70 mg/L de la dose réelle.
- **RMSE (Root Mean Squared Error)** : erreur quadratique moyenne. Elle est plus sensible aux grandes erreurs. Un RMSE de 3.46 mg/L (> MAE) confirme qu'il y a quelques cas avec des erreurs élevées (comme le 25/10/2018).

---

### Étape 7 — Affichage du résumé final

```python
print(f"Modèle: XGBoost")
print(f"R² sur test statique: {R²:.4f}")
print(f"Erreur moyenne (MAE): {MAE:.2f} mg/L")
```

**Explication :** Un résumé concis est affiché en fin d'exécution. Ce résumé confirme le modèle utilisé et ses performances sur les données de terrain. Il sert de rapport rapide pour l'opérateur ou l'ingénieur de la station.

---

## ✅ Garantie : aucune fuite de données (No Data Leakage)

| Règle | Statut |
|-------|--------|
| AL2SO4 absent de X (entrées) | ✅ Vérifié à chaque étape |

---

## 🛠️ Technologies utilisées

| Bibliothèque | Usage |
|-------------|-------|
| **Python** | Langage principal |
| **Pandas** | Chargement, nettoyage, manipulation des données |
| **NumPy** | Calcul scientifique et opérations matricielles |
| **PyWavelets** | Filtrage par ondelettes (`wavedec`, `waverec`, `threshold`) |
| **Scikit-learn** | Modèles ML, normalisation, évaluation (`R²`, `RMSE`, `MAE`) |
| **XGBoost** | Modèle de gradient boosting optimisé |
| **SHAP** | Interprétation et sélection des features |
| **Matplotlib** | Visualisation des résultats |
| **Seaborn** | Analyse statistique et matrices de corrélation |
| **Joblib** | Sauvegarde/chargement des modèles `.pkl` |

### Installation

```bash
py -m pip install pandas numpy scikit-learn PyWavelets xgboost shap matplotlib seaborn joblib openpyxl
```

---

## 🚀 Utilisation

### 1. Exécuter le pipeline complet

```bash
py Pipeline.py
```

### 2. Tester sur données réelles

```bash
py Test_Statique.py
```

Nécessite : `best_coagulant_model.pkl` et `features_list.pkl` (générés par Pipeline.py)

---

## 📋 Données

- **Source** : Station de traitement des eaux de Sidi Khelifa, Algérie
- **Période** : 2018–2019 (données journalières)
- **Nombre d'observations** : 730 jours
- **Valeurs manquantes** : aucune
- **Split** : 80% entraînement / 20% test (aléatoire, `random_state=42`)
---
 