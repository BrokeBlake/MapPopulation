import math

def get_map_bounds(center_lat, center_lon, width_px, height_px, zoom_level):
    """
    Get the map bounds, to calculate exactly what data is needed for each map
    """

    degrees_per_pixel = 360 / (256 * (2 ** zoom))
    lon_span = degrees_per_pixel * width_px* 1.1 #Just in case - it cant hurt to get a bit more information

    lon_min = center_lon - lon_span / 2
    lon_max = center_lon + lon_span / 2

    approx_lat_span = degrees_per_pixel * height_px * 1.1
    lat_min = center_lat - approx_lat_span / 2
    lat_max = center_lat + approx_lat_span / 2

    return {"lon_min": lon_min, "lon_max": lon_max, "lat_min": lat_min, "lat_max": lat_max}

# Example usage
center_lat, center_lon = -37.85, 145  # Your map center
width_px, height_px = 1350, 1000
zoom = 11

bounds = get_map_bounds(center_lat, center_lon, width_px, height_px, zoom)
print(bounds)
