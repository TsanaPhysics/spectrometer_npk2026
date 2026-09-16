#!/usr/bin/env python3
"""
Thailand 3D Topographic Analysis & Multi-View Scientific Plot
Digital Agriphysics & AI Research Unit (JC_AI_SciRBRU)
Department of Physics, Faculty of Science and Technology,
Rambhai Barni Rajabhat University (RBRU)

Generates:
models_3d/thailand_map_analysis.png
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LightSource
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import RegularGridInterpolator

def generate_analysis_plot():
    print("Generating Thailand 3D Topographic Analysis Visualization...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    out_dir = os.path.join(base_dir, "models_3d")
    
    # 1. Load Data
    dem_path = os.path.join(data_dir, "thailand_dem_mosaic.npz")
    geojson_path = os.path.join(data_dir, "thailand_provinces.geojson")
    
    dem_data = np.load(dem_path)
    elev_raw = dem_data['elev']
    bounds = dem_data['bounds']
    
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson = json.load(f)
        
    orig_lons = np.linspace(bounds[0], bounds[2], elev_raw.shape[1])
    orig_lats = np.linspace(bounds[3], bounds[1], elev_raw.shape[0])
    interp = RegularGridInterpolator((orig_lats, orig_lons), elev_raw, bounds_error=False, fill_value=0.0)
    
    # 2. Grid for Analysis: 400 x 240
    lon_min, lon_max = 97.35, 105.65
    lat_min, lat_max = 5.63, 20.45
    H, W = 420, 240
    
    lats = np.linspace(lat_max, lat_min, H)
    lons = np.linspace(lon_min, lon_max, W)
    GLAT, GLON = np.meshgrid(lats, lons, indexing='ij')
    elev = interp((GLAT, GLON))
    
    # Create Thailand Mask
    from skimage.draw import polygon
    th_mask = np.zeros((H, W), dtype=bool)
    for f in geojson['features']:
        geom = f['geometry']
        coords = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
        for poly in coords:
            ring = np.array(poly[0])
            c = np.clip(np.round((ring[:, 0] - lon_min) / (lon_max - lon_min) * (W - 1)).astype(int), 0, W - 1)
            r = np.clip(np.round((lat_max - ring[:, 1]) / (lat_max - lat_min) * (H - 1)).astype(int), 0, H - 1)
            rr, cc = polygon(r, c, shape=(H, W))
            th_mask[rr, cc] = True

    elev_thailand = np.where(th_mask, np.maximum(elev, 0.0), np.nan)
    
    # Custom Hypsometric Colormap (Sea -> Plains -> Plateau -> Mountain -> Peak)
    colors = [
        (0.00, "#1e3a8a"),  # Deep sea
        (0.05, "#0284c7"),  # Coastal shallow
        (0.08, "#15803d"),  # Lowland plains (Chao Phraya)
        (0.20, "#84cc16"),  # Uplands & undulating terrain
        (0.35, "#eab308"),  # Khorat plateau (200-400m)
        (0.55, "#ea580c"),  # High plateau & foothills (600-1000m)
        (0.75, "#b91c1c"),  # Mountain ridges (1200-1800m)
        (0.90, "#78350f"),  # High peaks (>2000m)
        (1.00, "#f8fafc")   # Alpine summit (Doi Inthanon 2565m)
    ]
    cmap_hypso = LinearSegmentedColormap.from_list("thai_hypso", [c[1] for c in colors])
    
    # 3. Setup Figure (2x2 Grid, Dark Theme)
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(18, 11), facecolor='#090d16')
    
    # --- PANEL 1: 3D Isometric Relief ---
    ax1 = fig.add_subplot(1, 2, 1, projection='3d', facecolor='#090d16')
    
    # Subsample for smooth 3D plotting
    sub = 3
    X_sub = GLON[::sub, ::sub]
    Y_sub = GLAT[::sub, ::sub]
    # In 3D: set sea floor to 0, land to true elevation
    Z_sub = np.where(th_mask[::sub, ::sub], np.maximum(elev[::sub, ::sub], 15.0), 0.0)
    
    # Hillshade
    ls = LightSource(azdeg=315, altdeg=45)
    rgb = ls.shade(Z_sub, cmap=cmap_hypso, vert_exag=0.008, blend_mode='overlay')
    
    surf = ax1.plot_surface(X_sub, Y_sub, Z_sub, facecolors=rgb, rstride=1, cstride=1,
                            linewidth=0, antialiased=True, shade=False)
    
    ax1.set_xlim([lon_min - 0.5, lon_max + 0.5])
    ax1.set_ylim([lat_min - 0.5, lat_max + 0.5])
    ax1.set_zlim([0, 3000])
    
    ax1.set_title("3D Topographic Relief Model of Thailand (Doi Inthanon 2,565 m)",
                  color='#38bdf8', fontsize=13, fontweight='bold', pad=12)
    ax1.set_xlabel("Longitude (°E)", color='#94a3b8', labelpad=8)
    ax1.set_ylabel("Latitude (°N)", color='#94a3b8', labelpad=8)
    ax1.set_zlabel("Elevation (m)", color='#94a3b8', labelpad=6)
    
    ax1.tick_params(colors='#64748b')
    ax1.xaxis.pane.fill = False
    ax1.yaxis.pane.fill = False
    ax1.zaxis.pane.fill = False
    ax1.view_init(elev=34, azim=-62)
    
    # --- PANEL 2: Cartographic Plan View with Province Borders & Landmarks ---
    ax2 = fig.add_subplot(2, 2, 2, facecolor='#0f172a')
    
    # Hillshade on 2D map
    rgb_2d = ls.shade(np.nan_to_num(elev, nan=0.0), cmap=cmap_hypso, vert_exag=0.005, blend_mode='soft')
    im2 = ax2.imshow(rgb_2d, extent=[lon_min, lon_max, lat_min, lat_max], origin='upper', aspect='equal')
    
    # Overlay Province Borders
    for f in geojson['features']:
        geom = f['geometry']
        coords = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
        for poly in coords:
            ring = np.array(poly[0])
            ax2.plot(ring[:, 0], ring[:, 1], color='#334155', linewidth=0.55, alpha=0.85)
            
    # Key Landmarks
    landmarks = [
        ("Doi Inthanon (2,565m)", 98.487, 18.588, '#ef4444', (10, 5)),
        ("Doi Chiang Dao (2,175m)", 98.90, 19.40, '#f97316', (10, 4)),
        ("Khao Kho (1,820m)", 101.0, 16.90, '#eab308', (10, 2)),
        ("Khao Soi Dao (1,675m)", 102.2, 12.95, '#10b981', (12, 10)),
        ("RBRU Chanthaburi", 102.11, 12.61, '#00e5ff', (12, -16)),
        ("Bangkok (Chao Phraya)", 100.50, 13.75, '#38bdf8', (10, -8)),
        ("Khao Luang (1,835m)", 99.70, 8.50, '#f59e0b', (10, 2)),
        ("Sankalakhiri Range", 101.30, 6.00, '#a855f7', (10, 2)),
    ]
    
    for name, lx, ly, col, offset in landmarks:
        ax2.scatter(lx, ly, color=col, s=40, edgecolors='#ffffff', linewidth=1.2, zorder=5)
        ax2.annotate(name, (lx, ly), xytext=offset, textcoords='offset points',
                     color='#f8fafc', fontsize=8, fontweight='bold',
                     bbox=dict(boxstyle="round,pad=0.2", fc='#1e293b', ec=col, lw=1, alpha=0.9), zorder=6)
        
    ax2.set_xlim([lon_min, lon_max])
    ax2.set_ylim([lat_min, lat_max])
    ax2.set_title("Cartographic Relief & 77 Provincial Boundaries", color='#38bdf8', fontsize=12, fontweight='bold')
    ax2.set_xlabel("Longitude (°E)", color='#94a3b8')
    ax2.set_ylabel("Latitude (°N)", color='#94a3b8')
    ax2.grid(True, color='#1e293b', linestyle=':', alpha=0.6)
    ax2.tick_params(colors='#64748b')
    
    # --- PANEL 3: North-to-South Longitudinal Elevation Transect ---
    ax3 = fig.add_subplot(2, 4, 7, facecolor='#0f172a')
    
    # Transect along Lon = 99.5°E
    col_idx = int(round((99.5 - lon_min) / (lon_max - lon_min) * (W - 1)))
    transect_ns = elev[:, col_idx]
    
    ax3.plot(lats, transect_ns, color='#00e5ff', linewidth=1.6, label='Topographic Profile')
    ax3.fill_between(lats, np.maximum(transect_ns, 0), 0, color='#0284c7', alpha=0.35)
    ax3.axhline(0, color='#38bdf8', linestyle='--', linewidth=0.8, label='Sea Level (0m)')
    
    ax3.set_title("N-S Transect (Lon: 99.5°E)", color='#38bdf8', fontsize=10, fontweight='bold')
    ax3.set_xlabel("Latitude (°N)", color='#94a3b8', fontsize=8)
    ax3.set_ylabel("Elevation (m)", color='#94a3b8', fontsize=8)
    ax3.set_xlim([lat_min, lat_max])
    ax3.set_ylim([-50, 2400])
    ax3.grid(True, color='#1e293b', linestyle=':')
    ax3.tick_params(colors='#64748b', labelsize=8)
    
    # Annotate key regions along N-S
    ax3.annotate("North Mtns", xy=(19.0, 1800), color='#f59e0b', fontsize=7, fontweight='bold')
    ax3.annotate("Central Basin", xy=(14.0, 100), color='#10b981', fontsize=7, fontweight='bold')
    ax3.annotate("Gulf", xy=(12.0, -30), color='#38bdf8', fontsize=7)
    ax3.annotate("South Peninsula", xy=(8.5, 1200), color='#a855f7', fontsize=7, fontweight='bold')
    
    # --- PANEL 4: West-to-East Equatorial Elevation Transect ---
    ax4 = fig.add_subplot(2, 4, 8, facecolor='#0f172a')
    
    # Transect along Lat = 15.0°N (Tenasserim -> Central -> Khorat Plateau -> Mekong)
    row_idx = int(round((lat_max - 15.0) / (lat_max - lat_min) * (H - 1)))
    transect_we = elev[row_idx, :]
    
    ax4.plot(lons, transect_we, color='#10b981', linewidth=1.6, label='Topographic Profile')
    ax4.fill_between(lons, np.maximum(transect_we, 0), 0, color='#059669', alpha=0.35)
    ax4.axhline(0, color='#38bdf8', linestyle='--', linewidth=0.8)
    
    ax4.set_title("W-E Transect (Lat: 15.0°N)", color='#38bdf8', fontsize=10, fontweight='bold')
    ax4.set_xlabel("Longitude (°E)", color='#94a3b8', fontsize=8)
    ax4.set_ylabel("Elevation (m)", color='#94a3b8', fontsize=8)
    ax4.set_xlim([lon_min, lon_max])
    ax4.set_ylim([-50, 1800])
    ax4.grid(True, color='#1e293b', linestyle=':')
    ax4.tick_params(colors='#64748b', labelsize=8)
    
    ax4.annotate("Tenasserim", xy=(98.5, 1400), color='#ef4444', fontsize=7, fontweight='bold')
    ax4.annotate("Chao Phraya", xy=(100.2, 80), color='#00e5ff', fontsize=7)
    ax4.annotate("Phetchabun", xy=(101.4, 900), color='#eab308', fontsize=7)
    ax4.annotate("Khorat Plateau (250m)", xy=(103.2, 350), color='#f97316', fontsize=7, fontweight='bold')
    ax4.annotate("Mekong", xy=(105.2, 180), color='#38bdf8', fontsize=7)
    
    # Master Super Title
    plt.suptitle("JC_AI_SciRBRU Digital Agriphysics • Kingdom of Thailand 3D Topographic Model Verification",
                 color='#f8fafc', fontsize=16, fontweight='bold', y=0.96)
    
    out_img_path = os.path.join(out_dir, "thailand_map_analysis.png")
    plt.tight_layout(rect=[0, 0.03, 1, 0.94])
    plt.savefig(out_img_path, dpi=200, facecolor='#090d16')
    plt.close()
    print(f"[SUCCESS] Saved {out_img_path}")

if __name__ == '__main__':
    generate_analysis_plot()
