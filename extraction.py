import rasterio
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from rasterio.transform import from_origin
from rasterio.enums import Resampling


class ExtractTif():
    """
    Converts a TIF file into a GeoDataFrame to use. Auto values are for the city of Melbourne

    """
    def __init__(self,
                 input_path = r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\Melbourne-Canberra\GHS_2025_pop_density_145_-35_melbourne_canberra.tif",
                 output_path = r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\Melbourne-Canberra\melbourne_population_density.parquet",
                 lat_middle = -37.8136,
                 lon_middle = 144.9631,
                 zoom_level = 10,
                 width_px = 850,
                 height_px = 625,
                 geo_mask = True):
        
        print("Starting Extraction...")
        self.tif_path = input_path
        self.output_gdf_path = output_path

        #Please note that these are all standardised and can be changed depending on data
        self.arcseconds_to_metres = 30.87  # Latitude conversion factor
        self.grid_resolution = 3  # 3x3 arcseconds
        self.geo_mask = geo_mask

        degrees_per_pixel = 360 / (256 * (2 ** zoom_level))
        lon_span = degrees_per_pixel * width_px* 1.1 #Just in case - it cant hurt to get a bit more information
        approx_lat_span = degrees_per_pixel * height_px * 1.1

        self.lon_min = round(lon_middle - lon_span / 2, 4)
        self.lon_max = round(lon_middle + lon_span / 2, 4)
        self.lat_min = round(lat_middle - approx_lat_span / 2, 4)
        self.lat_max = round(lat_middle + approx_lat_span / 2, 4)


        print(f"Determined Bounds as {self.lon_min}, {self.lon_max}, {self.lat_min}, {self.lat_max}")


        self.open_file()
        self.process_file()
        self.save_to_file()


    
    def open_file(self):

        print("Opening raster file...")
        with rasterio.open(self.tif_path) as dataset:
            self.transform = dataset.transform
            self.nodata = dataset.nodata
            self.pop_density = dataset.read(1)
            self.rows, self.cols = self.pop_density.shape

        print(f"Raster Shape: {self.pop_density.shape}")

    def process_file(self):
        pop_density = self.pop_density

        print(f"Converting into lat/lon...")
        # Convert raster indices to lat/lon
        grid_row, grid_col = np.meshgrid(range(self.rows), range(self.cols), indexing="ij")
        lon, lat = rasterio.transform.xy(self.transform, grid_row, grid_col)

        print(f"Flattening Arrays...")
        lon, lat, pop_density = np.array(lon).flatten(), np.array(lat).flatten(), pop_density.flatten() # Flatten arrays
        valid_mask = ~np.isnan(pop_density) if self.nodata is None else (pop_density != self.nodata) # Filter nodata
        lon, lat, pop_density = lon[valid_mask], lat[valid_mask], pop_density[valid_mask]
        if self.geo_mask:
            print(f"Applying Geographic Mask...")
            geo_mask = (self.lat_min <= lat) & (lat <= self.lat_max) & (self.lon_min <= lon) & (lon <= self.lon_max)
            lon, lat, pop_density = lon[geo_mask], lat[geo_mask], pop_density[geo_mask]

        # Compute the area of each grid cell
        dy = self.grid_resolution * self.arcseconds_to_metres
        dx = dy * np.cos(np.radians(lat))
        area = dx * dy

        pop_density = np.round(pop_density)

        nonzero_mask = pop_density > 0 # Remove zero-population cells
        lon, lat, pop_density, area = lon[nonzero_mask], lat[nonzero_mask], pop_density[nonzero_mask], area[nonzero_mask]

        print(f"Converting into Parquet file...")
        self.gdf = gpd.GeoDataFrame(
            {"longitude": lon, "latitude": lat, "population": pop_density},
            geometry=[Point(x, y) for x, y in zip(lon, lat)],
            crs="EPSG:4326"  # WGS 84 Coordinate Reference System
        )

    def save_to_file(self):

        self.gdf.to_parquet(self.output_gdf_path)
        print(f"GeoDataFrame saved as '{self.output_gdf_path}'")
    """
    def create_heatmap_tif(self):

        print("Generating Heatmap")

        res_x = abs(self.lon_max - self.lon_min) / self.cols
        res_y = abs(self.lat_max - self.lat_min) / self.rows

        heatmap_array = np.zeros((self.rows, self.cols), dtype=np.float32)

        for i in range(len(self.gdf)):
            row, col = ~self.transform * (self.gdf.iloc[i].longitude, self.gdf.iloc[i].latitude)
            row, col = int(row), int(col)
            if 0 <= row < self.rows and 0 <= col < self.cols: #If inside the given box - just in case use mistake
                heatmap_array[row, col] += self.gdf.iloc[i].population  # Aggregate population

        transform = from_origin(self.lon_min, self.lat_max, res_x, res_y)
        new_meta = {
            "driver": "GTiff",      "dtype": "float32",         "nodata": 0,
            "width": self.cols,     "height": self.rows,        "count": 1,
            "crs": "EPSG:4326",     "transform": transform,
        }

        with rasterio.open(self.output_heatmap_path, "w", **new_meta) as dst:
            dst.write(heatmap_array, 1)

        print(f"Heatmap GeoTIFF saved at {self.output_heatmap_path}")
    """
if __name__ == "__main__":
    cities = {
        "Melbourne": {
            "lat_middle": -37.8136,
            "lon_middle": 144.9631,
            "width_px": 850,
            "height_px": 625,
            "input_path": r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\Melbourne-Canberra\GHS_2025_pop_density_145_-35_melbourne_canberra.tif",
            "output_path": r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\Melbourne-Canberra\melbourne_full_population_density.parquet",
            "geo_mask": False
        },
        "Brisbane": {
            "lat_middle": -27.4705,
            "lon_middle": 153.0260,
            "width_px": 850,
            "height_px": 625,
            "input_path": r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\Brisbane-GoldCoast\GHS_2025_pop_density_155_-25_brisbane.tif",
            "output_path": r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\Brisbane-GoldCoast\brisbane_population_density.parquet"
        },
        "Sydney": {
            "lat_middle": -33.8688,
            "lon_middle": 151.1093,
            "width_px": 850,
            "height_px": 625,
            "input_path": r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\Sydney\GHS_2025_pop_density_155_-35_sydney.tif",
            "output_path": r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\Sydney\sydney_population_density.parquet"
        },
        "Perth": {
            "lat_middle": -31.9514,
            "lon_middle": 115.9617,
            "width_px": 850,
            "height_px": 625,
            "input_path": r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\Perth\GHS_2025_pop_density_115_-35_perth.tif",
            "output_path": r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\Perth\perth_population_density.parquet"
        }
    }

    ExtractTif(**cities["Melbourne"])
