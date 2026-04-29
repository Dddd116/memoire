import pandas as pd
import numpy as np
import joblib
import warnings
import pywt
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

# ============================================================
# ÉTAPE 1 : CHARGEMENT DES DONNÉES BRUTES ORIGINALES
# ============================================================
print("\n" + "=" * 60)
print("  ÉTAPE 1 : CHARGEMENT DES DONNÉES BRUTES ORIGINALES")
print("=" * 60)

FILE_PATH = "SIDI KHELIFA DATA-2018-2019.xlsx"

try:
    df_raw = pd.read_excel(FILE_PATH)
    print(f"✅ Données chargées depuis {FILE_PATH}")
except FileNotFoundError:
    print(f"❌ Fichier '{FILE_PATH}' non trouvé. Vérifiez le chemin.")
    raise

print(f"📊 Shape initiale : {df_raw.shape}")
print(f"📋 Colonnes : {list(df_raw.columns)}")

# Garder uniquement les colonnes utiles
COLS_UTILES = ['DD', 'MM', 'YY', 'TUR', 'TE', 'pH', 'SC', 'DO', 'AL2SO4']
df_raw = df_raw[COLS_UTILES].copy()
print(f"\n✅ Colonnes retenues : {COLS_UTILES}")

# ============================================================
# ÉTAPE 2 : NETTOYAGE
# ============================================================
print("\n" + "=" * 60)
print("  ÉTAPE 2 : NETTOYAGE")
print("=" * 60)

df_clean = df_raw.copy()

# Construire la colonne DATE
df_clean['DATE'] = pd.to_datetime(
    df_clean[['YY', 'MM', 'DD']].rename(
        columns={'YY': 'year', 'MM': 'month', 'DD': 'day'}
    )
)
df_clean = df_clean.drop(columns=['DD', 'MM', 'YY'])
df_clean = df_clean.sort_values('DATE').reset_index(drop=True)

# Supprimer les valeurs manquantes
missing = df_clean.isnull().sum()
if missing.sum() > 0:
    print(f"⚠️ Valeurs manquantes détectées : {missing[missing > 0].to_dict()}")
    df_clean = df_clean.dropna()
    print(f"✅ Après suppression NaN : {df_clean.shape}")

# Supprimer les doublons
df_clean = df_clean.drop_duplicates(subset='DATE')

print(f"📊 Shape après nettoyage : {df_clean.shape}")

# ============================================================
# ÉTAPE 2.5 : TOP 5 MIN ET MAX DES VALEURS BRUTES
# ============================================================
print("\n" + "=" * 60)
print("  ÉTAPE 2.5 : TOP 5 MIN ET MAX DES DONNÉES BRUTES")
print("=" * 60)

print("\n📊 TOP 5 MIN ET MAX DES VALEURS BRUTES:")
print("-" * 60)

features_analysis = ['pH', 'TUR', 'TE', 'SC', 'DO']
target_analysis = 'AL2SO4'

for col in features_analysis + [target_analysis]:
    print(f"\n🔍 {col}:")
    print(f"   ✅ 5 PLUS PETITES VALEURS:")
    min_values = df_clean[col].nsmallest(5).values
    for i, val in enumerate(min_values, 1):
        print(f"      {i}. {val:.4f}")

    print(f"   🔴 5 PLUS GRANDES VALEURS:")
    max_values = df_clean[col].nlargest(5).values
    for i, val in enumerate(max_values, 1):
        print(f"      {i}. {val:.4f}")

# Sauvegarder uniquement les top 5 min/max
top5_data = {}
for col in features_analysis + [target_analysis]:
    top5_data[col] = {
        'top5_min': df_clean[col].nsmallest(5).tolist(),
        'top5_max': df_clean[col].nlargest(5).tolist(),
        'min_date': df_clean.loc[df_clean[col].idxmin(), 'DATE'].strftime('%Y-%m-%d') if not df_clean[
            col].isna().all() else None,
        'max_date': df_clean.loc[df_clean[col].idxmax(), 'DATE'].strftime('%Y-%m-%d') if not df_clean[
            col].isna().all() else None
    }

joblib.dump(top5_data, 'top5_data.pkl')
print("\n💾 Top 5 min/max sauvegardés dans 'top5_data.pkl'")

# ============================================================
# ÉTAPE 3 : FILTRAGE PAR ONDELETTES AVEC PADDING
# ============================================================
print("\n" + "=" * 60)
print("  ÉTAPE 3 : FILTRAGE PAR ONDELETTES AVEC PADDING")
print("=" * 60)

WAVELET = 'db4'
LEVEL = 3
THRESHOLD_MODE = 'soft'
PADDING_MODE = 'symmetric'
PADDING_SIZE = 50

print(f"🌊 Ondelette : {WAVELET}, Niveau : {LEVEL}")
print(f"📐 Mode seuillage : {THRESHOLD_MODE}")
print(f"🛡️ Padding mode : {PADDING_MODE}")
print(f"📏 Padding size : {PADDING_SIZE} échantillons de chaque côté")


def wavelet_denoise_with_padding(signal, wavelet='db4', level=3, mode='soft',
                                 padding_mode='symmetric', padding_size=50):
    signal_padded = np.pad(signal, pad_width=padding_size, mode=padding_mode)
    coeffs = pywt.wavedec(signal_padded, wavelet, level=level)
    sigma = np.median(np.abs(coeffs[-1])) / 0.6745
    thresh = sigma * np.sqrt(2 * np.log(len(signal_padded)))
    coeffs_thresh = [coeffs[0]]
    for detail in coeffs[1:]:
        coeffs_thresh.append(pywt.threshold(detail, thresh, mode=mode))
    denoised_padded = pywt.waverec(coeffs_thresh, wavelet)
    denoised_padded = denoised_padded[:len(signal_padded)]
    denoised = denoised_padded[padding_size:-padding_size]
    if len(denoised) != len(signal):
        if len(denoised) > len(signal):
            denoised = denoised[:len(signal)]
        else:
            denoised = np.pad(denoised, (0, len(signal) - len(denoised)), mode='edge')
    return denoised


df_wavelet = df_clean.copy()
filtered_signals = {}  # Pour stocker les signaux filtrés pour les graphiques

print("\n⏳ Application du filtre ondelettes avec padding...")
for col in ['TUR', 'TE', 'pH', 'SC', 'DO', 'AL2SO4']:
    if col in df_clean.columns:
        original = df_clean[col].values.astype(float)
        denoised = wavelet_denoise_with_padding(original, wavelet=WAVELET, level=LEVEL,
                                                mode=THRESHOLD_MODE, padding_mode=PADDING_MODE,
                                                padding_size=PADDING_SIZE)
        df_wavelet[col] = denoised
        filtered_signals[col] = {'original': original, 'denoised': denoised}
        diff = original - denoised
        noise_pct = np.std(diff) / (np.std(original) + 1e-10) * 100
        print(f"   ✓ {col}: bruit retiré {noise_pct:.1f}%")

print(f"✅ Filtrage avec padding terminé")

# ============================================================
# ÉTAPE 3.5 : DESSIN DES SIGNAUX AVANT ET APRÈS FILTRAGE
# ============================================================
print("\n" + "=" * 60)
print("  ÉTAPE 3.5 : DESSIN DES SIGNAUX AVANT/APRÈS FILTRAGE")
print("=" * 60)

# Créer une figure avec plusieurs sous-graphiques
fig, axes = plt.subplots(3, 2, figsize=(16, 12))
axes = axes.flatten()

colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown']
titles = ['Turbidité (TUR)', 'Température (TE)', 'pH', 'Conductivité (SC)', 'Oxygène Dissous (DO)', 'AL2SO4 (Target)']

for idx, col in enumerate(['TUR', 'TE', 'pH', 'SC', 'DO', 'AL2SO4']):
    ax = axes[idx]

    # Dessiner le signal original
    ax.plot(filtered_signals[col]['original'], color=colors[idx], alpha=0.6,
            linewidth=1, label='Signal original')

    # Dessiner le signal filtré
    ax.plot(filtered_signals[col]['denoised'], color='red', alpha=0.8,
            linewidth=2, label='Signal filtré (Wavelet)')

    ax.set_title(f'{titles[idx]} - Avant vs Après filtrage', fontsize=12, fontweight='bold')
    ax.set_xlabel('Temps (échantillons)', fontsize=10)
    ax.set_ylabel('Valeur', fontsize=10)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    # Ajouter une boîte avec le pourcentage de bruit retiré
    original = filtered_signals[col]['original']
    denoised = filtered_signals[col]['denoised']
    noise = np.std(original - denoised) / (np.std(original) + 1e-10) * 100
    ax.text(0.02, 0.95, f'Bruit retiré: {noise:.1f}%',
            transform=ax.transAxes, fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.suptitle('Comparaison des signaux avant et après filtrage par ondelettes (Wavelet Denoising)',
             fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('signaux_avant_apres_filtrage.png', dpi=150, bbox_inches='tight')
plt.show()

print("✅ Graphique 'signaux_avant_apres_filtrage.png' sauvegardé")

# ============================================================
# ÉTAPE 4 : PRÉPARATION POUR ML
# ============================================================
print("\n" + "=" * 60)
print("  ÉTAPE 4 : PRÉPARATION DES DONNÉES POUR ML")
print("=" * 60)

features = ['pH', 'TUR', 'TE', 'SC', 'DO']
target = 'AL2SO4'

print(f"📊 Features (entrées) : {features}")
print(f"🎯 Target (sortie)    : {target}")

X = df_wavelet[features].copy()
y = df_wavelet[target].copy()

mask = X.notna().all(axis=1) & y.notna()
X = X[mask]
y = y[mask]

print(f"📊 Nombre d'échantillons : {len(X)}")

# ============================================================
# ÉTAPE 5 : TRAIN/TEST SPLIT
# ============================================================
print("\n" + "=" * 60)
print("  ÉTAPE 5 : TRAIN/TEST SPLIT")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=True
)

print(f"📊 Train size : {X_train.shape}")
print(f"📊 Test size  : {X_test.shape}")

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)

print(f"✅ Normalisation appliquée")

# ============================================================
# ÉTAPE 6 : ENTRAÎNEMENT DES MODÈLES
# ============================================================
print("\n" + "=" * 60)
print("  ÉTAPE 6 : ENTRAÎNEMENT DES MODÈLES")
print("=" * 60)

models = {
    "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
    "XGBoost": XGBRegressor(n_estimators=100, random_state=42, verbosity=0),
    "Linear Regression": LinearRegression(),
    "Neural Network (MLP)": MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
}

results = {}
best_score = -np.inf
best_model = None
best_model_name = None
feature_importance_results = {}


def calculate_metrics(y_true, y_pred):
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-10))) * 100
    return {'R²': r2, 'MAE': mae, 'RMSE': rmse, 'MAPE': mape}


for name, model in models.items():
    print(f"\n{'=' * 50}")
    print(f"🔄 Entraînement : {name}")
    print(f"{'=' * 50}")

    if name in ["Linear Regression", "Neural Network (MLP)"]:
        model.fit(X_train_sc, y_train)
        y_pred_test = model.predict(X_test_sc)
    else:
        model.fit(X_train, y_train)
        y_pred_test = model.predict(X_test)

    test_metrics = calculate_metrics(y_test, y_pred_test)

    # Extraction de l'importance des features
    feature_importance = {}
    if name == "Random Forest":
        importance = model.feature_importances_
        for feat, imp in zip(features, importance):
            feature_importance[feat] = imp
    elif name == "XGBoost":
        importance = model.feature_importances_
        for feat, imp in zip(features, importance):
            feature_importance[feat] = imp
    elif name == "Linear Regression":
        coefficients = model.coef_
        for feat, coef in zip(features, coefficients):
            feature_importance[feat] = abs(coef)
    elif name == "Neural Network (MLP)":
        importance = np.mean(np.abs(model.coefs_[0]), axis=1)
        for feat, imp in zip(features, importance):
            feature_importance[feat] = imp

    total = sum(feature_importance.values())
    if total > 0:
        for feat in feature_importance:
            feature_importance[feat] = (feature_importance[feat] / total) * 100

    feature_importance_results[name] = feature_importance

    print(f"\n📊 PERFORMANCES SUR LE TEST:")
    print(f"   R²   = {test_metrics['R²']:.6f}")
    print(f"   MAE  = {test_metrics['MAE']:.6f} mg/L")
    print(f"   RMSE = {test_metrics['RMSE']:.6f} mg/L")
    print(f"   MAPE = {test_metrics['MAPE']:.2f}%")

    print(f"\n📊 IMPORTANCE DES FEATURES:")
    sorted_imp = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    for feat, imp in sorted_imp:
        bar = "█" * int(imp / 2)
        print(f"   {feat:<8} : {imp:6.2f}% {bar}")

    results[name] = {'test': test_metrics, 'feature_importance': feature_importance}

    if test_metrics['R²'] > best_score:
        best_score = test_metrics['R²']
        best_model = model
        best_model_name = name

# ============================================================
# ÉTAPE 7 : CLASSEMENT DES FEATURES
# ============================================================
print("\n" + "=" * 60)
print("  ÉTAPE 7 : CLASSEMENT DES FEATURES PAR IMPORTANCE")
print("=" * 60)

importance_df = pd.DataFrame(feature_importance_results).T
importance_df = importance_df[features]

print("\n📊 IMPORTANCE DES FEATURES SELON CHAQUE MODÈLE (%):")
print("=" * 60)
print(importance_df.to_string())
print("=" * 60)

avg_importance = importance_df.mean().sort_values(ascending=False)

print("\n🏆 CLASSEMENT MOYEN:")
print("-" * 40)
for i, (feat, imp) in enumerate(avg_importance.items(), 1):
    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
    print(f"   {medal} {feat}: {imp:.2f}%")

# Graphique de l'importance moyenne des features
plt.figure(figsize=(10, 6))
colors_bar = ['gold', 'silver', '#CD7F32', 'lightblue', 'lightgreen']
bars = plt.bar(avg_importance.index, avg_importance.values, color=colors_bar[:len(avg_importance)])
plt.title('Importance moyenne des features pour la prédiction de AL2SO4', fontsize=14, fontweight='bold')
plt.xlabel('Features (paramètres d\'entrée)', fontsize=12)
plt.ylabel('Importance (%)', fontsize=12)
plt.ylim(0, max(avg_importance.values) + 10)

# Ajouter les valeurs sur les barres
for bar, val in zip(bars, avg_importance.values):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
             f'{val:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('feature_importance.png', dpi=150, bbox_inches='tight')
plt.show()

print("✅ Graphique 'feature_importance.png' sauvegardé")

# ============================================================
# ÉTAPE 8 : COMPARAISON DES MODÈLES
# ============================================================
print("\n" + "=" * 60)
print("  ÉTAPE 8 : COMPARAISON DES MODÈLES")
print("=" * 60)

comparison_data = []
for name, metrics in results.items():
    comparison_data.append({
        'Modèle': name,
        'R²': metrics['test']['R²'],
        'MAE': metrics['test']['MAE'],
        'RMSE': metrics['test']['RMSE'],
        'MAPE': metrics['test']['MAPE']
    })

comparison_df = pd.DataFrame(comparison_data)
comparison_df = comparison_df.sort_values('R²', ascending=False)

print("\n📊 TABLEAU COMPARATIF:")
print("=" * 80)
print(comparison_df.to_string(index=False))
print("=" * 80)

# Graphique de comparaison des modèles
plt.figure(figsize=(12, 6))
x = np.arange(len(comparison_df))
width = 0.25

plt.bar(x - width, comparison_df['R²'], width, label='R²', color='green', alpha=0.7)
plt.bar(x, comparison_df['MAE'] / max(comparison_df['MAE']), width, label='MAE normalisé', color='red', alpha=0.7)
plt.bar(x + width, comparison_df['RMSE'] / max(comparison_df['RMSE']), width, label='RMSE normalisé', color='orange',
        alpha=0.7)

plt.xlabel('Modèles', fontsize=12)
plt.ylabel('Score', fontsize=12)
plt.title('Comparaison des performances des modèles', fontsize=14, fontweight='bold')
plt.xticks(x, comparison_df['Modèle'], rotation=45, ha='right')
plt.legend()
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('model_comparison.png', dpi=150, bbox_inches='tight')
plt.show()

print("✅ Graphique 'model_comparison.png' sauvegardé")

# ============================================================
# ÉTAPE 9 : SAUVEGARDE
# ============================================================
print("\n" + "=" * 60)
print("  ÉTAPE 9 : SAUVEGARDE")
print("=" * 60)

joblib.dump(best_model, 'best_coagulant_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(features, 'features_list.pkl')
joblib.dump(results, 'training_results.pkl')
joblib.dump(comparison_df, 'model_comparison.pkl')
joblib.dump(feature_importance_results, 'feature_importance_results.pkl')
joblib.dump(avg_importance, 'feature_importance_average.pkl')

best_metrics = {
    'model_name': best_model_name,
    'R2_score': results[best_model_name]['test']['R²'],
    'MAE': results[best_model_name]['test']['MAE'],
    'RMSE': results[best_model_name]['test']['RMSE'],
    'MAPE': results[best_model_name]['test']['MAPE']
}
joblib.dump(best_metrics, 'best_model_metrics.pkl')

# Sauvegarder dans Excel
comparison_df.to_excel('model_comparison.xlsx', index=False)
importance_df.to_excel('feature_importance.xlsx')

print("\n💾 Fichiers sauvegardés :")
print("   📁 best_coagulant_model.pkl        ← Meilleur modèle")
print("   📁 scaler.pkl                      ← Normalisateur")
print("   📁 features_list.pkl               ← Liste des features")
print("   📁 top5_data.pkl                   ← Top 5 min/max")
print("   📁 training_results.pkl            ← Résultats")
print("   📁 best_model_metrics.pkl          ← Métriques")
print("   📁 feature_importance_results.pkl  ← Importance par modèle")
print("   📁 feature_importance_average.pkl  ← Importance moyenne")
print("   📁 model_comparison.xlsx           ← Comparaison")
print("   📁 feature_importance.xlsx         ← Importance")
print("   🖼️ signaux_avant_apres_filtrage.png ← Graphique des signaux")
print("   🖼️ feature_importance.png          ← Graphique importance")
print("   🖼️ model_comparison.png            ← Graphique comparaison")

# ============================================================
# RAPPORT FINAL
# ============================================================
print("\n" + "=" * 60)
print("  📈 RAPPORT FINAL")
print("=" * 60)

r2_best = results[best_model_name]['test']['R²']
rmse_best = results[best_model_name]['test']['RMSE']
mae_best = results[best_model_name]['test']['MAE']
mape_best = results[best_model_name]['test']['MAPE']

print(f"\n🏆 MEILLEUR MODÈLE : {best_model_name}")
print(f"   R² = {r2_best:.4f}, RMSE = {rmse_best:.4f} mg/L, MAE = {mae_best:.4f} mg/L, MAPE = {mape_best:.2f}%")

print(f"\n📊 FEATURE IMPORTANCE:")
for i, (feat, imp) in enumerate(avg_importance.items(), 1):
    print(f"   {i}. {feat}: {imp:.2f}%")

print(f"\n✅ TOP 5 MIN/MAX sauvegardés dans 'top5_data.pkl'")
print(f"✅ Graphiques sauvegardés: signaux_avant_apres_filtrage.png, feature_importance.png, model_comparison.png")
