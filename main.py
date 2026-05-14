import requests
import json
import pandas as pd
from datetime import datetime

# =========================
# CONFIG
# =========================
API_KEY = "PUT_YOUR_API_KEY_HERE"

# จุดตัวอย่าง (ใช้พื้นที่น้ำท่วมมีโอกาสมี data)
points = [
    (13.7563, 100.5018),  # Bangkok
    (13.7450, 100.5340),
    (14.0208, 100.5250),  # Pathum Thani
    (14.3470, 100.5689)   # Ayutthaya
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

    # 🔥 DEBUG สำคัญ
    print("===================================")
    print(f"LAT: {lat}, LON: {lon}")
    print("STATUS:", res.status_code)
    print("RAW RESPONSE:")
    print(res.text)
    print("===================================")

    if res.status_code != 200:
        return None

    try:
        return res.json()
    except Exception as e:
        print("JSON ERROR:", e)
        return None


# =========================
# PROCESS DATA
# =========================
results = []

for lat, lon in points:
    data = get_flood_risk(lat, lon)

    if not data:
        print("NO DATA SKIP")
        continue

    # 🔥 รองรับ JSON หลายรูปแบบ
    if isinstance(data, dict):
        risk_level = data.get("risk_level") or data.get("data", {}).get("risk_level")
        risk_score = data.get("risk_score") or data.get("data", {}).get("risk_score")
        flood_probability = data.get("flood_probability") or data.get("data", {}).get("flood_probability")
        return_period = data.get("return_period") or data.get("data", {}).get("return_period")
    else:
        continue

    # ❗ ถ้าไม่มี risk_level = ข้าม
    if not risk_level:
        print("NO RISK DATA FOUND")
        continue

    results.append({
        "lat": lat,
        "lon": lon,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "flood_probability": flood_probability,
        "return_period": return_period,
        "timestamp": datetime.now().isoformat()
    })


# =========================
# SAVE CSV
# =========================
df = pd.DataFrame(results)
df.to_csv("flood_risk.csv", index=False)


# =========================
# SAVE GEOJSON (ArcGIS READY)
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

print("DONE ✔️ Results count:", len(results))
