import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_RANGE = "Sheet1!A1"


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
                else:
                    st.toast("Failed to save to Google Sheet.", icon="❌")
            else:
                st.toast("Please input all necessary infos.", icon="⁉️")
    def save_to_sheet(values):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        try:
            service = build("sheets", "v4", credentials=creds)
            sheet = service.spreadsheets()
            # Find the next empty row
            result = sheet.values().get(
                spreadsheetId=SPREADSHEET_ID,
                range="Sheet1!A:A"
            ).execute()
            num_rows = len(result.get("values", []))
            next_row = num_rows + 1
            target_range = f"Sheet1!A{next_row}:F{next_row}"
            update_result = sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=target_range,
                valueInputOption="RAW",
                body={"values": [values]},
            ).execute()
            return update_result
        except HttpError as err:
            print(err)
            return None
    
    # Create the base map
    m = folium.Map(location=CENTER_START, zoom_start=16)
    st.markdown("### Click in the map to choose location", unsafe_allow_html=True)
    # Render the map and capture clicks
    fmap = st_folium(m, center=st.session_state["marker_location"], zoom=st.session_state["zoom"], feature_group_to_add=fg,width=620, height=600, key="folium_map", on_change=update)
    st.markdown("<style>div.block-container { padding-top: 1rem; }</style>", unsafe_allow_html=True) #Reduces the space between the map and form
    st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    st.write(f"Coordinates: {st.session_state.marker_location}")
    with st.form("my_form", clear_on_submit=False, enter_to_submit=False):
        author = st.text_input("Your name:*", placeholder="John Doe")
        problem = st.text_input("Problem title:*", placeholder="Problem")
        description = st.text_area("Problem description:*", placeholder="Write as detailed as possible...")
        date = st.date_input("Date:*")
        time = st.time_input("Time:*", step=60)
        submit_btn = st.form_submit_button(on_click=submit)

elif page == "Other Page":
    """
    #Testing
    """