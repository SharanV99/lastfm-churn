import os
import requests
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

response = requests.get(url, params=params)
data = response.json()

print(response.status_code)
print(data)