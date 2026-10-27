import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression

df = pd.read_csv("features.csv")
feature_cols = ["scrobbles_per_week", "artist_variety", "avg_gap_days", "gap_std", "trend"]

X = df[feature_cols]
y = df["churned"]
model = LogisticRegression(class_weight="balanced", max_iter=1000)
model.fit(X, y)
df["churn_prob"] = model.predict_proba(X)[:, 1]

SAVE_RATE = 0.18
CONTACT_COST = 20.0
VALUE_PER_SCROBBLE = 0.05
df["customer_value"] = df["scrobbles_per_week"] * VALUE_PER_SCROBBLE * 52
df["expected_value"] = (df["churn_prob"] * df["customer_value"] * SAVE_RATE) - CONTACT_COST


# Chart 1: Targeting scatter
fig, ax = plt.subplots(figsize=(8, 6))
worth = df[df["expected_value"] > 0]
not_worth = df[df["expected_value"] <= 0]
ax.scatter(not_worth["churn_prob"], not_worth["customer_value"],
           alpha=0.4, color="#bbbbbb", label="Not worth contacting", s=20)
ax.scatter(worth["churn_prob"], worth["customer_value"],
           alpha=0.6, color="#d8593c", label="Worth contacting", s=20)
ax.set_xlabel("Churn probability")
ax.set_ylabel("Customer value (£/year)")
ax.set_title("Targeting: who's worth a retention nudge")
ax.legend()
plt.tight_layout()
plt.savefig("charts/targeting.png", dpi=120)
plt.close()


# Chart 2: Feature importance
fig, ax = plt.subplots(figsize=(8, 5))
coefs = pd.Series(model.coef_[0], index=feature_cols).sort_values()
colors = ["#1d9e75" if c < 0 else "#d8593c" for c in coefs]
ax.barh(coefs.index, coefs.values, color=colors)
ax.set_xlabel("Coefficient (→ more churn)")
ax.set_title("What predicts churn")
ax.axvline(0, color="black", linewidth=0.5)
plt.tight_layout()
plt.savefig("charts/features.png", dpi=120)
plt.close()


# Chart 3: Churn rate by activity trend
fig, ax = plt.subplots(figsize=(8, 5))
df["trend_bucket"] = pd.cut(df["trend"], bins=[-1, -0.1, 0.1, 1],
                             labels=["Declining", "Steady", "Rising"])
churn_by_trend = df.groupby("trend_bucket")["churned"].mean()
ax.bar(churn_by_trend.index, churn_by_trend.values, color="#d8593c")
ax.set_ylabel("Churn rate")
ax.set_title("Churn rate by listening trend")
plt.tight_layout()
plt.savefig("charts/trend.png", dpi=120)
plt.close()

print("Saved 3 charts to charts/")