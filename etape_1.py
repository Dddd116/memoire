# =====================================================
# ÉTAPE 1 : FILTRAGE ONDELETTES AVEC PADDING
# ✅ AL2SO4 est filtré mais N'EST PAS utilisé comme input
# =====================================================
import pandas as pd
import numpy as np
import pywt
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')


class WaveletFilter:
    """
    Classe pour le filtrage par ondelettes avec padding symétrique
    """

    def __init__(self, wavelet='db4', threshold_factor=0.8):
        self.wavelet = wavelet
        self.threshold_factor = threshold_factor
        self.params = {
            'TUR': {'level': 2, 'factor': 0.5, 'pad_size': 10},
            'SC': {'level': 4, 'factor': 0.9, 'pad_size': 20},
            'AL2SO4': {'level': 3, 'factor': 0.7, 'pad_size': 15},
            'TE': {'level': 3, 'factor': 0.7, 'pad_size': 15},
            'pH': {'level': 3, 'factor': 0.7, 'pad_size': 10},
            'DO': {'level': 3, 'factor': 0.7, 'pad_size': 10},
        }

    def _filter_signal(self, signal, level, threshold_factor, pad_size):
        """Filtre un signal avec padding"""
        signal = np.array(signal, dtype=float).copy()
        n = len(signal)

        # Gestion des NaN
        nans = np.isnan(signal)
        if nans.any():
            not_nan = np.where(~nans)[0]
            nan_idx = np.where(nans)[0]
            if len(not_nan) > 1:
                signal[nan_idx] = np.interp(nan_idx, not_nan, signal[not_nan])
            else:
                signal[nan_idx] = np.nanmean(signal)

        # Padding symétrique
        if pad_size is None:
            pad_size = min(15, n // 5)
        padded = np.pad(signal, pad_size, mode='reflect')

        # Décomposition
        coeffs = pywt.wavedec(padded, self.wavelet, level=level, mode='reflect')

        # Seuillage
        sigma = np.median(np.abs(coeffs[-1])) / 0.6745
        seuil = sigma * np.sqrt(2 * np.log(len(padded))) * threshold_factor

        coeffs_new = [coeffs[0]]
        for c in coeffs[1:]:
            coeffs_new.append(pywt.threshold(c, seuil, mode='soft'))

        # Reconstruction
        reconstructed = pywt.waverec(coeffs_new, self.wavelet, mode='reflect')
        if len(reconstructed) > len(padded):
            reconstructed = reconstructed[:len(padded)]
        signal_filtered = reconstructed[pad_size:-pad_size]

        # Ajustement longueur
        if len(signal_filtered) > n:
            signal_filtered = signal_filtered[:n]
        elif len(signal_filtered) < n:
            pad_extra = n - len(signal_filtered)
            signal_filtered = np.pad(signal_filtered, (0, pad_extra), mode='edge')

        return signal_filtered

    def fit_transform(self, df):
        """Applique le filtrage à toutes les variables"""
        df_result = df.copy()
        variables = ['TUR', 'TE', 'pH', 'SC', 'DO', 'AL2SO4']

        print("\n⏳ Application du filtrage Wavelet avec padding...\n")

        for var in variables:
            p = self.params[var]
            serie = df[var].to_numpy(dtype=float)
            original_mean = serie.mean()
            original_std = serie.std()

            df_result[f"{var}_FILTER"] = self._filter_signal(
                serie,
                level=p['level'],
                threshold_factor=p['factor'],
                pad_size=p['pad_size']
            )

            filtered_mean = df_result[f"{var}_FILTER"].mean()
            filtered_std = df_result[f"{var}_FILTER"].std()

            print(f"✅ {var:8s} → {var}_FILTER")
            print(f"   Original: μ={original_mean:.3f}, σ={original_std:.3f}")
            print(f"   Filtré:   μ={filtered_mean:.3f}, σ={filtered_std:.3f}\n")

        return df_result


class DataLoader:
    """Classe pour charger les données"""

    def __init__(self, file_path, sheet_name="DATA-FINALE"):
        self.file_path = file_path
        self.sheet_name = sheet_name

    def load(self):
        """Charge et prépare les données"""
        df = pd.read_excel(self.file_path, sheet_name=self.sheet_name)

        # Création de la colonne DATE
        df["DATE"] = pd.to_datetime(
            df[["YY", "MM", "DD"]].rename(
                columns={"YY": "year", "MM": "month", "DD": "day"}
            )
        )
        df = df.sort_values("DATE").reset_index(drop=True)

        print(f"✅ Données chargées: {df.shape}")
        print(f"📅 Période: {df['DATE'].min()} → {df['DATE'].max()}")

        return df


class PeakAnalyzer:
    """Classe pour analyser les pics (5 min et 5 max) pour toutes les variables"""

    @staticmethod
    def extract_all_peaks(df_original, df_filtered, variables, save_path="1_tous_les_pics_5min_5max.xlsx"):
        """
        Extrait les 5 plus petites et 5 plus grandes valeurs pour toutes les variables
        (originales et filtrées) dans un seul fichier
        """

        print("\n" + "=" * 70)
        print(" 📊 ANALYSE DES PICS (5 MIN / 5 MAX) - TOUTES LES VARIABLES")
        print("=" * 70)

        all_results = []

        for var in variables:
            # ========== VARIABLE ORIGINALE ==========
            orig_col = var
            if orig_col in df_original.columns:
                clean_orig = df_original[orig_col].dropna()

                if len(clean_orig) >= 5:
                    min_5_orig = clean_orig.nsmallest(5).values
                    max_5_orig = clean_orig.nlargest(5).values

                    all_results.append({
                        'Variable': f"{var} (ORIGINAL)",
                        'Type': 'Original',
                        'Min_1': min_5_orig[0] if len(min_5_orig) > 0 else None,
                        'Min_2': min_5_orig[1] if len(min_5_orig) > 1 else None,
                        'Min_3': min_5_orig[2] if len(min_5_orig) > 2 else None,
                        'Min_4': min_5_orig[3] if len(min_5_orig) > 3 else None,
                        'Min_5': min_5_orig[4] if len(min_5_orig) > 4 else None,
                        'Max_1': max_5_orig[0] if len(max_5_orig) > 0 else None,
                        'Max_2': max_5_orig[1] if len(max_5_orig) > 1 else None,
                        'Max_3': max_5_orig[2] if len(max_5_orig) > 2 else None,
                        'Max_4': max_5_orig[3] if len(max_5_orig) > 3 else None,
                        'Max_5': max_5_orig[4] if len(max_5_orig) > 4 else None,
                        'Mean': clean_orig.mean(),
                        'Std': clean_orig.std(),
                        'Min_Global': clean_orig.min(),
                        'Max_Global': clean_orig.max(),
                    })

            # ========== VARIABLE FILTRÉE ==========
            filt_col = f"{var}_FILTER"
            if filt_col in df_filtered.columns:
                clean_filt = df_filtered[filt_col].dropna()

                if len(clean_filt) >= 5:
                    min_5_filt = clean_filt.nsmallest(5).values
                    max_5_filt = clean_filt.nlargest(5).values

                    all_results.append({
                        'Variable': f"{var} (FILTRÉ)",
                        'Type': 'Filtré',
                        'Min_1': min_5_filt[0] if len(min_5_filt) > 0 else None,
                        'Min_2': min_5_filt[1] if len(min_5_filt) > 1 else None,
                        'Min_3': min_5_filt[2] if len(min_5_filt) > 2 else None,
                        'Min_4': min_5_filt[3] if len(min_5_filt) > 3 else None,
                        'Min_5': min_5_filt[4] if len(min_5_filt) > 4 else None,
                        'Max_1': max_5_filt[0] if len(max_5_filt) > 0 else None,
                        'Max_2': max_5_filt[1] if len(max_5_filt) > 1 else None,
                        'Max_3': max_5_filt[2] if len(max_5_filt) > 2 else None,
                        'Max_4': max_5_filt[3] if len(max_5_filt) > 3 else None,
                        'Max_5': max_5_filt[4] if len(max_5_filt) > 4 else None,
                        'Mean': clean_filt.mean(),
                        'Std': clean_filt.std(),
                        'Min_Global': clean_filt.min(),
                        'Max_Global': clean_filt.max(),
                    })

        # إنشاء DataFrame وتنسيقه
        df_results = pd.DataFrame(all_results)

        # تنسيق الأرقام
        for col in df_results.columns:
            if col not in ['Variable', 'Type']:
                df_results[col] = df_results[col].apply(lambda x: round(x, 4) if pd.notna(x) else x)

        # حفظ النتائج في ملف Excel واحد
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            df_results.to_excel(writer, sheet_name='Tous_les_pics', index=False)

            # إضافة إحصائيات إضافية في ورقة منفصلة
            stats_data = []
            for var in variables:
                for suffix, df_data in [('ORIGINAL', df_original), ('FILTRÉ', df_filtered)]:
                    col_name = var if suffix == 'ORIGINAL' else f"{var}_FILTER"
                    if col_name in df_data.columns:
                        clean = df_data[col_name].dropna()
                        stats_data.append({
                            'Variable': f"{var} ({suffix})",
                            'Nb_Observations': len(clean),
                            'Nb_NaN': df_data[col_name].isna().sum(),
                            'Mean': clean.mean(),
                            'Std': clean.std(),
                            'Min': clean.min(),
                            'Q1': clean.quantile(0.25),
                            'Median': clean.median(),
                            'Q3': clean.quantile(0.75),
                            'Max': clean.max(),
                            'IQR': clean.quantile(0.75) - clean.quantile(0.25),
                        })

            df_stats = pd.DataFrame(stats_data)
            for col in df_stats.columns:
                if col not in ['Variable', 'Nb_Observations', 'Nb_NaN']:
                    df_stats[col] = df_stats[col].apply(lambda x: round(x, 4) if pd.notna(x) else x)

            df_stats.to_excel(writer, sheet_name='Statistiques', index=False)

        # عرض النتائج في الطرفية
        print("\n" + "=" * 70)
        print(" 📋 RÉSULTATS DES PICS (5 MIN / 5 MAX)")
        print("=" * 70)

        for _, row in df_results.iterrows():
            print(f"\n{'─' * 60}")
            print(f"📊 **{row['Variable']}**")
            print(f"{'─' * 60}")
            print(f"📉 5 أصغر قيم (MIN): {row['Min_1']}, {row['Min_2']}, {row['Min_3']}, {row['Min_4']}, {row['Min_5']}")
            print(f"📈 5 أكبر قيم (MAX): {row['Max_1']}, {row['Max_2']}, {row['Max_3']}, {row['Max_4']}, {row['Max_5']}")
            print(f"📐 المتوسط: {row['Mean']} | الانحراف المعياري: {row['Std']}")
            print(f"   المدى الكلي: [{row['Min_Global']} → {row['Max_Global']}]")

        print(f"\n✅ تم حفظ النتائج في: {save_path}")
        return df_results, df_stats

    @staticmethod
    def plot_all_peaks(df_original, df_filtered, variables, save_path="1_tous_les_graphes_pics.png"):
        """رسم جميع المتغيرات مع تحديد القمم والقيعان في ملف واحد"""

        n_vars = len(variables)
        fig, axes = plt.subplots(n_vars, 2, figsize=(16, 4 * n_vars))
        fig.suptitle("Comparaison des pics: Original (gauche) vs Filtré (droite)",
                     fontsize=16, fontweight='bold')

        # إذا كان متغير واحد فقط، axes سيكون ثنائي الأبعاد بشكل مختلف
        if n_vars == 1:
            axes = axes.reshape(1, -1)

        for i, var in enumerate(variables):
            # ========== VARIABLE ORIGINALE (colonne de gauche) ==========
            ax_left = axes[i, 0]
            orig_col = var
            if orig_col in df_original.columns:
                clean_orig = df_original[orig_col].dropna()

                # رسم الإشارة
                ax_left.plot(clean_orig.index, clean_orig.values, 'b-', alpha=0.7, linewidth=1)

                # إيجاد القمم والقيعان
                min_5_idxs = clean_orig.nsmallest(5).index
                min_5_vals = clean_orig.nsmallest(5).values
                max_5_idxs = clean_orig.nlargest(5).index
                max_5_vals = clean_orig.nlargest(5).values

                # رسم القيعان (أخضر)
                ax_left.scatter(min_5_idxs, min_5_vals, color='green', s=80,
                                marker='v', zorder=5, edgecolors='black', linewidth=1)
                # رسم القمم (أحمر)
                ax_left.scatter(max_5_idxs, max_5_vals, color='red', s=80,
                                marker='^', zorder=5, edgecolors='black', linewidth=1)

                # إضافة تسميات
                for idx, val in zip(min_5_idxs, min_5_vals):
                    ax_left.annotate(f'{val:.1f}', (idx, val), textcoords="offset points",
                                     xytext=(0, -12), ha='center', fontsize=7, color='green')
                for idx, val in zip(max_5_idxs, max_5_vals):
                    ax_left.annotate(f'{val:.1f}', (idx, val), textcoords="offset points",
                                     xytext=(0, 8), ha='center', fontsize=7, color='red')

                ax_left.set_title(f'{var} - ORIGINAL', fontweight='bold')
                ax_left.set_xlabel('Index (jours)')
                ax_left.set_ylabel('Valeur')
                ax_left.grid(True, alpha=0.3)

            # ========== VARIABLE FILTRÉE (colonne de droite) ==========
            ax_right = axes[i, 1]
            filt_col = f"{var}_FILTER"
            if filt_col in df_filtered.columns:
                clean_filt = df_filtered[filt_col].dropna()

                # رسم الإشارة
                ax_right.plot(clean_filt.index, clean_filt.values, 'r-', alpha=0.7, linewidth=1)

                # إيجاد القمم والقيعان
                min_5_idxs = clean_filt.nsmallest(5).index
                min_5_vals = clean_filt.nsmallest(5).values
                max_5_idxs = clean_filt.nlargest(5).index
                max_5_vals = clean_filt.nlargest(5).values

                # رسم القيعان (أخضر)
                ax_right.scatter(min_5_idxs, min_5_vals, color='green', s=80,
                                 marker='v', zorder=5, edgecolors='black', linewidth=1)
                # رسم القمم (أحمر)
                ax_right.scatter(max_5_idxs, max_5_vals, color='red', s=80,
                                 marker='^', zorder=5, edgecolors='black', linewidth=1)

                # إضافة تسميات
                for idx, val in zip(min_5_idxs, min_5_vals):
                    ax_right.annotate(f'{val:.1f}', (idx, val), textcoords="offset points",
                                      xytext=(0, -12), ha='center', fontsize=7, color='green')
                for idx, val in zip(max_5_idxs, max_5_vals):
                    ax_right.annotate(f'{val:.1f}', (idx, val), textcoords="offset points",
                                      xytext=(0, 8), ha='center', fontsize=7, color='red')

                ax_right.set_title(f'{var} - FILTRÉ (Wavelet)', fontweight='bold')
                ax_right.set_xlabel('Index (jours)')
                ax_right.set_ylabel('Valeur')
                ax_right.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✅ Graphique sauvegardé: {save_path}")
        return fig


class Visualizer:
    """Classe pour la visualisation"""

    @staticmethod
    def plot_filtering_comparison(df_original, df_filtered, save_path="1_comparaison_filtrage.png"):
        """Génère les graphiques de comparaison"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Comparaison Signal Original vs Filtré (avec padding)",
                     fontsize=14, fontweight='bold')

        # AL2SO4 complet
        ax1 = axes[0, 0]
        ax1.plot(df_original['AL2SO4'].values, 'b-', alpha=0.5, label='Original', linewidth=0.8)
        ax1.plot(df_filtered['AL2SO4_FILTER'].values, 'r-', label='Filtré', linewidth=1.5)
        ax1.set_title("AL2SO4 - Original vs Filtré")
        ax1.set_xlabel("Temps (jours)")
        ax1.set_ylabel("mg/L")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Zoom début
        ax2 = axes[0, 1]
        zoom = 50
        ax2.plot(df_original['AL2SO4'].values[:zoom], 'b-o', alpha=0.5, label='Original', markersize=3)
        ax2.plot(df_filtered['AL2SO4_FILTER'].values[:zoom], 'r-s', label='Filtré', markersize=3)
        ax2.set_title(f"Zoom sur les {zoom} premières observations")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Zoom fin
        ax3 = axes[1, 0]
        zoom_end = 50
        ax3.plot(df_original['AL2SO4'].values[-zoom_end:], 'b-o', alpha=0.5, label='Original', markersize=3)
        ax3.plot(df_filtered['AL2SO4_FILTER'].values[-zoom_end:], 'r-s', label='Filtré', markersize=3)
        ax3.set_title(f"Zoom sur les {zoom_end} dernières observations")
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Résidus
        ax4 = axes[1, 1]
        diff = df_original['AL2SO4'].values - df_filtered['AL2SO4_FILTER'].values
        ax4.hist(diff, bins=30, color='purple', alpha=0.7, edgecolor='black')
        ax4.axvline(0, color='red', linestyle='--', linewidth=2)
        ax4.set_title(f"Résidus\nμ={diff.mean():.4f}, σ={diff.std():.4f}")
        ax4.set_xlabel("Différence (mg/L)")
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✅ Graphique sauvegardé: {save_path}")


# =====================================================
# EXÉCUTION PRINCIPALE
# =====================================================
if __name__ == "__main__":
    print("=" * 70)
    print(" ÉTAPE 1 : CHARGEMENT ET FILTRAGE DES DONNÉES AVEC PADDING ")
    print("=" * 70)

    # Chargement
    loader = DataLoader("SIDI KHELIFA DATA-2018-2019.xlsx")
    df = loader.load()

    # Filtrage
    filter_wavelet = WaveletFilter()
    df_clean = filter_wavelet.fit_transform(df)

    # =====================================================
    # تحليل القمم (5 MIN et 5 MAX) - ملف واحد فقط
    # =====================================================

    variables = ['TUR', 'TE', 'pH', 'SC', 'DO', 'AL2SO4']

    # استخراج جميع القمم في ملف Excel واحد
    analyzer = PeakAnalyzer()
    df_peaks, df_stats = analyzer.extract_all_peaks(
        df, df_clean, variables,
        save_path="1_tous_les_pics_5min_5max.xlsx"
    )

    # رسم جميع المتغيرات في ملف واحد
    analyzer.plot_all_peaks(
        df, df_clean, variables,
        save_path="1_tous_les_graphes_pics.png"
    )

    # Sauvegarde
    df_clean.to_excel("dataset_filtre_final_optimise.xlsx", index=False)
    print("\n" + "=" * 70)
    print("✅ Sauvegardé: dataset_filtre_final_optimise.xlsx")
    print(f"📊 Shape: {df_clean.shape}")
    print("=" * 70)

    # Visualisation de comparaison
    Visualizer.plot_filtering_comparison(df, df_clean)

    print("\n" + "=" * 70)
    print("✅ تحليل القمم مكتمل!")
    print("📁 الملفات الناتجة:")
    print("   📄 1_tous_les_pics_5min_5max.xlsx (جميع القمم لجميع المتغيرات)")
    print("      ├── Feuille 'Tous_les_pics' (5 MIN/5 MAX)")
    print("      └── Feuille 'Statistiques' (إحصائيات تفصيلية)")
    print("   📊 1_tous_les_graphes_pics.png (رسومات جميع المتغيرات)")
    print("   📊 1_comparaison_filtrage.png (مقارنة AL2SO4 قبل/بعد)")
    print("=" * 70)