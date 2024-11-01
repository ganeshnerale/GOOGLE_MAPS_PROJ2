import streamlit as st
import requests

# Set up your Google API key
API_KEY = "API-KEY"

# Function to get coordinates of an address
def get_coordinates(address):
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}"
    response = requests.get(geocode_url).json()
    
    if response["status"] == "OK":
        location = response["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        st.error("Error fetching coordinates.")
        return None, None

# Function to get nearby hospitals within a certain radius, along with their ratings
def get_nearby_hospitals(lat, lng, radius=5000):  # Radius in meters
    places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type=hospital&key={API_KEY}"
    response = requests.get(places_url).json()
    
    if response["status"] == "OK":
        hospitals = response["results"]
        hospital_info = []
        for hospital in hospitals:
            name = hospital["name"]
            rating = hospital.get("rating", "No rating available")  # Get rating, or default if not available
            hospital_lat = hospital["geometry"]["location"]["lat"]
            hospital_lng = hospital["geometry"]["location"]["lng"]
            hospital_info.append({"name": name, "rating": rating, "lat": hospital_lat, "lng": hospital_lng})
        return hospital_info
    else:
        st.error("Error fetching nearby hospitals.")
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
            distances.append({"hospital_name": destinations[i]["name"], "distance_text": distance_text, "rating": destinations[i]["rating"]})
        return distances
    else:
        st.error("Error fetching distances.")
        return []

# Streamlit app
def main():
    st.title("Nearby Hospitals Finder for Hecta")
    st.write("Enter an address to find nearby hospitals with ratings and distances.")
    
    address = st.text_input("Address")
    if st.button("Find Hospitals"):
        if address:
            lat, lng = get_coordinates(address)
            if lat is not None and lng is not None:
                hospitals = get_nearby_hospitals(lat, lng)
                if hospitals:
                    distances = get_distances((lat, lng), hospitals)
                    for d in distances:
                        st.write(f"**Hospital:** {d['hospital_name']}, **Rating:** {d['rating']}, **Distance:** {d['distance_text']}")
                else:
                    st.write("No hospitals found nearby.")
        else:
            st.write("Please enter a valid address.")

if __name__ == "__main__":
    main()
