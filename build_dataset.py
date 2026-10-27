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
    scrobbles = []

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
                ts = int(track["date"]["uts"])
                artist = track["artist"]["#text"]
                scrobbles.append((ts, artist))

        time.sleep(0.25)

    return scrobbles


def build_features(scrobbles, churn_days=45):
    if len(scrobbles) < 50:
        return None

    now = int(datetime.datetime.now().timestamp())
    cutoff = now - (churn_days * 24 * 60 * 60)

    timestamps = [s[0] for s in scrobbles]
    most_recent = max(timestamps)

    churned = 1 if most_recent < cutoff else 0

    before = [s for s in scrobbles if s[0] <= cutoff]
    if len(before) < 20:
        return None

    before_ts = sorted([s[0] for s in before])
    before_artists = [s[1] for s in before]

    span_days = (before_ts[-1] - before_ts[0]) / 86400
    span_weeks = max(span_days / 7, 1)

    scrobbles_per_week = len(before) / span_weeks
    artist_variety = len(set(before_artists)) / len(before_artists)

    gaps = [before_ts[i+1] - before_ts[i] for i in range(len(before_ts)-1)]
    avg_gap = sum(gaps) / len(gaps) / 86400
    gap_std = (sum((g/86400 - avg_gap)**2 for g in gaps) / len(gaps)) ** 0.5

    midpoint = before_ts[0] + (before_ts[-1] - before_ts[0]) / 2
    first_half = len([t for t in before_ts if t <= midpoint])
    second_half = len([t for t in before_ts if t > midpoint])
    trend = (second_half - first_half) / len(before_ts)

    return {
        "scrobbles_per_week": round(scrobbles_per_week, 2),
        "artist_variety": round(artist_variety, 3),
        "avg_gap_days": round(avg_gap, 2),
        "gap_std": round(gap_std, 2),
        "trend": round(trend, 3),
        "churned": churned
    }


roster = pd.read_csv("roster.csv")["username"].tolist()

results = []
for i, username in enumerate(roster):
    scrobbles = get_user_scrobbles(username)
    features = build_features(scrobbles)

    if features is not None:
        features["username"] = username
        results.append(features)

    if (i + 1) % 25 == 0:
        print(f"Processed {i + 1}/{len(roster)}, kept {len(results)} so far")

df = pd.DataFrame(results)
df.to_csv("features.csv", index=False)

print(f"\nDone. Saved {len(df)} users to features.csv")
print(f"Churn rate: {df['churned'].mean():.1%}")