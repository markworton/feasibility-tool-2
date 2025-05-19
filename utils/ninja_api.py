import requests
from config import RENEWABLES_NINJA_API_KEY

def get_ninja_data(lat, lon, tech="solar", year=2021):
    headers = {
        "Authorization": f"Token {RENEWABLES_NINJA_API_KEY}"
    }

    if tech == "solar":
        base_url = "https://www.renewables.ninja/api/data/pv"
        params = {
            "lat": lat,
            "lon": lon,
            "date_from": f"{year}-01-01",
            "date_to": f"{year}-12-31",
            "format": "json",
            "header": True,
            "capacity": 1,
            "azim": 180,
            "tilt": 35,
            "tracking": 0,
            "system_loss": 0.1
        }

    elif tech == "wind":
        base_url = "https://www.renewables.ninja/api/data/wind"
        params = {
            "lat": lat,
            "lon": lon,
            "date_from": f"{year}-01-01",
            "date_to": f"{year}-12-31",
            "format": "json",
            "header": True,
            "capacity": 1,
            "height": 100,
            "turbine": "Vestas_V112_3.0MW"
        }

    else:
        raise ValueError("tech must be 'solar' or 'wind'")

    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")
