import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("LASTFM_API_KEY")

url = "http://ws.audioscrobbler.com/2.0/"

seeds = ["rj", "eartle", "massdosage"]
target_count = 900

roster = set()
to_visit = list(seeds)
visited = set()

while len(roster) < target_count and to_visit:
    current = to_visit.pop(0)
    if current in visited:
        continue
    visited.add(current)

    params = {
        "method": "user.getFriends",
        "user": current,
        "api_key": api_key,
        "format": "json",
        "limit": 50
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "friends" not in data:
        continue

    friends = data["friends"]["user"]
    for friend in friends:
        name = friend["name"]
        roster.add(name)
        to_visit.append(name)

    print(f"Visited {current}, roster size now: {len(roster)}")
    time.sleep(0.25)

print(f"Done. Collected {len(roster)} usernames.")

import pandas as pd

df = pd.DataFrame({"username": list(roster)})
df.to_csv("roster.csv", index=False)
print(f"Saved {len(df)} usernames to roster.csv")