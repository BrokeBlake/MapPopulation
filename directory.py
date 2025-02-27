import streamlit as st
from generateMap import PopulationMapApp

st.set_page_config(layout="wide")

import os
import streamlit as st

st.write("Current Directory:", os.getcwd())
st.write("Files in Root Directory:", os.listdir('.'))

# Check if data/ParquetFiles exists
if os.path.exists("data/ParquetFiles"):
    st.write("ParquetFiles Directory Found! Files inside:", os.listdir("data/ParquetFiles"))
else:
    st.write("ParquetFiles Directory Not Found!")


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
        "input_file": "data\ParquetFiles\melbourne_population_density.parquet",
        "lat_middle": -37.8136,
        "lon_middle": 144.9631,
    },
    "Perth": {
        "input_file": "data\ParquetFiles\perth_population_density.parquet",
        "lat_middle": -31.9514,
        "lon_middle": 115.9617,
    },
    "Sydney": {
        "input_file": "data\ParquetFiles\sydney_population_density.parquet",
        "lat_middle": -33.8688,
        "lon_middle": 151.1093,
    },
    "Brisbane": {
        "input_file": "data\ParquetFiles\brisbane_population_density.parquet",
        "lat_middle": -27.4705,
        "lon_middle": 153.0260,
    },
    "Adelaide": {
        "input_file": "data\ParquetFiles\adelaide_population_density.parquet",
        "lat_middle": -34.9285,
        "lon_middle": 138.6007,
    },
    "Auckland": {
        "input_file": "data\ParquetFiles\auckland_population_density.parquet",
        "lat_middle": -36.8509,
        "lon_middle": 174.7645,
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