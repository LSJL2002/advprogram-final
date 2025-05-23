import streamlit as st
import folium
from streamlit_folium import st_folium

# Function to get position from click coordinates
def get_pos(lat, lng):
    return lat, lng

# Initialize session state to store marker location
if "marker_location" not in st.session_state:
    st.session_state.marker_location = [37.56325563600076, 126.93753719329834]  # Default location set to Yonsei Sinchon Campus
    st.session_state.zoom = 11  # Default zoom

# Create the base map
m = folium.Map(location=st.session_state.marker_location, zoom_start=st.session_state.zoom)

# Add a marker at the current location in session state
marker = folium.Marker(
    location=st.session_state.marker_location,
    draggable=False
)
marker.add_to(m)

# Render the map and capture clicks
map = st_folium(m, width=620, height=580, key="folium_map")

# Update marker position immediately after each click
if map.get("last_clicked"):
    lat, lng = map["last_clicked"]["lat"], map["last_clicked"]["lng"]
    st.session_state.marker_location = [lat, lng]  # Update session state with new marker location
    st.session_state.zoom = map["zoom"]
    # Redraw the map immediately with the new marker location
    m = folium.Map(location=st.session_state.marker_location, zoom_start=st.session_state.zoom)
    folium.Marker(
        location=st.session_state.marker_location,
        draggable=False
    ).add_to(m)
    map = st_folium(m, width=620, height=580, key="folium_map")

# Display coordinates
st.write(f"Coordinates: {st.session_state.marker_location}")