# Last.fm Churn Prediction & Targeting

Predicting which Last.fm users are about to disengage from the platform, then turning those predictions into a ranked targeting decision and a designed experiment to validate intervention.

**The deliverable isn't a model — it's a decision:** of the users most likely to churn, which are actually worth contacting, and how would we prove a retention nudge works?

## What this project does

1. **Collects its own data** from the Last.fm API — no pre-made dataset.
2. **Defines churn from raw behavior** — no "churned" label exists; it's derived from listening activity.
3. **Predicts churn** with a leakage-safe logistic regression (AUC 0.82).
4. **Translates predictions into targeting economics** — ranks users by the expected value of contacting them.
5. **Designs the validating experiment** — power analysis for a retention A/B test.

## Approach

### Defining churn
Last.fm has no churn label, so I defined it: a user is **churned** if they have no scrobbles (plays) in the 45 days before today. This measures disengagement from Last.fm the platform — not music listening in general, which the data can only proxy (a user could quit Last.fm while still listening on Spotify).

### Collecting the sample
Real usernames were gathered by snowballing through the `user.getFriends` endpoint from seed accounts, producing ~900 users. Each user's listening history (up to 2,000 recent scrobbles) was pulled live via the API.

### Features (leakage-safe)
Churn is defined by recency, so recency cannot be a feature — that would leak the answer. All features are computed **only from behavior before the 45-day label window**: listening volume, artist variety, consistency of listening gaps, and activity trend (rising vs declining).

### Model
Logistic regression with balanced class weights (the sample is imbalanced). **AUC 0.82** — high enough to be useful, not so high as to indicate leakage (a near-1.0 AUC would signal the label had leaked into the features).

### Targeting economics
A churn probability isn't a decision. For each user:

    expected value = (churn probability × customer value × save rate) − contact cost

Only users with positive expected value are targeted. The **18% save rate** is a benchmark from a real telecom win-back campaign I ran. Output: a ranked list of users to contact, with expected return.

### Experiment design
To validate a retention nudge, I designed an A/B test and ran the power analysis: detecting an 18% relative reduction in churn (80% → 65.6%) at 80% power and 5% significance requires ~148 users per arm (~295 total). With 785 targetable users, the experiment is **adequately powered** — though in a production setting with a realistic (lower) baseline churn rate, the targetable pool would shrink and sample size would need re-checking.

## Key limitations (honest notes)

- **Sampling bias:** users were snowballed from a long-tenured seed account, over-representing early adopters who have mostly churned. This inflates the churn rate (~80%) well above what a random Last.fm sample would show. The project predicts churn *within this biased sample*, not Last.fm's true churn rate.
- **Churn is a proxy:** Last.fm silence may mean a user disconnected scrobbling while still listening elsewhere — so this measures platform disengagement, not listening cessation.
- **Business constants are illustrative:** customer value and contact cost are placeholder inputs; the expected-value *framework* is the contribution, not the specific dollar figures.
- **Small sample:** a few hundred modeled users limits model stability; more data would tighten estimates.

## Stack
Python · Last.fm API · pandas · scikit-learn · statsmodels

## Files
- `build_roster.py` — collect usernames via the API
- `build_dataset.py` — pull histories, define churn, build features
- `model.py` — train and evaluate the churn model
- `targeting.py` — expected-value targeting
- `experiment.py` — A/B test power analysis