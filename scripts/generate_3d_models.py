#!/usr/bin/env python3
"""
NPK Spectrometer 2026 - 3D STL Model Generator
Digital Agriphysics & AI Research Unit (JC_AI_SciRBRU)
Department of Physics, Faculty of Science and Technology,
Rambhai Barni Rajabhat University (RBRU)

Generates research-grade, watertight, 3D-printable binary STL files:
1. models_3d/cuvette_optical_chamber.stl
2. models_3d/light_tight_lid.stl
"""

import os
import struct
import numpy as np
from skimage import measure

def write_binary_stl(filename, verts, faces):
    """Writes triangle mesh to standard binary STL format."""
    num_faces = len(faces)
    with open(filename, 'wb') as f:
        # 80-byte header
        header = f"NPK_Spectrometer_2026_JC_AI_SciRBRU_{os.path.basename(filename)}".encode('ascii')
        header = header.ljust(80, b' ')[:80]
        f.write(header)
        
        # 4-byte face count
        f.write(struct.pack('<I', num_faces))
        
        # Calculate face normals
        v0 = verts[faces[:, 0]]
        v1 = verts[faces[:, 1]]
        v2 = verts[faces[:, 2]]
        normals = np.cross(v1 - v0, v2 - v0)
        norm_lens = np.linalg.norm(normals, axis=1, keepdims=True)
        norm_lens[norm_lens == 0] = 1.0
        normals = normals / norm_lens
        
        # Pack records: 12 floats (normal + 3 vertices) + 1 uint16 (attribute=0)
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
        
    print(f"[OK] Generated {filename} ({num_faces:,} triangles, {os.path.getsize(filename)/1024:.1f} KB)")

# --- Signed Distance Functions (SDF) ---
def sdf_box(X, Y, Z, bx, by, bz, cx=0, cy=0, cz=0):
    """SDF for axis-aligned box centered at (cx, cy, cz) with half-extents (bx, by, bz)"""
    dx = np.abs(X - cx) - bx
    dy = np.abs(Y - cy) - by
    dz = np.abs(Z - cz) - bz
    
    mc = np.maximum(dx, np.maximum(dy, dz))
    d_out = np.sqrt(np.maximum(dx, 0.0)**2 + np.maximum(dy, 0.0)**2 + np.maximum(dz, 0.0)**2)
    d_in = np.minimum(mc, 0.0)
    return d_out + d_in

def sdf_cylinder_x(X, Y, Z, r, l, cx=0, cy=0, cz=0):
    """SDF for cylinder along X axis"""
    dyz = np.sqrt((Y - cy)**2 + (Z - cz)**2) - r
    dx = np.abs(X - cx) - l
    mc = np.maximum(dyz, dx)
    d_out = np.sqrt(np.maximum(dyz, 0.0)**2 + np.maximum(dx, 0.0)**2)
    d_in = np.minimum(mc, 0.0)
    return d_out + d_in

def sdf_cylinder_z(X, Y, Z, r, h, cx=0, cy=0, cz=0):
    """SDF for cylinder along Z axis"""
    dxy = np.sqrt((X - cx)**2 + (Y - cy)**2) - r
    dz = np.abs(Z - cz) - h
    mc = np.maximum(dxy, dz)
    d_out = np.sqrt(np.maximum(dxy, 0.0)**2 + np.maximum(dz, 0.0)**2)
    d_in = np.minimum(mc, 0.0)
    return d_out + d_in

def generate_optical_chamber_stl(filepath, res=0.30):
    """Generates the optical chamber mesh with cuvette slot, apertures, and flange."""
    print(f"Generating Optical Chamber mesh at resolution {res} mm...")
    
    # Domain bounds (mm)
    xmin, xmax = -34.0, 34.0
    ymin, ymax = -26.0, 26.0
    zmin, zmax = -1.0, 42.0
    
    x = np.arange(xmin, xmax + res, res)
    y = np.arange(ymin, ymax + res, res)
    z = np.arange(zmin, zmax + res, res)
    
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    
    # 1. Base Flange: 64 x 48 x 3 mm (centered, z in [0, 3])
    d_flange = sdf_box(X, Y, Z, bx=32.0 - 2.0, by=24.0 - 2.0, bz=1.5, cz=1.5) - 2.0
    
    # 2. Main Chamber Body: 46 x 30 x 33 mm (z in [3, 36])
    d_body = sdf_box(X, Y, Z, bx=23.0 - 2.0, by=15.0 - 2.0, bz=16.5 - 2.0, cz=19.5) - 2.0
    
    # 3. Top Labyrinth Baffle Lip: 41.6 x 25.6 x 3.5 mm (z in [36, 39.5])
    d_baffle = sdf_box(X, Y, Z, bx=20.8 - 1.5, by=12.8 - 1.5, bz=1.75 - 1.5, cz=37.75) - 1.5
    
    # Union of external solid bodies: min(flange, body, baffle)
    solid = np.minimum(d_flange, np.minimum(d_body, d_baffle))
    
    # 4. Cuvette Well: 12.75 x 12.75 mm from z = 3.0 upwards (open top)
    d_cuvette = sdf_box(X, Y, Z, bx=6.375, by=6.375, bz=22.0, cz=25.0)
    
    # 5. Coaxial Optical Aperture: dia = 3.0 mm (r = 1.5 mm), optical axis at z = 18.0 mm
    d_aperture = sdf_cylinder_x(X, Y, Z, r=1.5, l=25.0, cz=18.0)
    
    # 6. LED Pocket (-X side): 21 x 21 x 3.2 mm centered at z = 18.0
    d_led_pocket = sdf_box(X, Y, Z, bx=1.7, by=10.5, bz=10.5, cx=-21.5, cz=18.0)
    
    # 7. TCS34725 Pocket (+X side): 21 x 21 x 3.2 mm centered at z = 18.0
    d_sensor_pocket = sdf_box(X, Y, Z, bx=1.7, by=10.5, bz=10.5, cx=21.5, cz=18.0)
    
    # 8. Mounting Holes on Flange (4x M3 at pitch 54 x 38 mm)
    d_hole1 = sdf_cylinder_z(X, Y, Z, r=1.7, h=5.0, cx=-27.0, cy=-19.0, cz=1.5)
    d_hole2 = sdf_cylinder_z(X, Y, Z, r=1.7, h=5.0, cx= 27.0, cy=-19.0, cz=1.5)
    d_hole3 = sdf_cylinder_z(X, Y, Z, r=1.7, h=5.0, cx= 27.0, cy= 19.0, cz=1.5)
    d_hole4 = sdf_cylinder_z(X, Y, Z, r=1.7, h=5.0, cx=-27.0, cy= 19.0, cz=1.5)
    d_flange_holes = np.minimum(np.minimum(d_hole1, d_hole2), np.minimum(d_hole3, d_hole4))
    
    # 9. Sensor M2.5 pilot screw holes
    d_s_screw1 = sdf_cylinder_x(X, Y, Z, r=1.1, l=3.5, cx=20.0, cy=-7.5, cz=18.0)
    d_s_screw2 = sdf_cylinder_x(X, Y, Z, r=1.1, l=3.5, cx=20.0, cy= 7.5, cz=18.0)
    d_led_screw1 = sdf_cylinder_x(X, Y, Z, r=1.1, l=3.5, cx=-20.0, cy=-7.5, cz=18.0)
    d_led_screw2 = sdf_cylinder_x(X, Y, Z, r=1.1, l=3.5, cx=-20.0, cy= 7.5, cz=18.0)
    d_side_screws = np.minimum(np.minimum(d_s_screw1, d_s_screw2), np.minimum(d_led_screw1, d_led_screw2))
    
    # CSG Subtraction: max(solid, -cavity)
    cavities = np.minimum(d_cuvette, np.minimum(d_aperture, np.minimum(d_led_pocket, d_sensor_pocket)))
    cavities = np.minimum(cavities, np.minimum(d_flange_holes, d_side_screws))
    
    final_sdf = np.maximum(solid, -cavities)
    
    # Run Marching Cubes
    verts, faces, normals, values = measure.marching_cubes(final_sdf, level=0.0, spacing=(res, res, res))
    verts[:, 0] += xmin
    verts[:, 1] += ymin
    verts[:, 2] += zmin
    
    write_binary_stl(filepath, verts, faces)

def generate_light_tight_lid_stl(filepath, res=0.30):
    """Generates the light-tight labyrinth baffle lid with grip handle."""
    print(f"Generating Light-Tight Lid mesh at resolution {res} mm...")
    
    # Domain bounds (mm)
    xmin, xmax = -26.0, 26.0
    ymin, ymax = -18.0, 18.0
    zmin, zmax = -1.0, 38.0
    
    x = np.arange(xmin, xmax + res, res)
    y = np.arange(ymin, ymax + res, res)
    z = np.arange(zmin, zmax + res, res)
    
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    
    # 1. Main Lid Outer Shell: 48 x 32 x 24 mm (z in [0, 24])
    d_lid_body = sdf_box(X, Y, Z, bx=24.0 - 2.5, by=16.0 - 2.5, bz=12.0 - 2.5, cz=12.0) - 2.5
    
    # 2. Top Grip Handle: 18 x 8 x 12 mm (z in [24, 36])
    d_handle = sdf_box(X, Y, Z, bx=9.0 - 2.0, by=4.0 - 2.0, bz=6.0 - 2.0, cz=30.0) - 2.0
    
    solid = np.minimum(d_lid_body, d_handle)
    
    # 3. Bottom Skirt Cavity: 46.5 x 30.5 mm, depth 5.0 mm (z in [0, 5.0])
    d_skirt = sdf_box(X, Y, Z, bx=23.25, by=15.25, bz=3.0, cz=2.5)
    
    # 4. Labyrinth Step Cavity: 42.1 x 26.1 mm, height 3.8 mm (z in [5.0, 8.8])
    d_step = sdf_box(X, Y, Z, bx=21.05, by=13.05, bz=2.4, cz=6.9)
    
    # 5. Cuvette Clearance Pocket: 14.0 x 14.0 mm, height 12.0 mm (z in [8.8, 20.5])
    d_cuvette_head = sdf_box(X, Y, Z, bx=7.0, by=7.0, bz=6.5, cz=14.7)
    
    cavities = np.minimum(d_skirt, np.minimum(d_step, d_cuvette_head))
    final_sdf = np.maximum(solid, -cavities)
    
    verts, faces, normals, values = measure.marching_cubes(final_sdf, level=0.0, spacing=(res, res, res))
    verts[:, 0] += xmin
    verts[:, 1] += ymin
    verts[:, 2] += zmin
    
    write_binary_stl(filepath, verts, faces)

if __name__ == '__main__':
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models_3d", "spectrometer", "v4_chamber")
    os.makedirs(out_dir, exist_ok=True)
    
    chamber_stl = os.path.join(out_dir, "cuvette_optical_chamber.stl")
    lid_stl = os.path.join(out_dir, "light_tight_lid.stl")
    
    generate_optical_chamber_stl(chamber_stl, res=0.30)
    generate_light_tight_lid_stl(lid_stl, res=0.30)
    print("\n[SUCCESS] All 3D STL files successfully generated!")
