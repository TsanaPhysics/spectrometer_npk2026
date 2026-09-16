#!/usr/bin/env python3
"""
SpectorV5-Pro: Precision 3D Model Generator using Marching Cubes SDF
Designed according to: spectrometer-3d-chassis-architect
JC_AI_SciRBRU, Rambhai Barni Rajabhat University (RBRU)

Generates:
1. models_3d/spector_v5_workstation.stl (Main integrated console workstation)
2. models_3d/spector_v5_lid.stl (Double-stepped labyrinth seal cap)
"""

import os
import time
import struct
import numpy as np
from skimage import measure

def write_binary_stl(filename, verts, faces):
    """Writes triangle mesh to standard binary STL format."""
    num_faces = len(faces)
    with open(filename, 'wb') as f:
        header = f"SpectorV5_Pro_JC_AI_SciRBRU_{os.path.basename(filename)}".encode('ascii')
        header = header.ljust(80, b' ')[:80]
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

def sdf_box(X, Y, Z, bx, by, bz, cx=0.0, cy=0.0, cz=0.0):
    """SDF for axis-aligned box with half-extents (bx, by, bz) centered at (cx, cy, cz)"""
    dx = np.abs(X - cx) - bx
    dy = np.abs(Y - cy) - by
    dz = np.abs(Z - cz) - bz
    mc = np.maximum(dx, np.maximum(dy, dz))
    d_out = np.sqrt(np.maximum(dx, 0.0)**2 + np.maximum(dy, 0.0)**2 + np.maximum(dz, 0.0)**2)
    d_in = np.minimum(mc, 0.0)
    return d_out + d_in

def sdf_rounded_box_xy(X, Y, Z, bx, by, bz, r=3.0, cx=0.0, cy=0.0, cz=0.0):
    """SDF for box rounded in XY plane with radius r"""
    dx = np.abs(X - cx) - (bx - r)
    dy = np.abs(Y - cy) - (by - r)
    dz = np.abs(Z - cz) - bz
    dxy = np.sqrt(np.maximum(dx, 0.0)**2 + np.maximum(dy, 0.0)**2) - r
    dxy_in = np.minimum(np.maximum(dx, dy), 0.0)
    d_xy = dxy + dxy_in
    
    mc = np.maximum(d_xy, dz)
    d_out = np.sqrt(np.maximum(d_xy, 0.0)**2 + np.maximum(dz, 0.0)**2)
    d_in = np.minimum(mc, 0.0)
    return d_out + d_in

def sdf_cylinder_x(X, Y, Z, r, l, cx=0.0, cy=0.0, cz=0.0):
    """SDF for cylinder along X axis"""
    dyz = np.sqrt((Y - cy)**2 + (Z - cz)**2) - r
    dx = np.abs(X - cx) - l
    mc = np.maximum(dyz, dx)
    d_out = np.sqrt(np.maximum(dyz, 0.0)**2 + np.maximum(dx, 0.0)**2)
    d_in = np.minimum(mc, 0.0)
    return d_out + d_in

def sdf_cylinder_z(X, Y, Z, r, h, cx=0.0, cy=0.0, cz=0.0):
    """SDF for cylinder along Z axis"""
    dxy = np.sqrt((X - cx)**2 + (Y - cy)**2) - r
    dz = np.abs(Z - cz) - h
    mc = np.maximum(dxy, dz)
    d_out = np.sqrt(np.maximum(dxy, 0.0)**2 + np.maximum(dz, 0.0)**2)
    d_in = np.minimum(mc, 0.0)
    return d_out + d_in

def generate_spector_v5_workstation(filepath, res=0.45):
    """
    Generates SpectorV5-Pro Master Console Workstation Body:
    - 96 x 120 x 81.5 mm
    - 22 deg tilted front console deck for Wio Terminal
    - Rear flat deck with optical well, labyrinth seal rim
    - Collinear beam path, 3mm apertures, sensor pockets, battery cavity
    """
    t0 = time.time()
    print(f"\n[1/2] Computing SpectorV5 Workstation SDF at res = {res} mm...")
    
    xmin, xmax = -50.0, 50.0
    ymin, ymax = -62.0, 62.0
    zmin, zmax = -2.0, 84.0
    
    x = np.arange(xmin, xmax + res, res, dtype=np.float32)
    y = np.arange(ymin, ymax + res, res, dtype=np.float32)
    z = np.arange(zmin, zmax + res, res, dtype=np.float32)
    
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    
    # 1. Main Base Envelope: 96mm x 120mm, R=4mm fillet, up to 78mm
    d_base_shell = sdf_rounded_box_xy(X, Y, Z, bx=48.0, by=60.0, bz=39.0, r=4.0, cz=39.0)
    
    # 2. Wedge Incline Cutting Plane:
    # Front is 36mm high at Y = -60. Rear flat deck is 78mm high starting at Y = 20.
    # For Y in [-60, 20]: slope = (78 - 36) / (20 - (-60)) = 42 / 80 = 0.525
    # Normal to cutting plane: vector (0, -0.525, 1) normalized
    slope = 0.525
    z_deck = np.where(Y <= 20.0, 36.0 + (Y + 60.0) * slope, 78.0)
    d_top_plane = Z - z_deck
    
    # Wedge solid = intersection of base shell and top profile
    d_wedge = np.maximum(d_base_shell, d_top_plane)
    
    # 3. Raised Labyrinth Baffle Rim on rear top deck:
    # Outer 36 x 36 mm, R=2mm, height 3.5mm (Z from 78.0 to 81.5), centered at Y = 35.0
    d_baffle_rim = sdf_rounded_box_xy(X, Y, Z, bx=18.0, by=18.0, bz=1.75, r=2.0, cy=35.0, cz=79.75)
    
    # Positive chassis body:
    solid = np.minimum(d_wedge, d_baffle_rim)
    
    # --- NEGATIVE CAVITIES ---
    # A. Cuvette Well: 12.75 x 12.75 mm, Z from 18.0 upwards through top
    d_cuvette = sdf_box(X, Y, Z, bx=6.375, by=6.375, bz=35.0, cy=35.0, cz=51.0)
    # Cuvette Lead-in Chamfer: funnel at top
    d_cuvette_lead = sdf_cylinder_z(X, Y, Z, r=8.5, h=2.5, cy=35.0, cz=80.5)
    
    # B. Coaxial Optical Aperture Tunnel (3.0mm diameter, along X-axis at Y=35, Z=33)
    d_aperture = sdf_cylinder_x(X, Y, Z, r=1.5, l=52.0, cy=35.0, cz=33.0)
    
    # C. Left LED Pocket (Grove WS2812B at -X side): 4mm deep, 21 x 21 mm, M2.5 screws
    d_led_pocket = sdf_box(X, Y, Z, bx=2.5, by=10.5, bz=10.5, cx=-46.5, cy=35.0, cz=33.0)
    d_led_screw1 = sdf_cylinder_x(X, Y, Z, r=1.25, l=4.0, cx=-44.0, cy=27.5, cz=33.0)
    d_led_screw2 = sdf_cylinder_x(X, Y, Z, r=1.25, l=4.0, cx=-44.0, cy=42.5, cz=33.0)
    
    # D. Right Sensor Pocket (Adafruit TCS34725 at +X side): 4mm deep, 21 x 21 mm, M2.5 screws
    d_sensor_pocket = sdf_box(X, Y, Z, bx=2.5, by=10.5, bz=10.5, cx=46.5, cy=35.0, cz=33.0)
    d_sensor_screw1 = sdf_cylinder_x(X, Y, Z, r=1.25, l=4.0, cx=44.0, cy=27.5, cz=33.0)
    d_sensor_screw2 = sdf_cylinder_x(X, Y, Z, r=1.25, l=4.0, cx=44.0, cy=42.5, cz=33.0)
    
    # E. Wio Terminal Console Cradle (Rotated by theta = 27.7 degrees along incline)
    # Cradle center: Y_c = -22.0, Z_c = 36.0 + (-22.0 + 60.0) * 0.525 = 55.95
    theta = np.arctan(slope) # ~27.7 degrees
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    
    Y_rel = Y - (-22.0)
    Z_rel = Z - 55.95
    Y_rot = Y_rel * cos_t + Z_rel * sin_t
    Z_rot = -Y_rel * sin_t + Z_rel * cos_t
    
    # Wio Terminal Body: 72.8 x 57.8 x 13.0 mm (recessed into deck)
    dx_w = np.abs(X) - 36.4
    dy_w = np.abs(Y_rot) - 28.9
    dz_w = np.abs(Z_rot + 6.0) - 7.0
    d_wio_body = np.maximum(dx_w, np.maximum(dy_w, dz_w))
    
    # LCD Screen Window: 50.0 x 38.0 mm
    dx_s = np.abs(X) - 25.0
    dy_s = np.abs(Y_rot - 2.0) - 19.0
    dz_s = np.abs(Z_rot) - 15.0
    d_wio_screen = np.maximum(dx_s, np.maximum(dy_s, dz_s))
    
    # 5-way Analog Joystick clearance hole: Dia = 9.0 mm
    dxy_j = np.sqrt((X - 24.5)**2 + (Y_rot + 16.5)**2) - 4.5
    d_joystick = np.maximum(dxy_j, dz_s)
    
    # Buttons A, B, C clearance cutout
    dx_b = np.abs(X) - 24.0
    dy_b = np.abs(Y_rot - 26.5) - 4.0
    d_buttons = np.maximum(dx_b, np.maximum(dy_b, dz_s))
    
    d_console = np.minimum(d_wio_body, np.minimum(d_wio_screen, np.minimum(d_joystick, d_buttons)))
    
    # F. Cable Routing Channels (Left & Right Grove Conduits)
    d_conduit_l = sdf_box(X, Y, Z, bx=4.0, by=30.0, bz=4.0, cx=-26.0, cy=10.0, cz=20.0)
    d_conduit_r = sdf_box(X, Y, Z, bx=4.0, by=30.0, bz=4.0, cx= 26.0, cy=10.0, cz=20.0)
    
    # G. Li-Po Battery Cavity (Under console deck): 80 x 50 x 22 mm
    d_battery_bay = sdf_rounded_box_xy(X, Y, Z, bx=40.0, by=25.0, bz=11.0, r=3.0, cy=-25.0, cz=10.0)
    
    # H. MicroSD and USB-C Side Access Slots
    d_usbc_port = sdf_box(X, Y, Z, bx=6.0, by=8.0, bz=4.0, cx=-46.0, cy=-26.0, cz=34.0)
    d_sd_port   = sdf_box(X, Y, Z, bx=6.0, by=8.0, bz=2.5, cx= 46.0, cy=-26.0, cz=34.0)
    
    # I. 4x M3 Rubber Foot Recesses
    d_foot1 = sdf_cylinder_z(X, Y, Z, r=5.0, h=1.5, cx=-38.0, cy=-50.0, cz=0.5)
    d_foot2 = sdf_cylinder_z(X, Y, Z, r=5.0, h=1.5, cx= 38.0, cy=-50.0, cz=0.5)
    d_foot3 = sdf_cylinder_z(X, Y, Z, r=5.0, h=1.5, cx=-38.0, cy= 50.0, cz=0.5)
    d_foot4 = sdf_cylinder_z(X, Y, Z, r=5.0, h=1.5, cx= 38.0, cy= 50.0, cz=0.5)
    d_feet = np.minimum(np.minimum(d_foot1, d_foot2), np.minimum(d_foot3, d_foot4))
    
    # Combine all cavities
    cavities = np.minimum(d_cuvette, np.minimum(d_cuvette_lead, d_aperture))
    cavities = np.minimum(cavities, np.minimum(d_led_pocket, np.minimum(d_led_screw1, d_led_screw2)))
    cavities = np.minimum(cavities, np.minimum(d_sensor_pocket, np.minimum(d_sensor_screw1, d_sensor_screw2)))
    cavities = np.minimum(cavities, d_console)
    cavities = np.minimum(cavities, np.minimum(d_conduit_l, d_conduit_r))
    cavities = np.minimum(cavities, d_battery_bay)
    cavities = np.minimum(cavities, np.minimum(d_usbc_port, d_sd_port))
    cavities = np.minimum(cavities, d_feet)
    
    # Final CSG Boolean Difference:
    final_sdf = np.maximum(solid, -cavities)
    
    print("     Extracting iso-surface using Marching Cubes...")
    verts, faces, normals, values = measure.marching_cubes(final_sdf, level=0.0, spacing=(res, res, res))
    verts[:, 0] += xmin
    verts[:, 1] += ymin
    verts[:, 2] += zmin
    
    write_binary_stl(filepath, verts, faces)
    print(f"     Finished in {time.time() - t0:.2f}s")

def generate_spector_v5_lid(filepath, res=0.30):
    """
    Generates SpectorV5 Double-Stepped Labyrinth Seal Lid:
    - 42 x 42 x 28 mm
    - Ergonomic top ribbed handle
    - Tier 1 outer rim cavity (36.5 x 36.5 mm, depth 4.2mm)
    - Tier 2 labyrinth step (24 x 24 mm, height 3.0mm)
    - Tier 3 cuvette clearance chamber (14 x 14 mm, height 10.0mm)
    - Finger flutes for easy one-handed operation
    """
    t0 = time.time()
    print(f"\n[2/2] Computing SpectorV5 Labyrinth Lid SDF at res = {res} mm...")
    
    xmin, xmax = -24.0, 24.0
    ymin, ymax = -24.0, 24.0
    zmin, zmax = -1.0, 32.0
    
    x = np.arange(xmin, xmax + res, res, dtype=np.float32)
    y = np.arange(ymin, ymax + res, res, dtype=np.float32)
    z = np.arange(zmin, zmax + res, res, dtype=np.float32)
    
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    
    # 1. Main Lid Shell: 42 x 42 x 18 mm (Z in [0, 18])
    d_lid_body = sdf_rounded_box_xy(X, Y, Z, bx=21.0, by=21.0, bz=9.0, r=4.0, cz=9.0)
    
    # 2. Top Ergonomic Grip Handle: 30 x 12 x 10 mm (Z in [18, 28])
    d_handle = sdf_rounded_box_xy(X, Y, Z, bx=15.0, by=6.0, bz=5.0, r=3.0, cz=23.0)
    
    # Ridges on handle for grip
    d_ridges = 999.0
    for gx in [-10.0, -5.0, 0.0, 5.0, 10.0]:
        dr = sdf_cylinder_x(X, Y, Z, r=1.0, l=1.2, cx=gx, cy=0.0, cz=28.0)
        d_ridges = np.minimum(d_ridges, dr)
        
    solid = np.minimum(np.minimum(d_lid_body, d_handle), d_ridges)
    
    # 3. Cavities:
    # Tier 1 Outer Labyrinth Rim Cavity: 36.5 x 36.5 mm, depth 4.2 mm (Z in [0, 4.2])
    d_tier1 = sdf_rounded_box_xy(X, Y, Z, bx=18.25, by=18.25, bz=2.15, r=2.5, cz=2.05)
    
    # Tier 2 Intermediate Light Baffle Cavity: 24.0 x 24.0 mm, height 3.0 mm (Z in [4.2, 7.2])
    d_tier2 = sdf_rounded_box_xy(X, Y, Z, bx=12.0, by=12.0, bz=1.6, r=2.0, cz=5.7)
    
    # Tier 3 Cuvette Top Clearance Chamber: 14.0 x 14.0 mm, height 10.0 mm (Z in [7.2, 17.2])
    d_tier3 = sdf_rounded_box_xy(X, Y, Z, bx=7.0, by=7.0, bz=5.1, r=1.5, cz=12.2)
    
    # Ergonomic Finger Flutes on side walls
    d_flute1 = sdf_cylinder_x(X, Y, Z, r=5.5, l=2.0, cx=-21.0, cy=0.0, cz=9.0)
    d_flute2 = sdf_cylinder_x(X, Y, Z, r=5.5, l=2.0, cx= 21.0, cy=0.0, cz=9.0)
    
    cavities = np.minimum(d_tier1, np.minimum(d_tier2, d_tier3))
    cavities = np.minimum(cavities, np.minimum(d_flute1, d_flute2))
    
    final_sdf = np.maximum(solid, -cavities)
    
    print("     Extracting iso-surface using Marching Cubes...")
    verts, faces, normals, values = measure.marching_cubes(final_sdf, level=0.0, spacing=(res, res, res))
    verts[:, 0] += xmin
    verts[:, 1] += ymin
    verts[:, 2] += zmin
    
    write_binary_stl(filepath, verts, faces)
    print(f"     Finished in {time.time() - t0:.2f}s")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    models_dir = os.path.join(root_dir, "models_3d", "spectrometer", "v5_workstation")
    os.makedirs(models_dir, exist_ok=True)
    
    ws_stl = os.path.join(models_dir, "spector_v5_workstation.stl")
    lid_stl = os.path.join(models_dir, "spector_v5_lid.stl")
    
    generate_spector_v5_workstation(ws_stl, res=0.50)
    generate_spector_v5_lid(lid_stl, res=0.35)
    
    print("\n[SUCCESS] SpectorV5-Pro 3D Models generated successfully!")
