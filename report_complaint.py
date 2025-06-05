import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
from utils import save_to_sheet, get_data_from_sheet
from dotenv import load_dotenv #Do not delete this, I need it for the .env to work
from datetime import timedelta
import plotly.express as px
from complaint import Complaint



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
        if complaint.is_valid():
            # Prepare values to save
            values = [
                str(complaint.author),
                str(complaint.problem),
                str(complaint.description),
                str(complaint.date),
                str(complaint.time),
                str(complaint.location)
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
    complaint = Complaint()
    complaint.author = st.text_input("Your name:*", placeholder="John Doe")
    complaint.problem = st.text_input("Problem title:*", placeholder="Problem")
    complaint.description = st.text_area("Problem description:*", placeholder="Write as detailed as possible...")
    complaint.date = st.date_input("Date:*")
    complaint.time = st.time_input("Time:*", step=60)
    complaint.location = st.session_state.marker_location  # Use the marker location from session state
    submit_btn = st.button("submit", on_click=submit)



elif page == "View Problems":
    if st.session_state.get("last_page") != "View Problems" or st.session_state.get("data_updated", False):
        st.session_state.view_data = get_data_from_sheet()
        st.session_state.last_page = "View Problems"
        st.session_state.data_updated = False  # Reset the flag after updating

    data = st.session_state.get("view_data", [])

    if data:
        st.write("## Reported Problems")
        columns = ["Author", "Problem Title", "Description", "Date", "Time", "Location", "Status"]
        df = pd.DataFrame(data, columns=columns)
        

        # --- Author filter ---
        unique_authors = df["Author"].dropna().unique().tolist()
        unique_authors.sort()
        author_filter = st.selectbox("Filter by Author", options=["All"] + unique_authors, index=0)
        status_filter = st.selectbox("Filter by Status", options=["All", "Pending", "In Progress", "Resolved", "Closed"], index=0)
        
        if author_filter != "All":
            df = df[df["Author"] == author_filter]
        if status_filter != "All":
            df = df[df["Status"] == status_filter]

        # --- Status color styling (text color only) ---
        def color_status_text(col):
            color_map = {
                "Pending": "color: #f7b731; font-weight: bold;",
                "In Progress": "color: #3867d6; font-weight: bold;",
                "Resolved": "color: #20bf6b; font-weight: bold;",
                "Closed": "color: #a5b1c2; font-weight: bold;"
            }
            return [color_map.get(v, "") for v in col]

        styled_df = df.style.apply(color_status_text, subset=["Status"])
        st.dataframe(styled_df, use_container_width=True, column_order=["Status","Author", "Problem Title", "Description", "Date", "Time", "Location"])

        st.markdown("---")
        st.write("### Map of Reported Problems")

        CENTER_START = [37.56325563600076, 126.93753719329834]
        m = folium.Map(location=CENTER_START, zoom_start=16)
        fg = folium.FeatureGroup(name="Marker")

        for row in df.itertuples(index=False):
            lat, lng = str(row.Location).strip("[]").split(", ")
            lat, lng = float(lat), float(lng)
            fg.add_child(
                folium.Marker(
                    location=[lat, lng],
                    draggable=False,
                    popup=str(row._1),
                    tooltip=str(row._1),
                    icon=folium.Icon(icon="exclamation", prefix='fa', color='red', icon_color='white')
                )
            )
        st_folium(m, width=620, height=600, feature_group_to_add=fg, key="folium_map_view")
    else:
        st.write("No problems reported yet.")
    

    #A new map with a slider that will show the problems based on the date
    df["Date"] = pd.to_datetime(df["Date"])

    min_date = df["Date"].min().date() #Gets the min date of the google sheets
    max_date = df["Date"].max().date() #Max date of the google sheets
    if min_date == max_date: #There is a bug if the min date and max date is the same the slider will not work.
        max_date += timedelta(days=1)
    
    show_all = st.checkbox("Show all dates", value=False)

    if show_all:
        filtered_df = df.copy()
        selected_date = None
    else:
        selected_date = st.date_input(
            "Select a date to view problems:",
            min_value=min_date,
            max_value=max_date,
            value=min_date,
            format="YYYY-MM-DD"
    )
        filtered_df = df[df["Date"].dt.date == selected_date].copy()

    CENTER_START = [37.56325563600076, 126.93753719329834]
    m_filtered = folium.Map(location=CENTER_START, zoom_start=16)
    fg_filtered = folium.FeatureGroup(name="Filtered Markers")

    if filtered_df.empty:
        st.write("✅ There are no problems reported on this date!")
    else:
        st.write(f"**Total number of problems reported on {selected_date}: {len(filtered_df)}**")
        for _, row in filtered_df.iterrows():
            lat, lng = row["Location"].strip("[]").split(", ")
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

    if not filtered_df.empty:
        # Ensure Time is datetime.time
        filtered_df["Time"] = pd.to_datetime(filtered_df["Time"], format="%H:%M:%S").dt.time
        filtered_df["Hour"] = filtered_df["Time"].apply(lambda t: t.hour)

        # Group by Hour
        grouped = filtered_df.groupby("Hour").agg({
            "Problem Title": list,
            "Author": "count"
        }).reset_index().rename(columns={"Author": "Problem Count"})

        # Create hover text from problem titles
        grouped["Hover Text"] = grouped["Problem Title"].apply(lambda titles: "<br>".join(titles))

        # Ensure all hours 0-23 are present
        all_hours = pd.DataFrame({"Hour": list(range(24))})
        grouped = all_hours.merge(grouped, on="Hour", how="left")
        grouped["Problem Count"] = grouped["Problem Count"].fillna(0).astype(int)
        grouped["Hover Text"] = grouped["Hover Text"].fillna("No problems reported")

        # Plot
        fig = px.bar(
            grouped,
            x="Hour",
            y="Problem Count",
            hover_data={"Hover Text": True},
            labels={"Hour": "Hour of the Day", "Problem Count": "Number of Problems"},
            title="Problems Reported by Hour"
        )
        fig.update_traces(
            hovertemplate='%{customdata[0]}',
            customdata=grouped[["Hover Text"]].values
        )
        fig.update_layout(
            xaxis=dict(dtick=1),
            dragmode=False
            )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "scrollZoom": False,
                "displayModeBar": False,   
                "staticPlot": False,       
                "doubleClick": False,      
                "editable": False,
                "displaylogo": False
            }
        )