## Mon Projet de Memoire

# Description

Ce projet de mémoire porte sur l’analyse, le traitement et la modélisation de données temporelles issues de systèmes réels.
L’objectif est d’améliorer la qualité des données, réduire le bruit, extraire les informations pertinentes et construire des modèles de prédiction performants à l’aide du Machine Learning.
# Pipeline du projet

• Filtrage par ondelettes : wavedec(), waverec(), threshold();
• Padding / Ajustement de taille des signaux : np.pad();
• Sélection des variables : feature_importances_, SHAP;
• Modèles utilisés : RandomForest , GradientBoosting , Ridge , SVR (RBF) , ElasticNet;
• Entraînement / Test / Prédiction : train_test_split(), fit(), predict();
• Évaluation des performances : RMSE, MAE, R2 .

# Technologies utilisées

• Python : langage principal du projet;
• Pandas : manipulation et analyse des données;
• NumPy : calcul scientifique et opérations matricielles;
• Matplotlib : visualisation des résultats;
• Seaborn : analyse statistique avancée;
• PyWavelets : filtrage par ondelettes;
• Scikit-learn : modèles de Machine Learning et évaluation;
• SHAP : interprétation des modèles.

# Comparaison des modèles

RandomForest est le meilleur modèle (R² = 0,742 ; RMSE = 3,09 ; MAE = 2,29). Il explique 74,2 % de la variance et présente les erreurs les plus faibles.
GradientBoosting suit de très près (R² = 0,740 ; RMSE = 3,11 ; MAE = 2,41), avec des performances quasi identiques.
Les modèles linéaires (Ridge : R² = 0,60 ; RMSE = 3,81 ; MAE = 2,91) ;
ElasticNet : (R² = 0,59 RMSE = 3,85 ; MAE = 2,91)
SVR (R² = 0,60 ; RMSE = 3,84 ; MAE = 2,80) obtiennent des scores nettement plus faibles, confirmant que les relations dans les données ne sont pas purement linéaires.


