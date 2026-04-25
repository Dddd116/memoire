
# Importation de la bibliotheque pandas pour manipuler les tableaux de données
import pandas as pd

# Importation de NumPy pour les calculs numériques
import numpy as np

# Importation de matplotlib pour tracer les graphes
import matplotlib.pyplot as plt

# Importation de PyWavelets pour appliquer les ondelettes
import pywt


# ==========================================================
# 1. CHARGEMENT DES DONNÉES
# ==========================================================

# Afficher une ligne décorative
print("=" * 60)
# Titre du programme
print(" FILTRAGE PAR ONDELETTES - TRAITEMENT DES DONNÉES ")
# Ligne décorative
print("=" * 60)

# Nom du fichier Excel
file_name = "SIDI KHELIFA DATA-2018-2019.xlsx"
# Lire la feuille DATA-FINALE du fichier Excel
df = pd.read_excel(file_name, sheet_name="DATA-FINALE")


# ==========================================================
# CRÉATION DE LA COLONNE DATE
# ==========================================================

# Convertir YY MM DD en vraie date
df["DATE"] = pd.to_datetime(
    # Renommer les colonnes pour format date
    df[["YY", "MM", "DD"]].rename(
        columns={
            "YY": "year",
            "MM": "month",
            "DD": "day"
        }
    )
)

# Trier les lignes selon la date
df = df.sort_values("DATE").reset_index(drop=True)
# Message succès
print("Dataset chargé avec succès")
# Afficher nombre lignes
print("Nombre de lignes :", df.shape[0])


# ==========================================================
# VARIABLES UTILISÉES
# ==========================================================
# Variables de qualité d’eau à traiter
variables = ['TUR', 'TE', 'pH', 'SC', 'DO', 'AL2SO4']


# ==========================================================
# 2. FONCTION FILTRAGE ONDELETTES
# ==========================================================

# Fonction qui reçoit un signal et retourne signal filtré
def wavelet_filter(signal, wavelet='db4', level=3):
    # Convertir en tableau modifiable
    signal = np.array(signal, dtype=float).copy()
    # Décomposition ondelettes
    coeffs = pywt.wavedec(signal, wavelet, level=level)
    # Estimation du bruit
    sigma = np.median(np.abs(coeffs[-1])) / 0.6745
    # Calcul du seuil universel
    seuil = sigma * np.sqrt(2 * np.log(len(signal)))
    # Garder coefficients approximation
    coeffs_new = [coeffs[0]]
    # Parcourir coefficients détails
    for c in coeffs[1:]:
        # Supprimer petites valeurs = bruit
        c = pywt.threshold(c, seuil, mode='soft')
        # Ajouter coefficient filtré
        coeffs_new.append(c)
    # Reconstruction du signal propre
    signal_clean = pywt.waverec(coeffs_new, wavelet)
    # Retourner même longueur que signal original
    return signal_clean[:len(signal)]


# ==========================================================
# 3. APPLICATION DU FILTRAGE
# ==========================================================
# Copier dataframe original
df_clean = df.copy()
# Message lancement
print("\nFiltrage en cours...\n")
# Boucle sur chaque variable
for var in variables:
    # Supprimer valeurs manquantes et convertir tableau
    serie = df[var].dropna().to_numpy(copy=True, dtype=float)
    # Filtrer la variable
    filtered = wavelet_filter(serie)
    # Créer colonne vide remplie NaN
    full = np.full(len(df), np.nan)
    # Remplir avec signal filtré
    full[:len(filtered)] = filtered
    # Ajouter nouvelle colonne filtrée
    df_clean[var + "_FILTER"] = full
    # Message terminé
    print(var, " --> terminé")

# ==========================================================
# 4. INTERFACE 1 : COMPARAISON AVANT / APRÈS
# ==========================================================
# Créer figure avec 6 graphes
fig, axes = plt.subplots(3, 2, figsize=(15, 10))
# Titre principal
fig.suptitle(
    "Comparaison Signal Original / Signal Filtré",
    fontsize=16,
    fontweight='bold'
)
# Transformer matrice axes en tableau simple
axes = axes.ravel()
# Boucle affichage
for i, var in enumerate(variables):
    # Tracer signal original
    axes[i].plot(
        df["DATE"],
        df[var],
        label="Original",
        alpha=0.5
    )
    # Tracer signal filtré
    axes[i].plot(
        df["DATE"],
        df_clean[var + "_FILTER"],
        label="Filtré",
        linewidth=2
    )
    # Titre graphe
    axes[i].set_title(var)
    # Légende
    axes[i].legend()
    # Grille
    axes[i].grid(True)
# Ajuster espaces
plt.tight_layout()
# Afficher graphes
plt.show()


# ==========================================================
# 5. INTERFACE 2 : AFFICHAGE 5 MIN ET 5 MAX
# ==========================================================
print("\n" + "=" * 60)
print(" ANALYSE DES VALEURS EXTRÊMES ")
print("=" * 60)

# Boucle sur variables
for var in variables:
    print("\n------------------------------")
    print("Variable :", var)
    print("------------------------------")
    # Sélection colonne filtrée
    serie = df_clean[var + "_FILTER"].dropna()
    # Afficher 5 minimum
    print("\n5 Valeurs Minimum :")
    print(serie.nsmallest(5))
    # Afficher 5 maximum
    print("\n5 Valeurs Maximum :")
    print(serie.nlargest(5))

# ==========================================================
# 6. CALCUL RÉDUCTION BRUIT
# ==========================================================

print("\n" + "=" * 60)
print(" RÉDUCTION DU BRUIT ")
print("=" * 60)
# Boucle calcul statistiques
for var in variables:
    # Signal original
    original = df[var].dropna().to_numpy()
    # Signal filtré
    filtered = df_clean[var + "_FILTER"].dropna().to_numpy()
    # Bruit supprimé
    noise = original - filtered
    # Pourcentage réduction bruit
    reduction = (1 - np.std(noise) / np.std(original)) * 100
    # Rapport signal/bruit
    snr = 20 * np.log10(np.std(original) / np.std(noise))
    # Affichage résultats
    print(f"{var:8s} | Réduction = {reduction:.2f}% | SNR = {snr:.2f} dB")

# ==========================================================
# 7. EXPORT EXCEL FINAL
# ==========================================================
# Nom fichier sortie
output = "dataset_filtre_final.xlsx"
# Sauvegarder données filtrées
df_clean.to_excel(output, index=False)
print("\n" + "=" * 60)
print(" EXPORT TERMINÉ ")
print("=" * 60)
# Afficher nom fichier
print("Fichier créé :", output)

# ==========================================================
# FIN DU PROGRAMME
# ==========================================================
print("\nTraitement terminé avec succès.")