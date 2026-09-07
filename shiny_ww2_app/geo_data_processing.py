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
europe_gdf = gpd.read_file('geo_data/Europe_maps.geojson')
europe_gdf.head()

# %%
europe_gdf = europe_gdf.set_crs("ESRI:102013",allow_override= True)
europe_gdf["geometry"] = europe_gdf.make_valid()
#europe_gdf = europe_gdf.explode(column="geometry").drop(columns="geometry").set_geometry("geometry2").rename_geometry("geometry")
europe_gdf.geometry = europe_gdf.geometry.explode()[0:].values

europe_gdf.explore()
