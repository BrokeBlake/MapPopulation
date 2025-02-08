import rasterio
import numpy as np
import geopandas as gpd
from shapely.geometry import Point


class ExtractTif():
    """
    Converts a TIF file into a GeoDataFrame to use. Auto values are for the city of Melbourne

    """
    def __init__(self,
                 input_path = r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\GHS_POP_E2025_GLOBE_R2023A_4326_3ss_V1_0.tif",
                 output_path = r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\population_density.parquet",
                 lat_middle = -37.85,
                 lon_middle = 145,
                 zoom_level = 11,
                 width_px = 1350,
                 height_px = 1000,
                 geo_mask = True):
        
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

        print(F"Converting into Parquet file...")
        self.gdf = gpd.GeoDataFrame(
            {"longitude": lon, "latitude": lat, "population": pop_density, "area": area},
            geometry=[Point(x, y) for x, y in zip(lon, lat)],
            crs="EPSG:4326"  # WGS 84 Coordinate Reference System
        )

        self.pop_density = pop_density


    def save_to_file(self):

        self.gdf.to_parquet(self.output_gdf_path)

        print(f"GeoDataFrame saved as '{self.output_gdf_path}'")


if __name__ == "__main__":
    ExtractTif(lat_middle = -33.8688, lon_middle = 151.2093, output_path = r"C:\Users\blake\OneDrive\Documents\GitHub\MapPopulation\data\sydney_population_density.parquet")