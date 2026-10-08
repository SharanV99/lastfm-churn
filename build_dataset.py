import os
import requests
import time
import datetime
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("LASTFM_API_KEY")

url = "http://ws.audioscrobbler.com/2.0/"


def get_user_scrobbles(username, max_pages=10):
    timestamps = []

    for page in range(1, max_pages + 1):
        params = {
            "method": "user.getRecentTracks",
            "user": username,
            "api_key": api_key,
            "format": "json",
            "limit": 200,
            "page": page
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()
        except Exception:
            break

        if "recenttracks" not in data:
            break

        tracks = data["recenttracks"]["track"]
        for track in tracks:
            if "date" in track:
                timestamps.append(int(track["date"]["uts"]))

        time.sleep(0.25)

    return timestamps


def label_user(timestamps, churn_days=45):
    if len(timestamps) < 50:
        return None

    now = int(datetime.datetime.now().timestamp())
    cutoff = now - (churn_days * 24 * 60 * 60)

    most_recent = max(timestamps)
    oldest = min(timestamps)

    before = [t for t in timestamps if t <= cutoff]

    if len(before) < 20:
        return None

    churned = 1 if most_recent < cutoff else 0

    return {
        "scrobble_count": len(timestamps),
        "span_days": round((most_recent - oldest) / 86400),
        "days_since_last": round((now - most_recent) / 86400),
        "churned": churned
    }


roster = pd.read_csv("roster.csv")["username"].tolist()

results = []
for i, username in enumerate(roster):
    scrobbles = get_user_scrobbles(username)
    label = label_user(scrobbles)

    if label is not None:
        label["username"] = username
        results.append(label)

    if (i + 1) % 25 == 0:
        print(f"Processed {i + 1}/{len(roster)} users, kept {len(results)} so far")

df = pd.DataFrame(results)
df.to_csv("churn_dataset.csv", index=False)

print(f"\nDone. Saved {len(df)} users to churn_dataset.csv")
print(f"Churn rate: {df['churned'].mean():.1%}")