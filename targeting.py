import pandas as pd
from sklearn.linear_model import LogisticRegression

df = pd.read_csv("features.csv")

feature_cols = ["scrobbles_per_week", "artist_variety", "avg_gap_days", "gap_std", "trend"]
X = df[feature_cols]
y = df["churned"]

model = LogisticRegression(class_weight="balanced", max_iter=1000)
model.fit(X, y)

df["churn_prob"] = model.predict_proba(X)[:, 1]

SAVE_RATE = 0.18
CONTACT_COST = 1.0
VALUE_PER_SCROBBLE = 0.05

df["customer_value"] = df["scrobbles_per_week"] * VALUE_PER_SCROBBLE * 52
df["expected_value"] = (df["churn_prob"] * df["customer_value"] * SAVE_RATE) - CONTACT_COST

targets = df[df["expected_value"] > 0].sort_values("expected_value", ascending=False)

print(f"Total users: {len(df)}")
print(f"Worth contacting (EV > 0): {len(targets)}")
print(f"Total expected value from campaign: {targets['expected_value'].sum():.2f}")
print()
print("Top 10 users to target:")
print(targets[["username", "churn_prob", "customer_value", "expected_value"]].head(10).to_string(index=False))