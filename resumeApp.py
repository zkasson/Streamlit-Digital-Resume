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
    if st.session_state.counter < -1:  # Reset to last item if underflow occurs
        st.session_state.counter = 9  # Assuming 10 entries (IDs 1-10)

if col2.button('Next'):
    st.session_state.counter += 1
    if st.session_state.counter >= 10:  # Reset after the last item
        st.session_state.counter = 0

# Read the GeoJSON file
@st.cache_data
def read_json(url):
    return gpd.read_file(url)

json_file = r'C:\Users\zackk\OneDrive\Desktop\Resume\Streamlit Digital Resume\digitalResume.geojson'
state_json = r'https://raw.githubusercontent.com/zkasson/Portfolio/refs/heads/main/US_States.json'
gdf = read_json(json_file)
state_gdf = read_json(state_json)

# Display the current location based on the counter
current_id = st.session_state.counter + 1
current_location = gdf[gdf['ID'] == current_id]
current_location_name = current_location['Name'].iloc[0]
current_location_desc = current_location['Description'].iloc[0]
current_location_zoom = int(current_location['zoom'].iloc[0]) 
current_icon = current_location['Icon'].iloc[0]


# Display details
st.subheader(f"Location: {current_location_name}")
st.write(current_location_desc)

# Create and display the map
map = leafmap.Map(
    layers_control=True,
    draw_control=False,
    measure_control=False,
    fullscreen_control=False,
    center=current_location.geometry.iloc[0].coords[0][::-1],
    zoom=current_location_zoom)
map.add_basemap(basemap_selection)

# Add points with custom icons and sizes
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
                <i class="fa fa-{icon_name}" style="
                    font-size: 18px; /* Size of the icon */
                    color: white;">
                </i>
            </div>
            """
        ),
        popup=f"<b>{row['Name']}</b><br>{row['Description']}"
    ).add_to(map)


# Add state boundaries with a bold style
map.add_gdf(
    gdf=state_gdf,
    layer_name='State Boundaries',
    style={
        'color': 'black',      
        'weight': 2,   
        'fill': False      
    },
    zoom_to_layer=False,
    info_mode=None  
)


st_folium(map, width=1100, height=900)
