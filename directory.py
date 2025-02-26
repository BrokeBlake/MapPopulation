import streamlit as st
from app import PopulationMapApp

st.set_page_config(layout="wide")


#Remove top padding, and change sidebar size
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.3rem !important;
    }

    [data-testid="stSidebar"] {
        min-width: 200px !important;  /* Set default width */
        max-width: 200px !important;  /* Lock width to prevent resizing */
    }
    </style>
    """,
    unsafe_allow_html=True
)

MAPS = {
    "Melbourne": {
        "input_file": r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\Melbourne-Canberra\melbourne_population_density.parquet",
        "lat_middle": -37.8136,
        "lon_middle": 144.9631,
    },
    "Perth": {
        "input_file": r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\Perth\perth_population_density.parquet",
        "lat_middle": -31.9514,
        "lon_middle": 115.9617,
    },
    "Sydney": {
        "input_file": r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\Sydney\sydney_population_density.parquet",
        "lat_middle": -33.8688,
        "lon_middle": 151.1093,
    },
    "Brisbane": {
        "input_file": r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\Brisbane-GoldCoast\brisbane_population_density.parquet",
        "lat_middle": -27.4705,
        "lon_middle": 153.0260,
    }
}
st.sidebar.header("Select a City:")

selected_city = st.sidebar.radio(label="Select a City:", options=list(MAPS.keys()))

# Display Selected City
st.header(f"Calculate Population of a shape in {selected_city}")

# Initialize Map Application
PopulationMapApp(
    input_file=MAPS[selected_city]["input_file"],
    lat_middle=MAPS[selected_city]["lat_middle"],
    lon_middle=MAPS[selected_city]["lon_middle"],
    zoom_level=MAPS[selected_city].get("zoom_level", 10)
)