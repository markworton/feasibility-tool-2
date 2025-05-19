import requests
from config import RENEWABLES_NINJA_API_KEY

def get_ninja_data(lat, lon, tech="solar", year=2021):
    """
    Fetch solar or wind data from Renewables.ninja API.
    """

    # Set base URL and model
    if tech == "solar":
        base_url = "https://www.renewables.ninja/api/data/pv"
    elif tech == "wind":
        base_url = "https://www.renewables.ninja/api/data/wind"
    else:
        raise ValueError("tech must be either 'solar' or 'wind'")

    headers = {
        "Authorization": f"Token {RENEWABLES_NINJA_API_KEY}"
    }

    params = {
        "lat": lat,
        "lon": lon,
        "date_from": f"{year}-01-01",
        "date_to": f"{year}-12-31",
        "format": "json",
        "header": True,
        "tz": "Europe/London",
        "capacity": 1,
        "system_loss": 0.1
    }

    if tech == "wind":
        params["height"] = 100

    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")
