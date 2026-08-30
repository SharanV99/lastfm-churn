import os
import requests
import time
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("LASTFM_API_KEY")

url = "http://ws.audioscrobbler.com/2.0/"

params = {
    "method": "user.getRecentTracks",
    "user": "rj",
    "api_key": api_key,
    "format": "json",
    "limit": 5
}

all_rows = []

for page in range(1, 6):
    params["page"] = page
    response = requests.get(url, params=params)
    data = response.json()

    tracks = data["recenttracks"]["track"]
    for track in tracks:
        artist = track["artist"]["#text"]
        name = track["name"]
        uts = track["date"]["uts"]
        all_rows.append({"artist": artist, "track": name, "timestamp": uts})

    print(f"Fetched page {page}, rows so far: {len(all_rows)}")
    time.sleep(0.25)

print(f"Done. Collected {len(all_rows)} rows total.")

df = pd.DataFrame(all_rows)
df.to_csv("scrobbles.csv", index=False)