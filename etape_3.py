# =====================================================
# ÉTAPE 3 : SPLIT + SHAP + MODÈLES
# ✅ AUCUNE FUITE: AL2SO4 N'EST PAS DANS X
# =====================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.svm import SVR
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.preprocessing import RobustScaler
import shap
import warnings

warnings.filterwarnings('ignore')


class DataPreprocessor:
    """Classe pour préparer les données"""

    def __init__(self, test_size=0.20, random_state=42):
        self.test_size = test_size
        self.random_state = random_state
        self.scaler = RobustScaler()
        self.selected_features = None

    def split_data(self, X, y):
        """Split aléatoire 80/20"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state
        )

        print(f"\n📊 SPLIT {int((1 - self.test_size) * 100)}% / {int(self.test_size * 100)}%")
        print(f"   Train: {len(X_train)} obs")
        print(f"   Test:  {len(X_test)} obs")

        return X_train, X_test, y_train, y_test

    def scale_data(self, X_train, X_test):
        """Normalisation robuste"""
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        return X_train_scaled, X_test_scaled


class FeatureSelector:
    """Classe pour la sélection des features avec SHAP"""

    def __init__(self, threshold_percent=0.10):
        self.threshold_percent = threshold_percent
        self.selected_features = None
        self.shap_importance = None

    def select_features(self, X_train, y_train, feature_names):
        """
        Sélectionne les features importantes avec SHAP
        ✅ SHAP calculé UNIQUEMENT sur X_train (pas de leakage)
        """
        print("\n" + "=" * 50)
        print(" FEATURE SELECTION (SHAP)")
        print("=" * 50)

        # Modèle temporaire
        temp_model = RandomForestRegressor(
            n_estimators=100, max_depth=4, random_state=42, n_jobs=-1
        )
        temp_model.fit(X_train, y_train)

        # SHAP sur un échantillon de train
        explainer = shap.TreeExplainer(temp_model)
        shap_sample = X_train.sample(n=min(200, len(X_train)), random_state=42)
        shap_values = explainer.shap_values(shap_sample)

        # Importance moyenne
        self.shap_importance = pd.Series(
            np.abs(shap_values).mean(axis=0), index=feature_names
        ).sort_values(ascending=False)

        # Seuil
        threshold = self.shap_importance.max() * self.threshold_percent
        self.selected_features = self.shap_importance[
            self.shap_importance >= threshold
            ].index.tolist()

        print(f"✅ SHAP sélectionné {len(self.selected_features)} features sur {len(feature_names)}")
        print(f"   Seuil utilisé: {threshold:.6f}")

        print("\n🏆 Top 10 features:")
        for i, (f, imp) in enumerate(self.shap_importance.head(10).items(), 1):
            bar = "█" * int(imp / self.shap_importance.max() * 20)
            print(f"   {i:2d}. {f[:35]:35s}: {imp:.6f} {bar}")

        return self.selected_features

    def get_shap_importance_df(self):
        """Retourne le DataFrame d'importance SHAP"""
        return self.shap_importance.to_frame(name='SHAP_Importance')


class ModelTrainer:
    """Classe pour entraîner et évaluer les modèles"""

    def __init__(self):
        self.models = {
            "Ridge": Ridge(alpha=10.0),
            "SVR (RBF)": SVR(kernel='rbf', C=10.0, epsilon=0.5),
            "ElasticNet": ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=5000),
            "RandomForest": RandomForestRegressor(
                n_estimators=200, max_depth=4, random_state=42, n_jobs=-1
            ),
            "GradientBoosting": GradientBoostingRegressor(
                n_estimators=100, max_depth=2, learning_rate=0.05, random_state=42
            ),
        }
        self.results = None

    def train_and_evaluate(self, X_train, X_test, y_train, y_test, scaler=None):
        """
        Entraîne tous les modèles et évalue sur test
        """
        print("\n" + "=" * 50)
        print(" ENTRAÎNEMENT ET ÉVALUATION")
        print("=" * 50)

        results = []

        for name, model in self.models.items():
            # Déterminer si le modèle a besoin de scaling
            needs_scale = name in ["Ridge", "SVR (RBF)", "ElasticNet"]

            if needs_scale and scaler is not None:
                X_train_use = scaler.fit_transform(X_train)
                X_test_use = scaler.transform(X_test)
                model.fit(X_train_use, y_train)
                y_pred = model.predict(X_test_use)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            mae = mean_absolute_error(y_test, y_pred)

            results.append({
                "Model": name,
                "R2": r2,
                "RMSE": rmse,
                "MAE": mae,
                "Predictions": y_pred
            })

        self.results = pd.DataFrame(results).sort_values("R2", ascending=False)
        return self.results

    def print_results(self):
        """Affiche les résultats"""
        print(f"\n{'Rang':<4} {'Modèle':<20} {'R²':>10} {'RMSE':>10} {'MAE':>10} {'Statut'}")
        print("-" * 65)

        for i, row in self.results.iterrows():
            if row['R2'] > 0.5:
                st = "✅ BON"
            elif row['R2'] > 0.3:
                st = "⚠️ MOYEN"
            elif row['R2'] > 0:
                st = "〰️ FAIBLE"
            else:
                st = "❌ MAUVAIS"
            print(f"{i + 1:<4} {row['Model']:<20} {row['R2']:>10.4f} {row['RMSE']:>10.4f} {row['MAE']:>10.4f} {st}")

        return self.results.iloc[0]

    def save_results(self, path="3_resultats_modeles.xlsx"):
        """Sauvegarde les résultats"""
        self.results[['Model', 'R2', 'RMSE', 'MAE']].to_excel(path, index=False)
        print(f"✅ Sauvegardé: {path}")


class Visualizer:
    """Classe pour la visualisation"""

    @staticmethod
    def plot_results(y_test, predictions, shap_importance, best_model_name, best_r2,
                     save_path="3_resultats_modeles.png"):
        """Génère les graphiques des résultats"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle("Résultats: Split 80/20 + SHAP (Sans Data Leakage)",
                     fontsize=14, fontweight="bold")

        # SHAP Top 10
        ax1 = axes[0]
        shap_importance.head(10).plot(kind='barh', ax=ax1, color='#2a9d8f')
        ax1.set_title("Top 10 Features (SHAP Importance)")
        ax1.invert_yaxis()

        # Réel vs Prédit
        ax2 = axes[1]
        ax2.scatter(y_test, predictions, alpha=0.6, color='#e76f51', edgecolors='k', linewidth=0.3)
        mn, mx = min(y_test.min(), predictions.min()) - 1, max(y_test.max(), predictions.max()) + 1
        ax2.plot([mn, mx], [mn, mx], 'b--', linewidth=2, label='Idéal')
        ax2.set_title(f"{best_model_name} (R²={best_r2:.3f})")
        ax2.set_xlabel("Valeurs Réelles")
        ax2.set_ylabel("Valeurs Prédites")
        ax2.legend()
        ax2.grid(alpha=0.3)

        # Série temporelle
        ax3 = axes[2]
        ax3.plot(y_test.values, label='Réel', color='black', linewidth=2)
        ax3.plot(predictions, label='Prédit', color='#2a9d8f', linewidth=1.5, alpha=0.8)
        ax3.set_title("Comparaison sur Test (20%)")
        ax3.legend()
        ax3.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✅ Graphique: {save_path}")


# =====================================================
# EXÉCUTION PRINCIPALE
# =====================================================
if __name__ == "__main__":
    print("=" * 70)
    print(" ÉTAPE 3 : SPLIT 80/20 + SHAP + MODÈLES")
    print("=" * 70)

    # 1. Chargement
    df = pd.read_excel("dataset_features_engineered.xlsx")
    print(f"✅ Données chargées: {df.shape}")

    # 2. Séparation X et y (sans AL2SO4)
    from etape_2 import FeatureEngineer

    engineer = FeatureEngineer()
    X, y, feature_cols = engineer.get_X_y(df)

    # 3. Split
    preprocessor = DataPreprocessor(test_size=0.20, random_state=42)
    X_train, X_test, y_train, y_test = preprocessor.split_data(X, y)

    # 4. Feature Selection (SHAP)
    selector = FeatureSelector(threshold_percent=0.10)
    selected_features = selector.select_features(X_train, y_train, feature_cols)

    # 5. Réduction
    X_train_sel = X_train[selected_features]
    X_test_sel = X_test[selected_features]

    print(f"\n📊 Après sélection: X_train={X_train_sel.shape}, X_test={X_test_sel.shape}")

    # 6. Modèles
    trainer = ModelTrainer()
    scaler = RobustScaler()
    results = trainer.train_and_evaluate(X_train_sel, X_test_sel, y_train, y_test, scaler)

    # 7. Affichage
    best = trainer.print_results()

    # 8. Sauvegarde
    trainer.save_results()
    selector.get_shap_importance_df().to_excel("3_shap_importance.xlsx")
    print("✅ Sauvegardé: 3_shap_importance.xlsx")

    # 9. Visualisation
    Visualizer.plot_results(
        y_test,
        best['Predictions'],
        selector.shap_importance,
        best['Model'],
        best['R2']
    )

    # 10. Résumé
    print("\n" + "=" * 70)
    print("🏆 RÉSUMÉ FINAL")
    print("=" * 70)
    print(f"✅ Aucune fuite: AL2SO4 n'est JAMAIS dans X")
    print(f"📊 Features totales: {len(feature_cols)} → sélectionnées: {len(selected_features)}")
    print(f"🏆 Meilleur modèle: {best['Model']}")
    print(f"📈 R² = {best['R2']:.4f}")
    print(f"📉 RMSE = {best['RMSE']:.4f} | MAE = {best['MAE']:.4f}")