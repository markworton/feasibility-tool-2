import requests
from config import RENEWABLES_NINJA_API_KEY

def get_ninja_data(lat, lon, tech="solar", year=2021):
    base_url = f"https://www.renewables.ninja/api/data/{tech}"
    headers = {"Authorization": f"Token {RENEWABLES_NINJA_API_KEY}"}
    model = "pv" if tech == "solar" else "merra2"
    params = {
        "lat": lat,
        "lon": lon,
        "date_from": f"{year}-01-01",
        "date_to": f"{year}-12-31",
        "format": "json",
        "header": True,
        "tz": "Europe/London",
        "capacity": 1,
        "system_loss": 0.1,
        "model": model
    }
    if tech == "wind":
        params["height"] = 100
    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")
