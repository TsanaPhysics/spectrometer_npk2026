#!/usr/bin/env python3
"""
Thailand GIS & Topography Processor
Downloads and prepares:
1. data/thailand_provinces.geojson (77 provinces)
2. data/thailand_dem_mosaic.npz (Real-world digital elevation model grid)
"""

import os
import io
import json
import math
import requests
import numpy as np
from PIL import Image

def get_tile_bounds(zoom, x, y):
    """Returns lat/lon bounds of a Web Mercator tile (lon_min, lat_min, lon_max, lat_max)"""
    n = 2.0 ** zoom
    lon_min = x / n * 360.0 - 180.0
    lon_max = (x + 1) / n * 360.0 - 180.0
    lat_rad_max = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_rad_min = math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n)))
    lat_min = math.degrees(lat_rad_min)
    lat_max = math.degrees(lat_rad_max)
    return lon_min, lat_min, lon_max, lat_max

def prepare_gis_data(data_dir="data"):
    os.makedirs(data_dir, exist_ok=True)
    
    # 1. GeoJSON Provinces
    geojson_path = os.path.join(data_dir, "thailand_provinces.geojson")
    if not os.path.exists(geojson_path):
        print("Downloading Thailand GeoJSON...")
        url = 'https://raw.githubusercontent.com/apisit/thailand.json/master/thailand.json'
        r = requests.get(url, timeout=15)
        with open(geojson_path, 'wb') as f:
            f.write(r.content)
        print(f"Saved {geojson_path}")
    else:
        print(f"Using cached {geojson_path}")

    # 2. DEM Mosaic
    dem_npz_path = os.path.join(data_dir, "thailand_dem_mosaic.npz")
    if not os.path.exists(dem_npz_path):
        print("Downloading AWS Terrarium elevation tiles (Zoom 6, x:49-50, y:28-31)...")
        zoom = 6
        tiles = []
        for y in range(28, 32):
            row = []
            for x in range(49, 51):
                url = f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{zoom}/{x}/{y}.png'
                r = requests.get(url, timeout=15)
                img = Image.open(io.BytesIO(r.content))
                row.append(np.array(img))
            tiles.append(np.hstack(row))
        mosaic = np.vstack(tiles)
        
        # Terrarium decoding: (R * 256 + G + B / 256) - 32768
        elev = (mosaic[:, :, 0].astype(np.float32) * 256.0 + 
                mosaic[:, :, 1].astype(np.float32) + 
                mosaic[:, :, 2].astype(np.float32) / 256.0) - 32768.0
        
        # Tile bounds:
        # x=49 to 50: lon_min for x=49, lon_max for x=50
        lon_min, _, _, _ = get_tile_bounds(zoom, 49, 28)
        _, _, lon_max, _ = get_tile_bounds(zoom, 50, 28)
        # y=28 to 31: lat_max for y=28, lat_min for y=31
        _, _, _, lat_max = get_tile_bounds(zoom, 49, 28)
        _, lat_min, _, _ = get_tile_bounds(zoom, 49, 31)
        
        np.savez_compressed(dem_npz_path, elev=elev, bounds=[lon_min, lat_min, lon_max, lat_max])
        print(f"Saved {dem_npz_path} | Shape: {elev.shape} | Lon: [{lon_min:.2f}, {lon_max:.2f}], Lat: [{lat_min:.2f}, {lat_max:.2f}]")
    else:
        print(f"Using cached {dem_npz_path}")

if __name__ == '__main__':
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prepare_gis_data(os.path.join(root_dir, "data"))
