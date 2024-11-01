import streamlit as st
import pandas as pd
import requests
from io import BytesIO

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
        return None, None

# Function to get nearby hospitals within a certain radius, along with their ratings
def get_nearby_hospitals(lat, lng, radius=5000):  # Radius in meters
    places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type=hospital&key={API_KEY}"
    response = requests.get(places_url).json()
    
    if response["status"] == "OK":
        hospitals = response["results"]
        hospital_info = []
        for hospital in hospitals[:5]:  # Top 5 hospitals
            name = hospital["name"]
            rating = hospital.get("rating", "No rating available")
            hospital_lat = hospital["geometry"]["location"]["lat"]
            hospital_lng = hospital["geometry"]["location"]["lng"]
            hospital_info.append({"name": name, "rating": rating, "lat": hospital_lat, "lng": hospital_lng})
        return hospital_info
    else:
        return []

# Function to process each address and find nearby hospitals
def process_addresses(df):
    results = []
    for _, row in df.iterrows():
        address = row['address']
        lat, lng = get_coordinates(address)
        if lat is not None and lng is not None:
            hospitals = get_nearby_hospitals(lat, lng)
            hospital_names = [f"{h['name']} (Rating: {h['rating']})" for h in hospitals]
            results.append({
                "address": address,
                "latitude": lat,
                "longitude": lng,
                "top_5_hospitals": "; ".join(hospital_names)
            })
        else:
            results.append({
                "address": address,
                "latitude": "N/A",
                "longitude": "N/A",
                "top_5_hospitals": "No hospitals found"
            })
    return pd.DataFrame(results)

# Streamlit app
def main():
    # Custom title box
    st.markdown(
        """
        <div style="
            background-color: #4CAF50;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            color: white;
            font-size: 24px;">
            <b>Nearby Hospitals Finder</b>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Sidebar for About Us
    st.sidebar.title("About Us")
    st.sidebar.write(
        """
        **Nearby Hospitals Finder** is an application designed to help users locate nearby hospitals based on a given address.
        Just upload an Excel file containing addresses, and the app will provide the top 5 hospitals with ratings and distances
        for each location.
        
        This tool leverages Google Maps APIs for accurate data and aims to make finding healthcare facilities quick and easy.
        """
    )
    
    # Main content
    st.write("Upload an Excel file with an 'address' column to find nearby hospitals with ratings and distances.")
    
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        if 'address' not in df.columns:
            st.error("The Excel file must contain an 'address' column.")
        else:
            st.write("Processing addresses...")
            results_df = process_addresses(df)
            
            # Display the results
            st.write(results_df)
            
            # Download the results as an Excel file
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                results_df.to_excel(writer, index=False, sheet_name='Hospitals Nearby')
            processed_file = output.getvalue()
            
            st.download_button(
                label="Download Results",
                data=processed_file,
                file_name="hospitals_nearby.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()
