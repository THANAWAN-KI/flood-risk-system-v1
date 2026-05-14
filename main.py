import requests
import json
import pandas as pd
from datetime import datetime

# =========================
# CONFIG
# =========================
API_KEY = "2YWjjlLEyufi1gjMcWRAVomEcccN94OhcySD9CUJo70DI9h6AC1YmawShmzHRQ18"

# จุดตัวอย่าง (เปลี่ยนเป็นพื้นที่คุณได้)
points = [
    (14.1234, 101.5678),
    (14.1100, 101.5200),
    (14.2000, 101.6000)
]


# =========================
# CALL API
# =========================
def get_flood_risk(lat, lon):
    url = (
        "https://api-gateway.gistda.or.th/api/2.0/resources/gi-service/v1.0/"
        f"disasters/flood-recurrence?lat={lat}&lon={lon}&api_key={API_KEY}"
    )

    res = requests.get(url, timeout=30)

    if res.status_code != 200:
        print("API Error:", res.status_code)
        return None

    return res.json()


# =========================
# PROCESS DATA
# =========================
results = []

for lat, lon in points:
    print(f"Processing {lat}, {lon}")

    data = get_flood_risk(lat, lon)

    if data:
        results.append({
            "lat": lat,
            "lon": lon,
            "risk_level": data.get("risk_level"),
            "risk_score": data.get("risk_score"),
            "flood_probability": data.get("flood_probability"),
            "return_period": data.get("return_period"),
            "timestamp": datetime.now().isoformat()
        })


# =========================
# SAVE CSV
# =========================
df = pd.DataFrame(results)
df.to_csv("flood_risk.csv", index=False)


# =========================
# SAVE GEOJSON (ใช้ ArcGIS)
# =========================
geojson = {
    "type": "FeatureCollection",
    "features": []
}

for r in results:
    geojson["features"].append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [r["lon"], r["lat"]]
        },
        "properties": r
    })

with open("flood_risk.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson, f, indent=2, ensure_ascii=False)

print("DONE ✔️")
