from Train_Test_4 import y_test, X_test, X_train, y_train
# ==========================================
# ÉTAPE 5 : TRAINING MODEL (RANDOM FOREST)
# ==========================================

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

print("\n" + "="*60)
print(" TRAINING MODEL - RANDOM FOREST ")
print("="*60)

# ------------------------------------------
# 1. استيراد البيانات من étape 4
# ------------------------------------------
# X_train, X_test, y_train, y_test يجب أن تكون جاهزة

# ------------------------------------------
# 2. إنشاء النموذج
# ------------------------------------------
model = RandomForestRegressor(
    n_estimators=100,   # عدد الأشجار
    max_depth=10,       # عمق الشجرة
    random_state=42
)

# ------------------------------------------
# 3. تدريب النموذج
# ------------------------------------------
model.fit(X_train, y_train)

print("✅ Model trained successfully")

# ------------------------------------------
# 4. التنبؤ (Prediction)
# ------------------------------------------
y_pred = model.predict(X_test)

# ------------------------------------------
# 5. تقييم النموذج
# ------------------------------------------

# R² (جودة النموذج)
r2 = r2_score(y_test, y_pred)

# RMSE (الخطأ)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

# MAE (متوسط الخطأ)
mae = mean_absolute_error(y_test, y_pred)

print("\n📊 PERFORMANCE:")
print(f"R²   = {r2:.3f}")
print(f"RMSE = {rmse:.3f}")
print(f"MAE  = {mae:.3f}")

# ------------------------------------------
# 6. مقارنة القيم الحقيقية والمتوقعة
# ------------------------------------------
import pandas as pd

df_result = pd.DataFrame({
    'Real': y_test.values,
    'Predicted': y_pred,
    'Error': y_test.values - y_pred
})

print("\n📌 Exemple de résultats :")
print(df_result.head())

# ------------------------------------------
# 7. رسم النتائج
# ------------------------------------------
import matplotlib.pyplot as plt

plt.figure(figsize=(10,5))

plt.plot(y_test.values, label='Réel')
plt.plot(y_pred, label='Prédit')

plt.title("Comparaison Réel vs Prédit")
plt.legend()
plt.grid(True)

plt.show()