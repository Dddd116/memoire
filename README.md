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

> 💡 **Résultat clé** : La conductivité électrique (SC) est le facteur dominant dans la prédiction de la dose de coagulant .

---

## 🧪 Test statique (`test_statique.py`)

Un test sur **10 observations réelles datées** a été réalisé avec XGBoost :

| Date | TUR  | SC | Dose réelle | Dose prédite |
|------|------|----|-------------|--------------|
| 01/01/2018 | 16.0 | 1284 | 19.71       | — |
| 25/10/2018 | 5.95 | 1154 | 32.67       | — |
| 25/03/2019 | 17.1 | 1142 | 36.35       | — |
| … | …    | … | …           | … |

**Métriques sur le test statique :**
- R² = calculé sur 10 échantillons réels
- MAE et RMSE en mg/L

---

## ✅ Garantie : aucune fuite de données (No Data Leakage)

| Règle | Statut |
|-------|--------|
| AL2SO4 absent de X (entrées) | ✅ Vérifié à chaque étape |
 


---

## 🛠️ Technologies utilisées

| Bibliothèque | Usage |
|-------------|-------|
| **Python ** | Langage principal |
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
py test_statique.py
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

