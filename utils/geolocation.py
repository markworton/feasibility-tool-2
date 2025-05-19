import requests

def get_coordinates(postcode):
    url = f"https://api.postcodes.io/postcodes/{postcode}"
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()["result"]
        return result["latitude"], result["longitude"]
    else:
        raise ValueError("Invalid postcode or Postcodes.io API error.")
