import requests

# Set up your API key
API_KEY = "API-KEY"

# Function to get coordinates of an address
def get_coordinates(address):
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}"
    response = requests.get(geocode_url).json()
    
    if response["status"] == "OK":
        location = response["results"][0]["geometry"]["location"]
        print("lat : "+str(location["lat"]))
        print("lng : "+str(location["lng"]))
        return location["lat"], location["lng"]
    else:
        print("Error fetching coordinates.")
        return None, None

# Function to get nearby hospitals within a certain radius
def get_nearby_hospitals(lat, lng, radius=5000):  # Radius in meters
    places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type=hospital&key={API_KEY}"
    response = requests.get(places_url).json()
    
    if response["status"] == "OK":
        hospitals = response["results"]
        hospital_info = []
        for hospital in hospitals:
            name = hospital["name"]
            hospital_lat = hospital["geometry"]["location"]["lat"]
            hospital_lng = hospital["geometry"]["location"]["lng"]
            hospital_info.append({"name": name, "lat": hospital_lat, "lng": hospital_lng})
        return hospital_info
    else:
        print("Error fetching nearby hospitals.")
        return []

# Function to get distance to each hospital
def get_distances(origin, destinations):
    destinations_str = "|".join([f"{h['lat']},{h['lng']}" for h in destinations])
    distance_url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin[0]},{origin[1]}&destinations={destinations_str}&key={API_KEY}"
    response = requests.get(distance_url).json()
    
    if response["status"] == "OK":
        distances = []
        for i, row in enumerate(response["rows"][0]["elements"]):
            distance_text = row["distance"]["text"]
            distance_value = row["distance"]["value"]
            distances.append({"hospital_name": destinations[i]["name"], "distance_text": distance_text, "distance_value": distance_value})
        return distances
    else:
        print("Error fetching distances.")
        return []

# Main function
def find_nearby_hospitals_with_distance(address):
    lat, lng = get_coordinates(address)
    if lat is None or lng is None:
        return "Unable to fetch coordinates."

    hospitals = get_nearby_hospitals(lat, lng)
    if not hospitals:
        return "No hospitals found nearby."

    distances = get_distances((lat, lng), hospitals)
    for d in distances:
        print(f"Hospital: {d['hospital_name']}, Distance: {d['distance_text']}")

# Example usage
#address = "1600 Amphitheatre Parkway, Mountain View, CA"
address = "flat number 803 8th floor Vraj palace building A survey number 58/3, Kangshiyali ,lodhika,near copper residency, rajkot gujrat"
find_nearby_hospitals_with_distance(address)
