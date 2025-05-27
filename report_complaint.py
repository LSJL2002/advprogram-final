import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu

st.sidebar.title("Pages")

with st.sidebar:
    page = option_menu(
        "Pages",
        ["Report Problem", "View Problems"],
        icons=["exclmation-circle", "file-earmark"],
        menu_icon="cast",
        default_index=0,
    )

if page == "Report Problem":
    """
    # Report a problem in Yonsei University
    """

    CENTER_START = [37.56325563600076, 126.93753719329834]

    # Initialize session state to store marker location
    if "marker_location" not in st.session_state:
        st.session_state.marker_location = CENTER_START  # Default location set to Yonsei Sinchon Campus
        st.session_state.zoom = 16  # Default zoom



    # Create FeatureGroup for marker
    fg = folium.FeatureGroup(name="Marker")
    # Add marker to the group
    fg.add_child(
        folium.Marker(
        location=st.session_state.marker_location,
        draggable=False,
        popup="Marker title",
        tooltip="Marker hover title",
        icon=folium.Icon(icon="exclamation", prefix='fa', color='red', icon_color='white')
    ))

    # Function to update marker location and zoom values in session_state when map changed
    def update():
        fmap = st.session_state["folium_map"] # Get map from session_state
        if fmap.get("last_clicked"): # If map has last_clicked place
            lat, lng = fmap["last_clicked"]["lat"], fmap["last_clicked"]["lng"]
            st.session_state.marker_location = [lat, lng]  # Update session state with new marker location
            st.session_state.zoom = fmap["zoom"] # Update session state with new zoom value 

    def submit():
        if all([author, problem, description, date, time]):
            st.toast("Form submitted", icon="✅")
            # Other logic here
        else:
            st.toast("Please input all necessary infos.", icon="⁉️")


    # Create the base map
    m = folium.Map(location=CENTER_START, zoom_start=16)
    st.markdown("### Click in the map to choose location", unsafe_allow_html=True)


    # Render the map and capture clicks
    fmap = st_folium(m, center=st.session_state["marker_location"], zoom=st.session_state["zoom"], feature_group_to_add=fg,width=620, height=580, key="folium_map", on_change=update)


    # Write coordinates
    coordtext = f"Coordinates: {st.session_state.marker_location}"
    st.write(coordtext)
    with st.form("my_form", clear_on_submit=False, enter_to_submit=False):
        author = st.text_input("Your name:*", placeholder="John Doe")
        problem = st.text_input("Problem title:*", placeholder="Problem")
        description = st.text_area("Problem description:*", placeholder="Write as detailed as possible...")
        date = st.date_input("Date:*")
        time = st.time_input("Time:*", step=60)
        submit = st.form_submit_button(on_click=submit)

elif page == "Other Page":
    """
    #Testing
    """