import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, classification_report

df = pd.read_csv("features.csv")

feature_cols = ["scrobbles_per_week", "artist_variety", "avg_gap_days", "gap_std", "trend"]
X = df[feature_cols]
y = df["churned"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

model = LogisticRegression(class_weight="balanced", max_iter=1000)
model.fit(X_train, y_train)

probs = model.predict_proba(X_test)[:, 1]
preds = model.predict(X_test)

print(f"Test AUC: {roc_auc_score(y_test, probs):.3f}")
print()
print(classification_report(y_test, preds, target_names=["retained", "churned"]))