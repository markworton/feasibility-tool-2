import requests
from config import RENEWABLES_NINJA_API_KEY

def get_ninja_data(lat, lon, tech="solar", year=2021):
    """
    Fetch solar or wind data from Renewables.ninja API.
    """

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
            "system_loss": 0.1,
            "azim": 180,
            "tilt": 35,
            "tracking": 0
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
            "system_loss": 0.1,
            "height": 100
        }
    else:
        raise ValueError("tech must be 'solar' or 'wind'")

    headers = {
        "Authorization": f"Token {RENEWABLES_NINJA_API_KEY}"
    }

    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")
