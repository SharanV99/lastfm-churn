from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

baseline_churn = 0.80
save_rate = 0.18
treated_churn = baseline_churn * (1 - save_rate)

print(f"Baseline churn (control): {baseline_churn:.1%}")
print(f"Expected churn (treated):  {treated_churn:.1%}")
print()

effect = proportion_effectsize(baseline_churn, treated_churn)

analysis = NormalIndPower()
n_needed = analysis.solve_power(
    effect_size=effect,
    alpha=0.05,
    power=0.80,
    ratio=1.0
)

print(f"Users needed PER GROUP: {n_needed:.0f}")
print(f"Total users needed: {n_needed*2:.0f}")