# =====================================================
# ÉTAPE 2 : FEATURE ENGINEERING
# ✅ AUCUNE FEATURE NE CONTIENT AL2SO4
# ✅ LAG et Rolling UNIQUEMENT sur les variables d'entrée
# =====================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')


class FeatureEngineer:
    """
    Classe pour créer les features (LAG, Rolling, Saisonnier)
    ⚠️ AL2SO4 n'est JAMAIS utilisé comme input
    """

    def __init__(self, features_base=None, lags=None):
        """
        Parameters:
        -----------
        features_base : list
            Variables d'entrée (sans AL2SO4)
        lags : list
            Valeurs de décalage temporel
        """
        self.features_base = features_base or [
            'TUR_FILTER', 'TE_FILTER', 'pH_FILTER', 'SC_FILTER', 'DO_FILTER'
        ]
        self.lags = lags or [1, 2, 3, 7]
        self.target = 'AL2SO4_FILTER'

    def add_seasonal_features(self, df):
        """Ajoute les features saisonnières"""
        df = df.copy()
        df['month'] = df['DATE'].dt.month
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['is_summer'] = df['month'].isin([6, 7, 8]).astype(int)
        df['is_winter'] = df['month'].isin([12, 1, 2]).astype(int)
        df['quarter'] = df['DATE'].dt.quarter

        print("✅ Features saisonnières ajoutées: month_sin, month_cos, is_summer, is_winter, quarter")
        return df

    def add_lag_features(self, df):
        """Ajoute les features de décalage temporel"""
        df = df.copy()
        lag_count = 0

        for lag in self.lags:
            for col in self.features_base:
                df[f"{col}_lag{lag}"] = df[col].shift(lag)
                lag_count += 1

        print(f"✅ {lag_count} LAG features ajoutées (lags={self.lags})")
        return df

    def add_rolling_features(self, df):
        """Ajoute les statistiques glissantes"""
        df = df.copy()

        for col in self.features_base:
            df[f"{col}_roll3_mean"] = df[col].rolling(3, min_periods=1).mean()
            df[f"{col}_roll7_mean"] = df[col].rolling(7, min_periods=1).mean()
            df[f"{col}_roll7_std"] = df[col].rolling(7, min_periods=1).std().fillna(0)
            df[f"{col}_diff1"] = df[col].diff(1).fillna(0)

        print("✅ Rolling statistics ajoutées (mean3, mean7, std7, diff1)")
        return df

    def fit_transform(self, df):
        """Applique toutes les transformations"""
        print("\n" + "=" * 70)
        print(" CRÉATION DES FEATURES (LAG, ROLLING, SAISONNIER)")
        print("=" * 70)

        df_result = df.copy()

        # 1. Features saisonnières
        df_result = self.add_seasonal_features(df_result)

        # 2. LAG features
        df_result = self.add_lag_features(df_result)

        # 3. Rolling statistics
        df_result = self.add_rolling_features(df_result)

        # Supprimer les NaN
        initial_len = len(df_result)
        df_result = df_result.dropna().reset_index(drop=True)
        print(f"\n✅ Après suppression NaN: {len(df_result)} obs (éliminé {initial_len - len(df_result)} lignes)")

        return df_result

    def get_X_y(self, df):
        """
        Sépare X (inputs) et y (target)
        ✅ Vérification qu'AL2SO4 n'est pas dans X
        """
        # Mots clés à exclure des inputs
        exclusions = ['AL2SO4', 'DATE', 'YY', 'MM', 'DD', 'HEAD', 'month']

        feature_cols = []
        for c in df.columns:
            if not any(mot in c for mot in exclusions):
                # Vérification supplémentaire pour AL2SO4
                if 'AL2' not in c.upper():
                    feature_cols.append(c)

        X = df[feature_cols]
        y = df[self.target]

        # Double vérification paranoïaque
        al2_cols = [c for c in X.columns if 'AL2' in c.upper()]
        if al2_cols:
            raise ValueError(f"🚨 ALERTE: AL2SO4 présent dans X! Colonnes: {al2_cols}")

        print(f"\n📊 X shape: {X.shape} ({len(feature_cols)} features)")
        print(f"🔒 Vérification: AUCUNE colonne AL2SO4 dans X")
        print(f"🎯 y shape: {y.shape}")

        return X, y, feature_cols


class DataValidator:
    """Classe pour valider les données"""

    @staticmethod
    def check_distribution_shift(X_train, X_test, y_train, y_test):
        """Vérifie le distribution shift"""
        print("\n" + "=" * 50)
        print(" ANALYSE DU DISTRIBUTION SHIFT")
        print("=" * 50)

        shift = abs(y_test.mean() - y_train.mean())
        print(f"📊 y_train: μ={y_train.mean():.2f}, σ={y_train.std():.2f}")
        print(f"📊 y_test:  μ={y_test.mean():.2f}, σ={y_test.std():.2f}")
        print(f"⚠️  Écart des moyennes: {shift:.2f} mg/L")

        if shift > 3:
            print("   🔴 Shift ÉLEVÉ → Performance probablement mauvaise")
        elif shift > 1.5:
            print("   🟠 Shift MOYEN → Performance modérée")
        else:
            print("   🟢 Shift FAIBLE → Bonne performance attendue")

        return shift

    @staticmethod
    def plot_correlation_matrix(df, features_base, target, save_path="2_matrice_correlation.png"):
        """Génère la matrice de corrélation"""
        plt.figure(figsize=(12, 8))
        corr_matrix = df[features_base + [target]].corr()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')
        plt.title("Matrice de corrélation (features brutes + target)")
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✅ Graphique: {save_path}")


# =====================================================
# EXÉCUTION PRINCIPALE
# =====================================================
if __name__ == "__main__":
    # Chargement des données filtrées
    df = pd.read_excel("dataset_filtre_final_optimise.xlsx")
    print(f"✅ Données chargées: {df.shape}")

    # Feature engineering
    engineer = FeatureEngineer()
    df_features = engineer.fit_transform(df)

    # Séparation X et y (vérification anti-fuite)
    X, y, feature_cols = engineer.get_X_y(df_features)

    # Sauvegarde
    df_features.to_excel("dataset_features_engineered.xlsx", index=False)
    print("\n✅ Sauvegardé: dataset_features_engineered.xlsx")

    # Visualisation
    validator = DataValidator()
    validator.plot_correlation_matrix(
        df_features,
        engineer.features_base,
        engineer.target
    )

    # Affichage des features créées
    print("\n" + "=" * 50)
    print(" LISTE DES FEATURES CRÉÉES")
    print("=" * 50)
    print(f"Total: {len(feature_cols)} features")
    print("\nExemples:")
    for i, f in enumerate(feature_cols[:10], 1):
        print(f"   {i:2d}. {f}")
    if len(feature_cols) > 10:
        print(f"   ... et {len(feature_cols) - 10} autres")