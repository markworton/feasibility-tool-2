import requests
from config import RENEWABLES_NINJA_API_KEY

def get_ninja_data(lat, lon, tech="solar", year=2021):
    """
    Fetch solar or wind data from Renewables.ninja API.
    """
    base_url = f"https://www.renewables.ninja/api/data/{tech}"
    headers = {
        "Authorization": f"Token {RENEWABLES_NINJA_API_KEY}"
    }

    # Determine model based on technology
    if tech == "solar":
        model = "pv"
    elif tech == "wind":
        model = "merra2"
    else:
        raise ValueError("Unknown technology type. Use 'solar' or 'wind'.")

    # Assemble request parameters
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

    # For wind only: add height
    if tech == "wind":
        params["height"] = 100

    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error {response.status_code}: {response.text}")