#!/usr/bin/env python3
"""
Thailand 3D Topographic Analysis & Multi-View Scientific Plot
Enhanced with Major River Basins (ลุ่มแม่น้ำ) and Rich Hypsometric Color Grading
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
    print("Generating Enhanced Thailand 3D Topographic & River Basin Visualization...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    out_dir = os.path.join(base_dir, "models_3d", "thailand_map")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Load GIS Data
    dem_path = os.path.join(data_dir, "thailand_dem_mosaic.npz")
    geojson_path = os.path.join(data_dir, "thailand_provinces.geojson")
    rivers_path = os.path.join(data_dir, "thailand_rivers.geojson")
    
    dem_data = np.load(dem_path)
    elev_raw = dem_data['elev']
    bounds = dem_data['bounds']
    
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson = json.load(f)
        
    rivers_data = None
    if os.path.exists(rivers_path):
        with open(rivers_path, 'r', encoding='utf-8') as rf:
            rivers_data = json.load(rf)
            
    orig_lons = np.linspace(bounds[0], bounds[2], elev_raw.shape[1])
    orig_lats = np.linspace(bounds[3], bounds[1], elev_raw.shape[0])
    interp = RegularGridInterpolator((orig_lats, orig_lons), elev_raw, bounds_error=False, fill_value=0.0)
    
    # 2. Target Grid for Analysis: 420 x 240
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

    # 3. Refined Rich Hypsometric Palette (National Geographic / Physical Atlas Style)
    # Ocean -> Coastal/Delta -> Alluvial Plains -> Khorat Plateau -> Uplands -> Mountain Ridges -> Alpine Summits
    colors = [
        (0.00, "#081c3b"),  # Deep ocean
        (0.04, "#0284c7"),  # Coastal shallow / Gulf waters
        (0.07, "#1b4332"),  # Lowland delta & Chao Phraya basin (<100m)
        (0.18, "#2d6a4f"),  # Alluvial plains & river valleys (100-250m)
        (0.32, "#74c69d"),  # Foothills & undulating plains (250-400m)
        (0.48, "#e9c46a"),  # Khorat sandstone plateau (400-700m)
        (0.65, "#e76f51"),  # Intermediate mountain ranges (700-1200m)
        (0.80, "#b0413e"),  # High mountain ridges (1200-1800m)
        (0.92, "#6c2d2c"),  # High peaks (>1800m)
        (1.00, "#ffffff")   # Alpine granite/snow summit (Doi Inthanon 2565m)
    ]
    cmap_hypso = LinearSegmentedColormap.from_list("thai_hypso_rich", [c[1] for c in colors])
    
    # Configure Thai fonts in Matplotlib
    plt.rcParams['font.sans-serif'] = ['Thonburi', 'Arial', 'DejaVu Sans']
    plt.rcParams['font.family'] = 'sans-serif'
    
    # 4. Setup Master Figure (2x2 Grid, Dark Theme)
    fig = plt.figure(figsize=(19, 11.5), facecolor='#070b12')
    
    # --- PANEL 1: 3D Isometric Relief with Overlaid River Arteries ---
    ax1 = fig.add_subplot(1, 2, 1, projection='3d', facecolor='#070b12')
    
    sub = 3
    X_sub = GLON[::sub, ::sub]
    Y_sub = GLAT[::sub, ::sub]
    Z_sub = np.where(th_mask[::sub, ::sub], np.maximum(elev[::sub, ::sub], 15.0), 0.0)
    
    ls = LightSource(azdeg=315, altdeg=48)
    rgb_3d = ls.shade(Z_sub, cmap=cmap_hypso, vert_exag=0.008, blend_mode='overlay')
    
    surf = ax1.plot_surface(X_sub, Y_sub, Z_sub, facecolors=rgb_3d, rstride=1, cstride=1,
                            linewidth=0, antialiased=True, shade=False)
    
    # Overlay River Arteries in 3D
    if rivers_data:
        for rf_feat in rivers_data['features']:
            r_geom = rf_feat['geometry']
            r_coords = r_geom['coordinates']
            r_lines = r_coords if r_geom['type'] == 'MultiLineString' else [r_coords]
            for r_seg in r_lines:
                r_pts = np.array(r_seg)
                if len(r_pts) < 2:
                    continue
                # Filter points within bounds
                valid = (r_pts[:, 0] >= lon_min) & (r_pts[:, 0] <= lon_max) & (r_pts[:, 1] >= lat_min) & (r_pts[:, 1] <= lat_max)
                if np.sum(valid) > 1:
                    rx = r_pts[valid, 0]
                    ry = r_pts[valid, 1]
                    # Sample Z along river path and lift slightly
                    rz = interp(np.column_stack([ry, rx]))
                    rz = np.maximum(rz, 10.0) + 25.0 # Float above surface
                    ax1.plot(rx, ry, rz, color='#38bdf8', linewidth=1.1, alpha=0.9, zorder=10)
                    
    ax1.set_xlim([lon_min - 0.5, lon_max + 0.5])
    ax1.set_ylim([lat_min - 0.5, lat_max + 0.5])
    ax1.set_zlim([0, 3000])
    
    ax1.set_title("3D Topographic Relief & Active River Network (ลุ่มแม่น้ำหลัก)",
                  color='#38bdf8', fontsize=13, fontweight='bold', pad=12)
    ax1.set_xlabel("Longitude (°E)", color='#94a3b8', labelpad=8)
    ax1.set_ylabel("Latitude (°N)", color='#94a3b8', labelpad=8)
    ax1.set_zlabel("Elevation (m)", color='#94a3b8', labelpad=6)
    
    ax1.tick_params(colors='#64748b')
    ax1.xaxis.pane.fill = False
    ax1.yaxis.pane.fill = False
    ax1.zaxis.pane.fill = False
    ax1.view_init(elev=34, azim=-62)
    
    # --- PANEL 2: 2D Cartographic Plan with Hypsometric Shading & River Basins ---
    ax2 = fig.add_subplot(2, 2, 2, facecolor='#0c1322')
    
    rgb_2d = ls.shade(np.nan_to_num(elev, nan=0.0), cmap=cmap_hypso, vert_exag=0.005, blend_mode='soft')
    im2 = ax2.imshow(rgb_2d, extent=[lon_min, lon_max, lat_min, lat_max], origin='upper', aspect='equal')
    
    # Overlay Province Borders (Subtle dark slate)
    for f in geojson['features']:
        geom = f['geometry']
        coords = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
        for poly in coords:
            ring = np.array(poly[0])
            ax2.plot(ring[:, 0], ring[:, 1], color='#334155', linewidth=0.55, alpha=0.75)
            
    # Overlay All 37 River Segments
    if rivers_data:
        for rf_feat in rivers_data['features']:
            p = rf_feat.get('properties', {})
            r_geom = rf_feat['geometry']
            r_coords = r_geom['coordinates']
            r_lines = r_coords if r_geom['type'] == 'MultiLineString' else [r_coords]
            r_name = p.get('name', '')
            is_major = r_name in ['Chao Phraya', 'Mekong', 'Ping', 'Nan', 'Mun', 'Chi', 'Mae Klong']
            lw = 1.4 if is_major else 0.85
            col = '#00e5ff' if is_major else '#38bdf8'
            for r_seg in r_lines:
                r_pts = np.array(r_seg)
                ax2.plot(r_pts[:, 0], r_pts[:, 1], color=col, linewidth=lw, alpha=0.92, zorder=4)
                
    # River Basin Annotations (ลุ่มน้ำ)
    basin_labels = [
        ("ลุ่มน้ำเจ้าพระยา (Chao Phraya)", 100.2, 14.8, '#00e5ff', 9),
        ("ลุ่มน้ำชี-มูล (Chi-Mun Basin)", 103.5, 15.6, '#38bdf8', 9),
        ("ลุ่มน้ำแม่กลอง (Mae Klong)", 99.2, 14.2, '#00e5ff', 8),
        ("ลุ่มน้ำป่าสัก (Pa Sak)", 101.1, 15.6, '#7dd3fc', 8),
        ("ลุ่มน้ำตาปี (Tapi Basin)", 99.1, 8.8, '#38bdf8', 8),
        ("แม่น้ำโขง (Mekong)", 104.8, 17.5, '#0284c7', 8)
    ]
    for b_name, bx, by, b_col, b_sz in basin_labels:
        ax2.text(bx, by, b_name, color=b_col, fontsize=b_sz, fontweight='bold',
                 bbox=dict(boxstyle="round,pad=0.25", fc='#081426', ec=b_col, lw=0.8, alpha=0.85),
                 zorder=6, ha='center', va='center')
        
    # Key Mountain & Cultural Landmarks
    landmarks = [
        ("Doi Inthanon (2,565m)", 98.487, 18.588, '#ef4444', (10, 6)),
        ("Doi Chiang Dao (2,175m)", 98.90, 19.40, '#f97316', (10, 4)),
        ("Khao Kho (1,820m)", 101.0, 16.90, '#eab308', (10, 2)),
        ("Khao Soi Dao (1,675m)", 102.2, 12.95, '#10b981', (12, 10)),
        ("RBRU Chanthaburi", 102.11, 12.61, '#00e5ff', (12, -16)),
        ("Bangkok (Chao Phraya)", 100.50, 13.75, '#38bdf8', (10, -8)),
        ("Khao Luang (1,835m)", 99.70, 8.50, '#f59e0b', (10, 2)),
        ("Sankalakhiri Range", 101.30, 6.00, '#a855f7', (10, 2)),
    ]
    
    for name, lx, ly, col, offset in landmarks:
        ax2.scatter(lx, ly, color=col, s=36, edgecolors='#ffffff', linewidth=1.1, zorder=7)
        ax2.annotate(name, (lx, ly), xytext=offset, textcoords='offset points',
                     color='#f8fafc', fontsize=7.5, fontweight='bold',
                     bbox=dict(boxstyle="round,pad=0.2", fc='#1e293b', ec=col, lw=1, alpha=0.9), zorder=8)
        
    ax2.set_xlim([lon_min, lon_max])
    ax2.set_ylim([lat_min, lat_max])
    ax2.set_title("แผนที่แสดงระดับความสูง-ต่ำ ขอบเขต 77 จังหวัด และโครงข่ายลุ่มน้ำ", color='#38bdf8', fontsize=12, fontweight='bold')
    ax2.set_xlabel("Longitude (°E)", color='#94a3b8')
    ax2.set_ylabel("Latitude (°N)", color='#94a3b8')
    ax2.grid(True, color='#1e293b', linestyle=':', alpha=0.5)
    ax2.tick_params(colors='#64748b')
    
    # Hypsometric Colorbar
    cax = fig.add_axes([0.915, 0.54, 0.015, 0.36])
    sm = plt.cm.ScalarMappable(cmap=cmap_hypso, norm=plt.Normalize(vmin=0, vmax=2565))
    sm.set_array([])
    cb = fig.colorbar(sm, cax=cax)
    cb.set_label("ระดับความสูงเหนือระดับน้ำทะเล (Elevation, m)", color='#94a3b8', fontsize=8, labelpad=8)
    cb.ax.tick_params(colors='#94a3b8', labelsize=8)
    cb.set_ticks([0, 100, 300, 600, 1200, 1800, 2565])
    cb.ax.set_yticklabels(['0m (ทะเล)', '100m (ที่ราบลุ่ม)', '300m (ที่ดอน)', '600m (ที่ราบสูง)', '1200m (ภูเขา)', '1800m (สันเขา)', '2565m (ยอดดอย)'])
    
    # --- PANEL 3: N-S Longitudinal Profile ---
    ax3 = fig.add_subplot(2, 4, 7, facecolor='#0c1322')
    col_idx = int(round((99.5 - lon_min) / (lon_max - lon_min) * (W - 1)))
    transect_ns = elev[:, col_idx]
    
    ax3.plot(lats, transect_ns, color='#00e5ff', linewidth=1.5)
    ax3.fill_between(lats, np.maximum(transect_ns, 0), 0, color='#0284c7', alpha=0.35)
    ax3.axhline(0, color='#38bdf8', linestyle='--', linewidth=0.7)
    
    ax3.set_title("N-S Transect (Lon: 99.5°E)", color='#38bdf8', fontsize=9.5, fontweight='bold')
    ax3.set_xlabel("Latitude (°N)", color='#94a3b8', fontsize=8)
    ax3.set_ylabel("Elevation (m)", color='#94a3b8', fontsize=8)
    ax3.set_xlim([lat_min, lat_max])
    ax3.set_ylim([-50, 2400])
    ax3.grid(True, color='#1e293b', linestyle=':')
    ax3.tick_params(colors='#64748b', labelsize=8)
    
    ax3.annotate("North Mtns", xy=(19.0, 1750), color='#f59e0b', fontsize=7, fontweight='bold')
    ax3.annotate("Chao Phraya Basin", xy=(14.0, 100), color='#10b981', fontsize=7, fontweight='bold')
    ax3.annotate("Gulf", xy=(11.8, -30), color='#38bdf8', fontsize=7)
    ax3.annotate("South Peninsula", xy=(8.5, 1150), color='#a855f7', fontsize=7, fontweight='bold')
    
    # --- PANEL 4: W-E Transect ---
    ax4 = fig.add_subplot(2, 4, 8, facecolor='#0c1322')
    row_idx = int(round((lat_max - 15.0) / (lat_max - lat_min) * (H - 1)))
    transect_we = elev[row_idx, :]
    
    ax4.plot(lons, transect_we, color='#10b981', linewidth=1.5)
    ax4.fill_between(lons, np.maximum(transect_we, 0), 0, color='#059669', alpha=0.35)
    ax4.axhline(0, color='#38bdf8', linestyle='--', linewidth=0.7)
    
    ax4.set_title("W-E Transect (Lat: 15.0°N)", color='#38bdf8', fontsize=9.5, fontweight='bold')
    ax4.set_xlabel("Longitude (°E)", color='#94a3b8', fontsize=8)
    ax4.set_ylabel("Elevation (m)", color='#94a3b8', fontsize=8)
    ax4.set_xlim([lon_min, lon_max])
    ax4.set_ylim([-50, 1800])
    ax4.grid(True, color='#1e293b', linestyle=':')
    ax4.tick_params(colors='#64748b', labelsize=8)
    
    ax4.annotate("Tenasserim", xy=(98.5, 1380), color='#ef4444', fontsize=7, fontweight='bold')
    ax4.annotate("Chao Phraya", xy=(100.2, 80), color='#00e5ff', fontsize=7)
    ax4.annotate("Phetchabun", xy=(101.4, 900), color='#eab308', fontsize=7)
    ax4.annotate("Khorat Plateau (250m)", xy=(103.2, 350), color='#f97316', fontsize=7, fontweight='bold')
    ax4.annotate("Mekong", xy=(105.2, 180), color='#38bdf8', fontsize=7)
    
    # Super Title
    plt.suptitle("JC_AI_SciRBRU Digital Agriphysics • Thailand 3D Topographic & River Basin System (โครงข่ายลุ่มน้ำและระดับความสูง-ต่ำ)",
                 color='#f8fafc', fontsize=15, fontweight='bold', y=0.96)
    
    out_img_path = os.path.join(out_dir, "thailand_map_analysis.png")
    plt.tight_layout(rect=[0, 0.03, 0.90, 0.94])
    plt.savefig(out_img_path, dpi=200, facecolor='#070b12')
    plt.close()
    print(f"[SUCCESS] Saved {out_img_path}")

if __name__ == '__main__':
    generate_analysis_plot()
