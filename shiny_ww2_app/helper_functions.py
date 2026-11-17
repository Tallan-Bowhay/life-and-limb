import pandas as pd
import geopandas as gpd

def quick_inspect_geo_data(gdf, name = "Geo DataFrame"):
    print(f"--- {name} ---")
    print("CRS:", gdf.crs)
    print("Feature count:", len(gdf))
    print("Columns:", list(gdf.columns))
    print("Geometry types:", gdf.geom_type.value_counts().to_dict())
    print("Invalid geoms:", (~gdf.is_valid).sum())
    print()