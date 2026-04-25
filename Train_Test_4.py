from Time_Lag_3 import df_final
# ==========================================
# ÉTAPE 4 : TRAIN / TEST SPLIT (TIME SERIES)
# ==========================================

print("\n" + "="*60)
print(" TRAIN / TEST SPLIT ")
print("="*60)

# ------------------------------------------
# 1. ترتيب البيانات حسب التاريخ (مهم جداً)
# ------------------------------------------
df_final = df_final.sort_values(by='DATE')

# ------------------------------------------
# 2. تحديد نسبة التقسيم
# ------------------------------------------
split_ratio = 0.7   # 70% train / 30% test
split_index = int(len(df_final) * split_ratio)

# ------------------------------------------
# 3. تقسيم البيانات
# ------------------------------------------
train = df_final.iloc[:split_index]
test  = df_final.iloc[split_index:]

# ------------------------------------------
# 4. فصل X و y
# ------------------------------------------
X_train = train.drop(columns=['AL2SO4_FILTER', 'DATE'])
y_train = train['AL2SO4_FILTER']
X_test = test.drop(columns=['AL2SO4_FILTER', 'DATE'])
y_test = test['AL2SO4_FILTER']

# ------------------------------------------
# 5. عرض النتائج
# ------------------------------------------
print("\n📊 Train size :", X_train.shape)
print("📊 Test size  :", X_test.shape)
print("\n📅 Train period :")
print(train['DATE'].min(), "→", train['DATE'].max())
print("\n📅 Test period :")
print(test['DATE'].min(), "→", test['DATE'].max())