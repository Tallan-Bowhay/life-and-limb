# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import pandas as pd
import geopandas as gpd

from shapely.geometry import GeometryCollection, MultiPolygon

# %%
french_line = gpd.read_file("geo_data/Ligne_de_demarquation_france.geojson")
french_line.explore()

# %%
europe_gdf = gpd.read_file('geo_data/Europe_maps_claude_reformat.geojson')
europe_gdf.head()

# %%
#europe_gdf = europe_gdf.set_crs("ESRI:102013",allow_override= True)
europe_gdf["geometry"] = europe_gdf.make_valid()

europe_gdf.explore(column="Foreign_Po")

# %%
europe_gdf["Foreign_Po"].value_counts()

# %%
power_remap_dict = {
    "Neutral":"Neutral",
    "German-occupied":"Axis Controlled",
    "Axis-aligned": "Axis",
    "Axis and German-occupied":"Axis Controlled",
    "German Protectorate":"Axis Controlled",
    "German, Bulgarian-occupied":"Axis Controlled",
    "Allied":"Allies",
    "Allies":"Allies",
    "Axis":"Axis"
}

europe_gdf["Simp_Foreign_Po"] = europe_gdf["Foreign_Po"].map(power_remap_dict)

europe_gdf.explore(column="Simp_Foreign_Po")
