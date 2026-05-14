import requests
import json
import pandas as pd
from datetime import datetime

API_KEY = "JTGRudfw7zoIvqlJjAm3OKq7mX0lAUk9hHYctgO327sdJ8F7GEUnbokvlCIjDh0U"

points = [
    (13.7563, 100.5018),  # Bangkok
    (14.0208, 100.5250),  # Pathum Thani
    (14.3470, 100.5689)   # Ayutthaya
]


# =========================
# NEW API (Risk-based)
# =========================
def get_flood_risk(lat, lon):

    url = "https://api-gateway.gistda.or.th/api/2.0/resources/gi-service/v1.0/disasters/flood-risk"

    params = {
        "lat": lat,
        "lon": lon,
        "api_key": API_KEY
    }

    res = requests.get(url, params=params, timeout=30)

    print("STATUS:", res.status_code)
    print("RAW:", res.text)

    if res.status_code != 200:
        return None

    try:
        return res.json()
    except:
        return None


results = []

for lat, lon in points:
    data = get_flood_risk(lat, lon)

    if not data:
        continue

    # รองรับหลาย format
    risk_level = (
        data.get("risk_level")
        or data.get("data", {}).get("risk_level")
        or data.get("level")
    )

    risk_score = (
        data.get("risk_score")
        or data.get("data", {}).get("risk_score")
    )

    if not risk_level:
        continue

    results.append({
        "lat": lat,
        "lon": lon,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "timestamp": datetime.now().isoformat()
    })


# =========================
# CSV
# =========================
pd.DataFrame(results).to_csv("flood_risk.csv", index=False)


# =========================
# GEOJSON
# =========================
geojson = {"type": "FeatureCollection", "features": []}

for r in results:
    geojson["features"].append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [r["lon"], r["lat"]]
        },
        "properties": r
    })

with open("flood_risk.geojson", "w") as f:
    json.dump(geojson, f, indent=2)

print("DONE ✔️", len(results))
