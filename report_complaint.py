import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
from utils import save_to_sheet, get_data_from_sheet, shorten_coords
from dotenv import load_dotenv
from datetime import timedelta


load_dotenv()


st.sidebar.title("Pages")

with st.sidebar:
    page = option_menu(
        "Pages",
        ["Report Problem", "View Problems"],
        icons=["exclamation-circle", "eye"],
        menu_icon="list",
        default_index=0,
    )

if page == "Report Problem":
    st.subheader("Report a problem in Yonsei University")
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
                # Prepare values to save
                values = [
                    str(author),
                    str(problem),
                    str(description),
                    str(date),
                    str(time),
                    str(st.session_state.marker_location)
                ]
                result = save_to_sheet(values)
                if result:
                    st.toast("Form submitted and saved to Google Sheet!", icon="✅")
                    st.session_state.data_updated = True
                else:
                    st.toast("Failed to save to Google Sheet.", icon="❌")
            else:
                st.toast("Please input all necessary infos.", icon="⁉️")
    
    
    # Create the base map
    st.markdown("### Click in the map to choose location", unsafe_allow_html=True)
    m = folium.Map(location=CENTER_START, zoom_start=16)
    st.write("<style>iframe[title='streamlit_folium.st_folium'] { height: 600px;}</style>", unsafe_allow_html=True)
    # Render the map and capture clicks
    fmap = st_folium(m, center=st.session_state["marker_location"], zoom=st.session_state["zoom"], feature_group_to_add=fg, width=620, height=600, key="folium_map", on_change=update)
    st.write(f"Coordinates: {st.session_state.marker_location}")
    st.markdown("---")
    author = st.text_input("Your name:*", placeholder="John Doe")
    problem = st.text_input("Problem title:*", placeholder="Problem")
    description = st.text_area("Problem description:*", placeholder="Write as detailed as possible...")
    date = st.date_input("Date:*")
    time = st.time_input("Time:*", step=60)
    submit_btn = st.button("submit", on_click=submit)



elif page == "View Problems":
    if st.session_state.get("last_page") != "View Problems" or st.session_state.get("data_updated", False):
        st.session_state.view_data = get_data_from_sheet()
        st.session_state.last_page = "View Problems"
        st.session_state.data_updated = False  # Reset the flag after updating

    data = st.session_state.get("view_data", [])

    if data:
        st.write("## Reported Problems")
        columns = ["Author", "Problem Title", "Description", "Date", "Time", "Location"]
        df = pd.DataFrame(data, columns=columns)
        if not df.empty and "Location" in df.columns:
            df["Full_Location"] = df["Location"]
            df["Location"] = df["Location"].apply(shorten_coords)
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.write("### Map of Reported Problems")

        CENTER_START = [37.56325563600076, 126.93753719329834]
        m = folium.Map(location=CENTER_START, zoom_start=16)
        fg = folium.FeatureGroup(name="Marker")

        for row in data:
            lat, lng = row[-1].strip("[]").split(", ")
            lat, lng = float(lat), float(lng)
            fg.add_child(
                folium.Marker(
                    location=[lat, lng],
                    draggable=False,
                    popup=row[1],
                    tooltip=row[1],
                    icon=folium.Icon(icon="exclamation", prefix='fa', color='red', icon_color='white')
                )
            )
        st_folium(m, width=620, height=600, feature_group_to_add=fg, key="folium_map_view")
    else:
        st.write("No problems reported yet.")
    

    #A new map with a slider that will show the problems based on the date
    df["Date"] = pd.to_datetime(df["Date"])

    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()
    if min_date == max_date:
        max_date += timedelta(days=1)
    selected_date = st.slider(
        "Select a date to view problems:",
        min_value=min_date,
        max_value=max_date,
        value=min_date,
        format="YYYY-MM-DD"
)

    filtered_df = df[df["Date"].dt.date == selected_date]

    CENTER_START = [37.56325563600076, 126.93753719329834]
    m_filtered = folium.Map(location=CENTER_START, zoom_start=16)
    fg_filtered = folium.FeatureGroup(name="Filtered Markers")

    if filtered_df.empty:
        st.write("✅ There are no problems reported on this date!")
    else:
        for _, row in filtered_df.iterrows():
            lat, lng = row["Full_Location"].strip("[]").split(", ")
            lat, lng = float(lat), float(lng)
            fg_filtered.add_child(
                folium.Marker(
                    location=[lat, lng],
                    draggable=False,
                    popup=row["Problem Title"],
                    tooltip=row["Problem Title"],
                    icon=folium.Icon(icon="exclamation", prefix='fa', color='red', icon_color='white')
                )
            )

        st.markdown("### Map of Problems Reported on Selected Date")
        st_folium(m_filtered, width=620, height=600, feature_group_to_add=fg_filtered, key="filtered_map")