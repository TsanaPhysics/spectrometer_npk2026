#!/usr/bin/env python3
"""
Thailand 3D Topographic Map & Solid Model Generator
Digital Agriphysics & AI Research Unit (JC_AI_SciRBRU)
Department of Physics, Faculty of Science and Technology,
Rambhai Barni Rajabhat University (RBRU)

Generates:
1. models_3d/thailand_topographic_map_3d.stl (Display Plinth with real DEM, borders, typography & compass)
2. models_3d/thailand_country_standalone_3d.stl (Standalone country cutout with relief surface)
3. models_3d/thailand_relief.png (16-bit Heightmap for OpenSCAD / Blender / CNC)
4. models_3d/thailand_map.scad (Parametric OpenSCAD Model)
"""

import os
import io
import time
import json
import struct
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage.draw import polygon, line
from skimage import measure
from scipy.interpolate import RegularGridInterpolator

def write_binary_stl(filename, verts, faces, title="Thailand_Map_JC_AI_SciRBRU"):
    """Writes 3D triangle mesh to standard binary STL format."""
    num_faces = len(faces)
    with open(filename, 'wb') as f:
        header = title.encode('ascii').ljust(80, b' ')[:80]
        f.write(header)
        f.write(struct.pack('<I', num_faces))
        
        v0 = verts[faces[:, 0]]
        v1 = verts[faces[:, 1]]
        v2 = verts[faces[:, 2]]
        normals = np.cross(v1 - v0, v2 - v0)
        norm_lens = np.linalg.norm(normals, axis=1, keepdims=True)
        norm_lens[norm_lens == 0] = 1.0
        normals = normals / norm_lens
        
        data = np.zeros(num_faces, dtype=[
            ('norm', '<f4', (3,)),
            ('v0', '<f4', (3,)),
            ('v1', '<f4', (3,)),
            ('v2', '<f4', (3,)),
            ('attr', '<u2')
        ])
        data['norm'] = normals
        data['v0'] = v0
        data['v1'] = v1
        data['v2'] = v2
        data['attr'] = 0
        data.tofile(f)
        
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    print(f"[OK] Generated {filename}")
    print(f"     Faces: {num_faces:,} triangles | Size: {size_mb:.2f} MB")

def mesh_heightfield_to_stl(z_grid, dx, dy, out_path, title="Thailand_Plinth"):
    """
    Converts 2D heightfield array into mathematically guaranteed 100% watertight binary STL.
    Zero boundary edges, zero non-manifold edges.
    """
    H, W = z_grid.shape
    N = H * W
    
    cols = np.arange(W, dtype=np.float32)
    rows = np.arange(H, dtype=np.float32)
    C, R = np.meshgrid(cols, rows)
    
    X = (C - (W - 1) / 2.0) * dx
    Y = ((H - 1) / 2.0 - R) * dy
    Z_top = z_grid
    Z_bot = np.zeros_like(Z_top)
    
    verts_top = np.column_stack([X.ravel(), Y.ravel(), Z_top.ravel()])
    verts_bot = np.column_stack([X.ravel(), Y.ravel(), Z_bot.ravel()])
    verts = np.vstack([verts_top, verts_bot])
    
    idx = np.arange(N, dtype=np.int32).reshape(H, W)
    
    # Top quads (facing +Z)
    v00 = idx[:-1, :-1].ravel()
    v01 = idx[:-1, 1:].ravel()
    v10 = idx[1:, :-1].ravel()
    v11 = idx[1:, 1:].ravel()
    top_f1 = np.column_stack([v00, v10, v01])
    top_f2 = np.column_stack([v01, v10, v11])
    
    # Bottom quads (facing -Z)
    b00 = v00 + N
    b01 = v01 + N
    b10 = v10 + N
    b11 = v11 + N
    bot_f1 = np.column_stack([b00, b01, b10])
    bot_f2 = np.column_stack([b01, b11, b10])
    
    # North wall (r=0, +Y)
    n_top_0, n_top_1 = idx[0, :-1], idx[0, 1:]
    n_bot_0, n_bot_1 = n_top_0 + N, n_top_1 + N
    north_f1 = np.column_stack([n_top_0, n_top_1, n_bot_0])
    north_f2 = np.column_stack([n_top_1, n_bot_1, n_bot_0])
    
    # South wall (r=H-1, -Y)
    s_top_0, s_top_1 = idx[-1, :-1], idx[-1, 1:]
    s_bot_0, s_bot_1 = s_top_0 + N, s_top_1 + N
    south_f1 = np.column_stack([s_top_1, s_top_0, s_bot_1])
    south_f2 = np.column_stack([s_top_0, s_bot_0, s_bot_1])
    
    # West wall (c=0, -X)
    w_top_0, w_top_1 = idx[:-1, 0], idx[1:, 0]
    w_bot_0, w_bot_1 = w_top_0 + N, w_top_1 + N
    west_f1 = np.column_stack([w_top_0, w_top_1, w_bot_0])
    west_f2 = np.column_stack([w_top_1, w_bot_1, w_bot_0])
    
    # East wall (c=W-1, +X)
    e_top_0, e_top_1 = idx[:-1, -1], idx[1:, -1]
    e_bot_0, e_bot_1 = e_top_0 + N, e_top_1 + N
    east_f1 = np.column_stack([e_top_1, e_top_0, e_bot_1])
    east_f2 = np.column_stack([e_top_0, e_bot_0, e_bot_1])
    
    faces = np.vstack([
        top_f1, top_f2,
        bot_f1, bot_f2,
        north_f1, north_f2,
        south_f1, south_f2,
        west_f1, west_f2,
        east_f1, east_f2
    ])
    
    write_binary_stl(out_path, verts, faces, title)

def generate_thailand_3d_models():
    t0 = time.time()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    out_dir = os.path.join(base_dir, "models_3d")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Load GIS Data
    geojson_path = os.path.join(data_dir, "thailand_provinces.geojson")
    dem_path = os.path.join(data_dir, "thailand_dem_mosaic.npz")
    
    if not os.path.exists(geojson_path) or not os.path.exists(dem_path):
        import subprocess
        subprocess.run(["python3", os.path.join(base_dir, "scripts", "download_thailand_gis.py")], check=True)
        
    print("Loading GIS data...")
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson = json.load(f)
        
    dem_data = np.load(dem_path)
    elev_raw = dem_data['elev']
    bounds = dem_data['bounds'] # [lon_min, lat_min, lon_max, lat_max]
    
    orig_lons = np.linspace(bounds[0], bounds[2], elev_raw.shape[1])
    orig_lats = np.linspace(bounds[3], bounds[1], elev_raw.shape[0])
    interp = RegularGridInterpolator((orig_lats, orig_lons), elev_raw, bounds_error=False, fill_value=0.0)
    
    # 2. Grid & Plinth Geometry (120mm x 200mm, dx=dy=0.45mm -> 266 x 444 pixels)
    dx = 0.45
    dy = 0.45
    plinth_w_mm = 120.0
    plinth_h_mm = 200.0
    W_px = int(round(plinth_w_mm / dx)) # 267 px
    H_px = int(round(plinth_h_mm / dy)) # 444 px
    
    print(f"Constructing Plinth Grid: {W_px} x {H_px} pixels ({plinth_w_mm:.1f} x {plinth_h_mm:.1f} mm)...")
    
    # Map placement inside plinth:
    # Width 82mm = ~182 px, Height 150mm = ~333 px
    map_w_px = int(round(82.0 / dx))
    map_h_px = int(round(150.0 / dy))
    map_x0 = (W_px - map_w_px) // 2
    map_x1 = map_x0 + map_w_px
    map_y0 = 54
    map_y1 = map_y0 + map_h_px
    
    lon_min, lon_max = 97.35, 105.65
    lat_min, lat_max = 5.63, 20.45
    
    # Base ocean height 2.0 mm
    z_plinth = np.full((H_px, W_px), 2.0, dtype=np.float32)
    
    # Chamfered plinth edges (outer 7 pixels taper down to 0.6 mm)
    for r in range(H_px):
        for c in range(W_px):
            dist_edge = min(r, H_px - 1 - r, c, W_px - 1 - c)
            if dist_edge < 7:
                z_plinth[r, c] = max(0.6, dist_edge * 0.28)
                
    # 3. Rasterize Thailand Mask & Province Boundaries
    th_mask = np.zeros((H_px, W_px), dtype=bool)
    border_mask = np.zeros((H_px, W_px), dtype=bool)
    
    for f in geojson['features']:
        geom = f['geometry']
        coords = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
        for poly in coords:
            ring = np.array(poly[0])
            lons, lats = ring[:, 0], ring[:, 1]
            cols = np.clip(np.round(map_x0 + (lons - lon_min) / (lon_max - lon_min) * (map_w_px - 1)).astype(int), 0, W_px - 1)
            rows = np.clip(np.round(map_y0 + (lat_max - lats) / (lat_max - lat_min) * (map_h_px - 1)).astype(int), 0, H_px - 1)
            rr, cc = polygon(rows, cols, shape=(H_px, W_px))
            th_mask[rr, cc] = True
            for i in range(len(rows) - 1):
                lr, lc = line(rows[i], cols[i], rows[i+1], cols[i+1])
                border_mask[lr, lc] = True
                
    # 4. Sample Real DEM Elevations
    map_rows = np.arange(map_y0, map_y1)
    map_cols = np.arange(map_x0, map_x1)
    grid_lats = lat_max - (map_rows - map_y0) / (map_h_px - 1) * (lat_max - lat_min)
    grid_lons = lon_min + (map_cols - map_x0) / (map_w_px - 1) * (lon_max - lon_min)
    GLAT, GLON = np.meshgrid(grid_lats, grid_lons, indexing='ij')
    
    sampled_elev = interp((GLAT, GLON))
    sampled_elev = np.clip(sampled_elev, 0.0, 2600.0)
    
    # Elevation scaling:
    # Base coastline shelf = 3.2 mm (stands 1.2mm above 2.0mm ocean)
    # Peak relief = 3.2 + (elev / 2565.0) * 11.8 mm -> Max 15.0 mm at Doi Inthanon
    elev_relief = 3.2 + (sampled_elev / 2565.0) * 11.8
    
    target_region = z_plinth[map_y0:map_y1, map_x0:map_x1]
    sub_mask = th_mask[map_y0:map_y1, map_x0:map_x1]
    target_region[sub_mask] = elev_relief[sub_mask]
    
    # Province borders: engrave -0.40 mm into the terrain
    target_borders = border_mask[map_y0:map_y1, map_x0:map_x1] & sub_mask
    target_region[target_borders] -= 0.40
    
    # 5. Render Embossed Typography & Compass Rose onto Plinth Base
    print("Rendering embossed Thai/English typography & badges...")
    img_text = Image.new('L', (W_px, H_px), color=0)
    draw = ImageDraw.Draw(img_text)
    
    # Fonts
    font_path_th = '/System/Library/Fonts/Supplemental/Thonburi.ttc'
    font_path_en = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
    
    try:
        f_title_th = ImageFont.truetype(font_path_th, 15)
        f_title_en = ImageFont.truetype(font_path_en, 10)
        f_sub_th   = ImageFont.truetype(font_path_th, 9)
        f_sub_en   = ImageFont.truetype(font_path_en, 8)
        f_coord    = ImageFont.truetype(font_path_en, 7)
    except Exception:
        f_title_th = f_title_en = f_sub_th = f_sub_en = f_coord = ImageFont.load_default()
        
    # Header
    draw.text((W_px // 2, 18), "ราชอาณาจักรไทย • THAILAND", font=f_title_th, fill=255, anchor='mm')
    draw.text((W_px // 2, 34), "TOPOGRAPHIC RELIEF MAP 2026", font=f_title_en, fill=220, anchor='mm')
    
    # Footer
    draw.text((W_px // 2, H_px - 26), "หน่วยวิจัยเกษตรดิจิทัล JC_AI_SciRBRU • มรภ.รำไพพรรณี", font=f_sub_th, fill=240, anchor='mm')
    draw.text((W_px // 2, H_px - 13), "DIGITAL AGRIPHYSICS • SCALE 1:10,000,000", font=f_sub_en, fill=200, anchor='mm')
    
    # Compass Rose at Top-Right
    cx, cy = W_px - 32, 68
    draw.line([(cx, cy - 16), (cx, cy + 16)], fill=255, width=2)
    draw.line([(cx - 16, cy), (cx + 16, cy)], fill=255, width=2)
    draw.polygon([(cx, cy - 16), (cx - 3, cy - 3), (cx, cy), (cx + 3, cy - 3)], fill=255)
    draw.polygon([(cx, cy + 16), (cx - 3, cy + 3), (cx, cy), (cx + 3, cy + 3)], fill=150)
    draw.polygon([(cx + 16, cy), (cx + 3, cy - 3), (cx, cy), (cx + 3, cy + 3)], fill=180)
    draw.polygon([(cx - 16, cy), (cx - 3, cy - 3), (cx, cy), (cx - 3, cy + 3)], fill=180)
    draw.text((cx, cy - 22), "N", font=f_title_en, fill=255, anchor='mm')
    
    # Scale Bar (100 km & 200 km)
    # At 1:10,000,000: 100 km = 10 mm = ~22 px
    sx, sy = 28, H_px - 44
    draw.line([(sx, sy), (sx + 44, sy)], fill=255, width=2)
    draw.line([(sx, sy - 3), (sx, sy + 3)], fill=255, width=2)
    draw.line([(sx + 22, sy - 3), (sx + 22, sy + 3)], fill=255, width=2)
    draw.line([(sx + 44, sy - 3), (sx + 44, sy + 3)], fill=255, width=2)
    draw.text((sx, sy - 7), "0", font=f_coord, fill=255, anchor='mm')
    draw.text((sx + 22, sy - 7), "100", font=f_coord, fill=255, anchor='mm')
    draw.text((sx + 44, sy - 7), "200 km", font=f_coord, fill=255, anchor='mm')
    
    # Coordinate Tick Marks
    # Latitude ticks on left margin
    for lat_val in [8, 12, 16, 20]:
        r_tick = int(round(map_y0 + (lat_max - lat_val) / (lat_max - lat_min) * (map_h_px - 1)))
        if 0 <= r_tick < H_px:
            draw.line([(12, r_tick), (16, r_tick)], fill=200, width=1)
            draw.text((8, r_tick), f"{lat_val}°N", font=f_coord, fill=200, anchor='rm')
            
    # Longitude ticks on bottom
    for lon_val in [98, 100, 102, 104]:
        c_tick = int(round(map_x0 + (lon_val - lon_min) / (lon_max - lon_min) * (map_w_px - 1)))
        if 0 <= c_tick < W_px:
            draw.line([(c_tick, map_y1 + 4), (c_tick, map_y1 + 8)], fill=200, width=1)
            draw.text((c_tick, map_y1 + 13), f"{lon_val}°E", font=f_coord, fill=200, anchor='mm')
            
    # Apply embossed text: only outside the country mask!
    text_arr = np.array(img_text).astype(np.float32) / 255.0
    text_emboss = text_arr * 0.90 # 0.90 mm embossed height
    text_active = (text_emboss > 0) & (~th_mask)
    z_plinth[text_active] += text_emboss[text_active]
    
    # 6. Export Model A: thailand_topographic_map_3d.stl
    stl_plinth_path = os.path.join(out_dir, "thailand_topographic_map_3d.stl")
    print(f"\n[1/3] Generating Master Plinth STL: {stl_plinth_path}...")
    mesh_heightfield_to_stl(z_plinth, dx, dy, stl_plinth_path, title="Thailand_Topographic_Plinth_RBRU")
    
    # 7. Export Model B: Standalone Country Cutout (thailand_country_standalone_3d.stl)
    stl_standalone_path = os.path.join(out_dir, "thailand_country_standalone_3d.stl")
    print(f"\n[2/3] Generating Standalone Country Cutout STL: {stl_standalone_path}...")
    
    # Sub-grid covering only the country
    country_mask = th_mask[map_y0:map_y1, map_x0:map_x1]
    country_elev = elev_relief # in [3.2, 15.0] mm
    
    # Create 3D volumetric grid for Marching Cubes
    # Z from 0 to 16 mm with step dz = 0.5 mm
    dz = 0.5
    nz = int(round(16.5 / dz))
    vol = np.zeros((map_h_px, map_w_px, nz), dtype=np.float32)
    
    z_levels = np.arange(nz) * dz
    for k, z_val in enumerate(z_levels):
        layer = country_mask & (country_elev >= z_val)
        vol[layer, k] = 1.0
        
    # Pad volume with 0 so the boundaries close neatly
    vol_padded = np.pad(vol, 1, mode='constant', constant_values=0)
    verts_mc, faces_mc, _, _ = measure.marching_cubes(vol_padded, level=0.5, spacing=(dy, dx, dz))
    
    # Map Marching Cubes coordinates to real-world mm:
    # Axis 0 is row (North to South), Axis 1 is col (West to East), Axis 2 is Z
    row_coords = verts_mc[:, 0]
    col_coords = verts_mc[:, 1]
    z_coords   = verts_mc[:, 2]
    
    X_mm = (col_coords - 1.0) * dx
    Y_mm = (map_h_px - (row_coords - 1.0)) * dy
    Z_mm = (z_coords - 1.0) * dz
    
    # Center X and Y around (0, 0), and place bottom exactly on Z = 0.0
    X_mm -= (X_mm.min() + X_mm.max()) / 2.0
    Y_mm -= (Y_mm.min() + Y_mm.max()) / 2.0
    Z_mm -= Z_mm.min()
    
    # Scale standalone model by 2.0x so it has optimal desktop display proportions (~74 x 135 x 12.5 mm)
    scale_standalone = 2.0
    verts_final = np.column_stack([X_mm * scale_standalone, Y_mm * scale_standalone, Z_mm * scale_standalone])
    
    write_binary_stl(stl_standalone_path, verts_final, faces_mc, title="Thailand_Country_Standalone_RBRU")
    
    # 8. Export 16-Bit Grayscale Heightmap for OpenSCAD / Blender
    png_path = os.path.join(out_dir, "thailand_relief.png")
    print(f"\n[3/3] Exporting 16-bit Heightmap: {png_path}...")
    z_norm = (z_plinth - z_plinth.min()) / (z_plinth.max() - z_plinth.min())
    img_16bit = (z_norm * 65535.0).astype(np.uint16)
    Image.fromarray(img_16bit).save(png_path)
    print(f"[OK] Saved {png_path} ({os.path.getsize(png_path)/1024:.1f} KB)")
    
    # 9. Create OpenSCAD Parametric Script
    scad_path = os.path.join(out_dir, "thailand_map.scad")
    scad_content = f"""// ==============================================================================
// Kingdom of Thailand - 3D Topographic Model
// Digital Agriphysics & AI Research Unit (JC_AI_SciRBRU)
// Department of Physics, Faculty of Science and Technology,
// Rambhai Barni Rajabhat University (RBRU)
// ==============================================================================

// --- User Parameters ---
model_scale_x       = 1.0;   // Scaling factor X
model_scale_y       = 1.0;   // Scaling factor Y
relief_multiplier   = 1.0;   // Vertical terrain exaggeration (1.0x - 3.0x)
base_pedestal_h     = 2.0;   // Additional base thickness (mm)

// Mode Selection: "plinth" or "standalone"
mode = "plinth"; 

module thailand_display_plinth() {{
    scale([model_scale_x, model_scale_y, relief_multiplier])
        import("thailand_topographic_map_3d.stl");
}}

module thailand_standalone_country() {{
    scale([model_scale_x, model_scale_y, relief_multiplier])
        import("thailand_country_standalone_3d.stl");
}}

if (mode == "plinth") {{
    thailand_display_plinth();
}} else if (mode == "standalone") {{
    thailand_standalone_country();
}}
"""
    with open(scad_path, 'w', encoding='utf-8') as f:
        f.write(scad_content)
    print(f"[OK] Generated {scad_path}")
    
    print(f"\n[SUCCESS] All 3D Thailand models successfully created in {time.time() - t0:.2f}s!")

if __name__ == '__main__':
    generate_thailand_3d_models()
