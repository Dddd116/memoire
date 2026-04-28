# =====================================================
# EXÉCUTION COMPLÈTE DU PIPELINE
# =====================================================
import subprocess
import sys

print("=" * 70)
print(" EXÉCUTION DU PIPELINE COMPLET EN 3 ÉTAPES")
print("=" * 70)

scripts = [
    ("etape_1.py", "Filtrage Wavelet"),
    ("etape_2.py", "Feature Engineering"),
    ("etape_3.py", "Split + SHAP + Modèles"),
]

for script, description in scripts:
    print(f"\n🚀 Lancement: {description}...")
    print("-" * 50)
    result = subprocess.run([sys.executable, script], capture_output=False)
    if result.returncode != 0:
        print(f"❌ Erreur dans {script}")
        break
    else:
        print(f"✅ {description} terminé avec succès")

print("\n" + "=" * 70)
print("✅ PIPELINE COMPLET TERMINÉ")
print("=" * 70)