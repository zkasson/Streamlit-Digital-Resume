import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap
from streamlit_folium import st_folium
import folium

# Set up
st.set_page_config(page_title='Digital Resume', layout='wide')

# Sidebar controls
st.sidebar.title('Controls')
st.sidebar.subheader("Click 'Next' to flip through my experience")
basemap_selection = st.sidebar.selectbox('Select a basemap', ['openstreetmap','CartoDB.DarkMatter', 'CartoDB.Positron'])

# Counter to track the current entry
if 'counter' not in st.session_state:
    st.session_state.counter = 0
col1, col2 = st.sidebar.columns([1, 1])  # Two buttons side-by-side

if col1.button('Back'):
    st.session_state.counter -= 1
    if st.session_state.counter <= -1:  # Reset to last item if underflow occurs
        st.session_state.counter = 10  

if col2.button('Next'):
    st.session_state.counter += 1
    if st.session_state.counter >= 11:  # Reset after the last item
        st.session_state.counter = 0

# Read the GeoJSON file

def read_json(url):
    return gpd.read_file(url)

json_file = r'https://raw.githubusercontent.com/zkasson/Streamlit-Digital-Resume/refs/heads/main/digitalResume.geojson'
state_json = r'https://raw.githubusercontent.com/zkasson/Portfolio/refs/heads/main/US_States.json'
gdf = read_json(json_file)
state_gdf = read_json(state_json)




# If counter is 0, show all points from the GeoDataFrame (gdf)
if st.session_state.counter == 0:
# Display the current counter value to debug
    st.title(f"Hi Land IQ. Thanks for having me!")
    st.write('This is a quick web app that I built to show you a bit of my previous experience.')

    # Get the bounds of the entire dataset
    bounds = gdf.total_bounds  # minx, miny, maxx, maxy
    center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]
    zoom_level = 3  

    # Create and display the map
    map = leafmap.Map(
    layers_control=True,
    draw_control=False,
    measure_control=False,
    fullscreen_control=False,
    center=center,
    zoom=zoom_level)

    # Add points for all locations
    for idx, row in gdf.iterrows():
        icon_name = row['Icon']
        coordinates = row.geometry.coords[0][::-1]  # Extract lat/lon

        # Use a folium DivIcon to create a pin-like marker
        folium.Marker(
            location=coordinates,
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    position: relative;
                    width: 36px; height: 36px;
                    background: gray;
                    border-radius: 50%; /* Make it a circle */
                    box-shadow: 0 2px 6px rgba(0,0,0,0.2); /* Add a subtle shadow */
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transform: translate(-50%, -50%);
                ">
                    <i class="fa fa-{icon_name}" style="font-size: 18px; color: white;"></i>
                </div>
                """
            ),
            popup=f"<b>{row['Name']}</b><br>{row['Description']}"
        ).add_to(map)
else:
    # Display the current location based on the counter
    current_id = st.session_state.counter 
    current_location = gdf[gdf['ID'] == current_id]
    current_location_name = current_location['Name'].iloc[0]
    current_location_desc = current_location['Description'].iloc[0]
    current_location_exp = current_location['Experience'].iloc[0]
    current_location_zoom = float(current_location['zoom'].iloc[0]) 
    current_icon = current_location['Icon'].iloc[0]


    # Display details
    st.subheader(f"Location: {current_location_name}")
    st.write(current_location_desc)
    st.write(current_location_exp)
    st.write(f"I learned {current_location_exp}")


    # Create and display the map
    map = leafmap.Map(
    layers_control=True,
    draw_control=False,
    measure_control=False,
    fullscreen_control=False,
    center=current_location.geometry.iloc[0].coords[0][::-1],
    zoom=current_location_zoom)

    # Add a single point for the current location
    for idx, row in current_location.iterrows():
        icon_name = row['Icon']
        coordinates = row.geometry.coords[0][::-1]  # Extract lat/lon

        # Use a folium DivIcon to create a pin-like marker
        folium.Marker(
            location=coordinates,
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    position: relative;
                    width: 36px; height: 36px;
                    background: gray;
                    border-radius: 50%; /* Make it a circle */
                    box-shadow: 0 2px 6px rgba(0,0,0,0.2); /* Add a subtle shadow */
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transform: translate(-50%, -50%);
                ">
                    <i class="fa fa-{icon_name}" style="font-size: 18px; color: white;"></i>
                </div>
                """
            ),
            popup=f"<b>{row['Name']}</b><br>{row['Description']}"
        ).add_to(map)

#Add basemap
map.add_basemap(basemap_selection)

# Add state boundaries with a bold style
map.add_gdf(
    gdf=state_gdf,
    layer_name='State Boundaries',
    style={
        'color': 'black',      
        'weight': .5,   
        'fill': False      
    },
    zoom_to_layer=False,
    info_mode=None  
)


st_folium(map, width=1100, height=900)

