#!/usr/bin/env python3
"""
==============================================================================
🎨 QUANTUM PHYSICISTS CHIBI FIGURINE GENERATOR (PIXAR / GHIBLI 3D STYLE)
🔬 Albert Einstein • Max Planck • Werner Heisenberg • Erwin Schrödinger
🏛️ หน่วยวิจัยฟิสิกส์เกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics) มรภ.รำไพพรรณี
==============================================================================
Creates 100% Watertight Manifold 3D STL models using Signed Distance Fields (SDF)
and Scikit-Image Marching Cubes.
"""

import os
import sys
import time
import struct
import numpy as np
from skimage import measure

# ------------------------------------------------------------------------------
# 1. VECTORIZED SDF PRIMITIVES & OPERATORS
# ------------------------------------------------------------------------------

def sdf_sphere(X, Y, Z, cx, cy, cz, r):
    return np.sqrt((X - cx)**2 + (Y - cy)**2 + (Z - cz)**2) - r

def sdf_ellipsoid(X, Y, Z, cx, cy, cz, rx, ry, rz):
    dx = (X - cx) / rx
    dy = (Y - cy) / ry
    dz = (Z - cz) / rz
    d = np.sqrt(dx**2 + dy**2 + dz**2)
    k0 = np.min([rx, ry, rz])
    return (d - 1.0) * k0

def sdf_box(X, Y, Z, cx, cy, cz, hx, hy, hz):
    dx = np.abs(X - cx) - hx
    dy = np.abs(Y - cy) - hy
    dz = np.abs(Z - cz) - hz
    ox = np.maximum(dx, 0.0)
    oy = np.maximum(dy, 0.0)
    oz = np.maximum(dz, 0.0)
    outside = np.sqrt(ox**2 + oy**2 + oz**2)
    inside = np.minimum(np.maximum(dx, np.maximum(dy, dz)), 0.0)
    return outside + inside

def sdf_segment(X, Y, Z, ax, ay, az, bx, by, bz, r):
    abx = bx - ax
    aby = by - ay
    abz = bz - az
    pax = X - ax
    pay = Y - ay
    paz = Z - az
    ab2 = abx**2 + aby**2 + abz**2
    if ab2 < 1e-8:
        return np.sqrt(pax**2 + pay**2 + paz**2) - r
    h = np.clip((pax * abx + pay * aby + paz * abz) / ab2, 0.0, 1.0)
    dx = pax - abx * h
    dy = pay - aby * h
    dz = paz - abz * h
    return np.sqrt(dx**2 + dy**2 + dz**2) - r

def sdf_cylinder_z(X, Y, Z, cx, cy, z_min, z_max, r):
    d_xy = np.sqrt((X - cx)**2 + (Y - cy)**2) - r
    d_z = np.maximum(z_min - Z, Z - z_max)
    outside = np.sqrt(np.maximum(d_xy, 0.0)**2 + np.maximum(d_z, 0.0)**2)
    inside = np.minimum(np.maximum(d_xy, d_z), 0.0)
    return outside + inside

def sdf_torus(X, Y, Z, cx, cy, cz, R_maj, r_min, plane='xy'):
    if plane == 'xy':
        q_x = np.sqrt((X - cx)**2 + (Y - cy)**2) - R_maj
        q_y = Z - cz
    elif plane == 'xz':
        q_x = np.sqrt((X - cx)**2 + (Z - cz)**2) - R_maj
        q_y = Y - cy
    else: # 'yz'
        q_x = np.sqrt((Y - cy)**2 + (Z - cz)**2) - R_maj
        q_y = X - cx
    return np.sqrt(q_x**2 + q_y**2) - r_min

def sdf_tilted_torus(X, Y, Z, cx, cy, cz, R_maj, r_min, tilt_x_deg=30.0, tilt_z_deg=20.0):
    # Coordinate transformation for tilted torus
    rad_x = np.radians(tilt_x_deg)
    rad_z = np.radians(tilt_z_deg)
    # Translate
    px = X - cx
    py = Y - cy
    pz = Z - cz
    # Rotate around X
    py1 = py * np.cos(rad_x) - pz * np.sin(rad_x)
    pz1 = py * np.sin(rad_x) + pz * np.cos(rad_x)
    # Rotate around Z
    px2 = px * np.cos(rad_z) - py1 * np.sin(rad_z)
    py2 = px * np.sin(rad_z) + py1 * np.cos(rad_z)
    
    q_x = np.sqrt(px2**2 + py2**2) - R_maj
    q_y = pz1
    return np.sqrt(q_x**2 + q_y**2) - r_min

def smin(d1, d2, k=2.0):
    """Smooth minimum (smooth boolean union)"""
    h = np.clip(0.5 + 0.5 * (d2 - d1) / np.maximum(k, 1e-6), 0.0, 1.0)
    return d2 * (1.0 - h) + d1 * h - k * h * (1.0 - h)

# ------------------------------------------------------------------------------
# 2. CHIBI BODY RIG GENERATOR
# ------------------------------------------------------------------------------

def build_chibi_base_rig(X, Y, Z, plinth_w=52.0, plinth_d=42.0, plinth_h=9.0):
    """Generates the common chibi lower body, plinth, and chubby head."""
    d = np.full_like(X, 100.0)
    
    def add_shape(s):
        nonlocal d
        d = np.minimum(d, s)
    
    def add_smooth(s, k=1.8):
        nonlocal d
        d = smin(d, s, k=k)

    # 1. Stepped Wooden Plinth
    # Lower tier
    d_p1 = sdf_box(X, Y, Z, 0.0, 0.0, plinth_h * 0.25, plinth_w * 0.5, plinth_d * 0.5, plinth_h * 0.25)
    # Upper tier
    d_p2 = sdf_box(X, Y, Z, 0.0, 0.0, plinth_h * 0.65, plinth_w * 0.45, plinth_d * 0.45, plinth_h * 0.40)
    # Beveled Nameplate Plaque (front)
    d_plaque = sdf_box(X, Y, Z, 0.0, -plinth_d * 0.45 + 1.2, plinth_h * 0.55, plinth_w * 0.38, 1.5, plinth_h * 0.28)
    
    add_shape(d_p1)
    add_shape(d_p2)
    add_shape(d_plaque)

    # 2. Stubby Chibi Legs & Oxford Shoes
    for side in [-1, 1]:
        lx = side * 8.5
        # Leg trouser
        d_leg = sdf_cylinder_z(X, Y, Z, lx, 0.0, plinth_h - 1.0, 24.0, 4.8)
        # Cute rounded classic shoe
        d_shoe = sdf_ellipsoid(X, Y, Z, lx, 1.5, plinth_h + 2.0, 5.2, 7.2, 3.8)
        add_shape(d_leg)
        add_shape(d_shoe)

    # 3. Chubby Pear-Shaped Torso (Z from 22 to 48)
    d_torso = sdf_ellipsoid(X, Y, Z, 0.0, 0.5, 34.5, 13.5, 11.2, 12.0)
    # Belly softness protrusion
    d_belly = sdf_sphere(X, Y, Z, 0.0, 2.8, 33.0, 10.5)
    add_smooth(d_torso, k=2.5)
    add_smooth(d_belly, k=2.5)

    # 4. Large Pixar/Ghibli Head (Z center = 62.0)
    d_head = sdf_ellipsoid(X, Y, Z, 0.0, 0.0, 62.0, 20.5, 18.5, 19.5)
    # Chubby soft cheeks
    d_cheek_l = sdf_sphere(X, Y, Z, -11.0, 7.5, 57.5, 7.6)
    d_cheek_r = sdf_sphere(X, Y, Z,  11.0, 7.5, 57.5, 7.6)
    # Cute button nose
    d_nose = sdf_sphere(X, Y, Z, 0.0, 17.5, 59.5, 3.2)
    # Cute rounded ears
    d_ear_l = sdf_ellipsoid(X, Y, Z, -21.0, -1.0, 60.5, 3.2, 4.8, 5.2)
    d_ear_r = sdf_ellipsoid(X, Y, Z,  21.0, -1.0, 60.5, 3.2, 4.8, 5.2)

    add_smooth(d_head, k=3.0)
    add_smooth(d_cheek_l, k=2.2)
    add_smooth(d_cheek_r, k=2.2)
    add_shape(d_nose)
    add_shape(d_ear_l)
    add_shape(d_ear_r)

    return d

# ------------------------------------------------------------------------------
# 3. CHARACTER 1: ALBERT EINSTEIN
# ------------------------------------------------------------------------------

def build_albert_einstein_sdf(X, Y, Z):
    d = build_chibi_base_rig(X, Y, Z)
    
    def add_shape(s):
        nonlocal d
        d = np.minimum(d, s)
        
    def add_smooth(s, k=1.8):
        nonlocal d
        d = smin(d, s, k=k)

    # 1. Iconic Wild Fluffy Hair Curls (Clusters of spheres around head)
    # Crown tufts
    for ang in np.linspace(-65, 65, 7):
        rad = np.radians(ang)
        hx = 16.0 * np.sin(rad)
        hz = 62.0 + 19.0 * np.cos(rad)
        add_smooth(sdf_sphere(X, Y, Z, hx, -3.0, hz, 6.8), k=2.0)
    
    # Back and side fluffy hair clumps
    for phi in np.linspace(40, 320, 12):
        rad = np.radians(phi)
        hx = 20.5 * np.cos(rad)
        hy = 19.0 * np.sin(rad)
        if hy < 6.0: # Keep face visible
            add_smooth(sdf_sphere(X, Y, Z, hx, hy, 63.0, 6.5), k=2.2)
            add_smooth(sdf_sphere(X, Y, Z, hx * 1.05, hy * 1.05, 55.0, 6.0), k=2.2)

    # 2. Bushy Characteristic Mustache
    d_must_l = sdf_segment(X, Y, Z, -0.5, 17.0, 56.5, -6.5, 15.5, 54.5, 3.5)
    d_must_r = sdf_segment(X, Y, Z,  0.5, 17.0, 56.5,  6.5, 15.5, 54.5, 3.5)
    add_shape(d_must_l)
    add_shape(d_must_r)

    # 3. E = mc² Chalkboard & Arms
    # Chalkboard with wooden frame held in front of chest
    d_board_frame = sdf_box(X, Y, Z, 0.0, 15.0, 39.0, 13.0, 2.0, 9.0)
    d_board_inner = sdf_box(X, Y, Z, 0.0, 15.6, 39.0, 11.2, 1.6, 7.2)
    add_shape(d_board_frame)
    add_shape(d_board_inner)
    
    # Relief text indicator (embossed formula badge)
    d_formula = sdf_box(X, Y, Z, 0.0, 16.5, 39.0, 8.5, 0.8, 3.0)
    add_shape(d_formula)

    # Arms holding the chalkboard
    d_arm_l = sdf_segment(X, Y, Z, -13.0, 1.0, 44.0, -11.0, 14.0, 38.0, 4.0)
    d_arm_r = sdf_segment(X, Y, Z,  13.0, 1.0, 44.0,  11.0, 14.0, 38.0, 4.0)
    add_shape(d_arm_l)
    add_shape(d_arm_r)

    return d

# ------------------------------------------------------------------------------
# 4. CHARACTER 2: MAX PLANCK
# ------------------------------------------------------------------------------

def build_max_planck_sdf(X, Y, Z):
    d = build_chibi_base_rig(X, Y, Z)
    
    def add_shape(s):
        nonlocal d
        d = np.minimum(d, s)
        
    def add_smooth(s, k=1.8):
        nonlocal d
        d = smin(d, s, k=k)

    # 1. Distinguished High Forehead & Parted Side Hair
    for phi in np.linspace(70, 290, 9):
        rad = np.radians(phi)
        hx = 19.5 * np.cos(rad)
        hy = 18.0 * np.sin(rad)
        if hy < 3.0:
            add_smooth(sdf_sphere(X, Y, Z, hx, hy, 61.0, 5.2), k=2.0)
            add_smooth(sdf_sphere(X, Y, Z, hx * 0.95, hy * 0.95, 54.0, 4.8), k=2.0)

    # 2. Pince-Nez Round Spectacles & Trim Mustache
    d_spec_l = sdf_torus(X, Y, Z, -6.5, 17.5, 61.5, 5.2, 1.1, plane='xz')
    d_spec_r = sdf_torus(X, Y, Z,  6.5, 17.5, 61.5, 5.2, 1.1, plane='xz')
    d_bridge = sdf_segment(X, Y, Z, -2.5, 17.8, 61.5, 2.5, 17.8, 61.5, 0.9)
    add_shape(d_spec_l)
    add_shape(d_spec_r)
    add_shape(d_bridge)

    # Gentleman mustache
    d_must = sdf_segment(X, Y, Z, -4.5, 17.2, 56.2, 4.5, 17.2, 56.2, 2.2)
    add_shape(d_must)

    # Bowtie on collar
    d_bow = sdf_sphere(X, Y, Z, 0.0, 7.5, 45.5, 2.2)
    d_bow_l = sdf_box(X, Y, Z, -3.2, 7.5, 45.5, 2.0, 1.2, 1.5)
    d_bow_r = sdf_box(X, Y, Z,  3.2, 7.5, 45.5, 2.0, 1.2, 1.5)
    add_shape(d_bow)
    add_shape(d_bow_l)
    add_shape(d_bow_r)

    # 3. Glowing Quantum Energy Orb (E = h*nu)
    # Orb centered at (0, 15, 38)
    d_orb = sdf_sphere(X, Y, Z, 0.0, 15.0, 38.0, 6.4)
    # Quantum orbital energy ring around orb
    d_orb_ring = sdf_tilted_torus(X, Y, Z, 0.0, 15.0, 38.0, 9.2, 1.3, tilt_x_deg=35.0, tilt_z_deg=25.0)
    add_shape(d_orb)
    add_shape(d_orb_ring)

    # Arms cupping the quantum orb gently from both sides
    d_arm_l = sdf_segment(X, Y, Z, -13.0, 1.0, 44.0, -5.5, 14.0, 36.0, 3.8)
    d_arm_r = sdf_segment(X, Y, Z,  13.0, 1.0, 44.0,  5.5, 14.0, 36.0, 3.8)
    add_shape(d_arm_l)
    add_shape(d_arm_r)

    return d

# ------------------------------------------------------------------------------
# 5. CHARACTER 3: WERNER HEISENBERG
# ------------------------------------------------------------------------------

def build_werner_heisenberg_sdf(X, Y, Z):
    d = build_chibi_base_rig(X, Y, Z)
    
    def add_shape(s):
        nonlocal d
        d = np.minimum(d, s)
        
    def add_smooth(s, k=1.8):
        nonlocal d
        d = smin(d, s, k=k)

    # 1. Youthful Stylish Wavy Hair
    # Main wavy hair crest curving to the right
    d_quiff = sdf_ellipsoid(X, Y, Z, -2.0, 4.0, 80.0, 8.5, 7.2, 6.0)
    d_wave_r = sdf_ellipsoid(X, Y, Z, 8.5, 2.0, 78.0, 7.5, 6.8, 5.5)
    add_smooth(d_quiff, k=2.5)
    add_smooth(d_wave_r, k=2.5)

    # Back & side volume
    for phi in np.linspace(50, 310, 10):
        rad = np.radians(phi)
        hx = 20.0 * np.cos(rad)
        hy = 18.0 * np.sin(rad)
        if hy < 6.0:
            add_smooth(sdf_sphere(X, Y, Z, hx, hy, 62.0, 5.8), k=2.2)

    # Necktie
    d_tie = sdf_box(X, Y, Z, 0.0, 6.8, 41.0, 1.5, 1.0, 4.2)
    add_shape(d_tie)

    # 2. Quantum Uncertainty Principle Orbital Cloud / Atom Model
    # Held in raised right hand at (13, 14, 43)
    cx, cy, cz = 13.0, 14.0, 43.0
    d_atom_core = sdf_sphere(X, Y, Z, cx, cy, cz, 3.5)
    # Intersecting electron orbital rings
    d_ring1 = sdf_tilted_torus(X, Y, Z, cx, cy, cz, 9.5, 1.2, tilt_x_deg=35.0, tilt_z_deg=40.0)
    d_ring2 = sdf_tilted_torus(X, Y, Z, cx, cy, cz, 9.5, 1.2, tilt_x_deg=-40.0, tilt_z_deg=30.0)
    add_shape(d_atom_core)
    add_shape(d_ring1)
    add_shape(d_ring2)

    # Right arm extending forward to present the uncertainty orbital
    d_arm_r = sdf_segment(X, Y, Z, 13.0, 1.0, 44.0, cx, cy - 2.0, cz - 2.0, 3.8)
    # Left arm resting smartly by his side
    d_arm_l = sdf_segment(X, Y, Z, -13.0, 1.0, 44.0, -12.5, 3.5, 32.0, 3.8)
    add_shape(d_arm_r)
    add_shape(d_arm_l)

    return d

# ------------------------------------------------------------------------------
# 6. CHARACTER 4: ERWIN SCHRÖDINGER & HIS CAT
# ------------------------------------------------------------------------------

def build_erwin_schrodinger_sdf(X, Y, Z):
    d = build_chibi_base_rig(X, Y, Z)
    
    def add_shape(s):
        nonlocal d
        d = np.minimum(d, s)
        
    def add_smooth(s, k=1.8):
        nonlocal d
        d = smin(d, s, k=k)

    # 1. Neat Intellectual Hair & Parting
    for phi in np.linspace(60, 300, 10):
        rad = np.radians(phi)
        hx = 19.8 * np.cos(rad)
        hy = 18.2 * np.sin(rad)
        if hy < 5.0:
            add_smooth(sdf_sphere(X, Y, Z, hx, hy, 62.0, 5.5), k=2.0)
    # Swept-back hair crest
    d_crest = sdf_ellipsoid(X, Y, Z, 0.0, -3.0, 80.0, 10.0, 12.0, 5.0)
    add_smooth(d_crest, k=2.2)

    # 2. Round Professor Wireframe Spectacles
    d_spec_l = sdf_torus(X, Y, Z, -6.6, 17.6, 61.5, 5.4, 1.1, plane='xz')
    d_spec_r = sdf_torus(X, Y, Z,  6.6, 17.6, 61.5, 5.4, 1.1, plane='xz')
    d_bridge = sdf_segment(X, Y, Z, -2.5, 17.9, 61.5, 2.5, 17.9, 61.5, 0.9)
    add_shape(d_spec_l)
    add_shape(d_spec_r)
    add_shape(d_bridge)

    # Bowtie
    d_bow = sdf_sphere(X, Y, Z, 0.0, 7.2, 45.5, 2.0)
    add_shape(d_bow)

    # 3. Schrödinger's Box with Cute Peeking Cat!
    # Cardboard box held in arms: center (8.0, 14.0, 38.0), size 16x14x12
    bx, by, bz = 8.0, 14.0, 37.0
    d_box = sdf_box(X, Y, Z, bx, by, bz, 8.5, 7.5, 6.0)
    add_shape(d_box)

    # Open box flaps
    d_flap_f = sdf_box(X, Y, Z, bx, by + 7.5, bz + 4.5, 8.0, 1.0, 2.5)
    add_shape(d_flap_f)

    # Adorable Cat Head peeking out of the box!
    cx, cy, cz = bx, by, bz + 7.5
    d_cat_head = sdf_sphere(X, Y, Z, cx, cy, cz, 5.2)
    # Cat pointed ears
    d_ear_l = sdf_segment(X, Y, Z, cx - 3.2, cy, cz + 2.0, cx - 4.5, cy, cz + 6.5, 1.8)
    d_ear_r = sdf_segment(X, Y, Z, cx + 3.2, cy, cz + 2.0, cx + 4.5, cy, cz + 6.5, 1.8)
    # Cat cute snout
    d_cat_snout = sdf_sphere(X, Y, Z, cx, cy + 4.2, cz - 0.6, 1.8)
    # Cat cute paws resting on the front box rim
    d_paw_l = sdf_sphere(X, Y, Z, cx - 3.8, by + 7.2, bz + 4.0, 2.2)
    d_paw_r = sdf_sphere(X, Y, Z, cx + 3.8, by + 7.2, bz + 4.0, 2.2)

    add_smooth(d_cat_head, k=1.5)
    add_shape(d_ear_l)
    add_shape(d_ear_r)
    add_shape(d_cat_snout)
    add_shape(d_paw_l)
    add_shape(d_paw_r)

    # Arms holding the box
    d_arm_r = sdf_segment(X, Y, Z,  13.0, 1.0, 44.0, bx + 7.0, by, bz, 3.8)
    d_arm_l = sdf_segment(X, Y, Z, -13.0, 1.0, 44.0, bx - 7.0, by, bz, 3.8)
    add_shape(d_arm_r)
    add_shape(d_arm_l)

    return d

# ------------------------------------------------------------------------------
# 7. GRAND DIORAMA: ALL 4 QUANTUM PHYSICISTS TOGETHER
# ------------------------------------------------------------------------------

def build_quantum_diorama_sdf(X, Y, Z):
    """Combines all 4 quantum physicists onto a single magnificent diorama base."""
    # Master plinth base
    d_base = sdf_box(X, Y, Z, 0.0, 0.0, 4.5, 110.0, 23.0, 4.5)
    d_top  = sdf_box(X, Y, Z, 0.0, 0.0, 8.5, 106.0, 20.0, 3.5)
    d_diorama = np.minimum(d_base, d_top)

    # Offset coordinates for each character:
    # Einstein: X = -78
    # Planck:   X = -26
    # Heisenberg: X = +26
    # Schrödinger: X = +78
    offsets = [
        (-78.0, build_albert_einstein_sdf),
        (-26.0, build_max_planck_sdf),
        ( 26.0, build_werner_heisenberg_sdf),
        ( 78.0, build_erwin_schrodinger_sdf)
    ]

    for ox, builder in offsets:
        # Check active domain mask to optimize memory
        mask = (X >= ox - 26.0) & (X <= ox + 26.0)
        if np.any(mask):
            X_loc = X - ox
            d_char = builder(X_loc, Y, Z)
            d_diorama = np.minimum(d_diorama, d_char)

    return d_diorama

# ------------------------------------------------------------------------------
# 8. BINARY STL WRITER & MESH EXTRACTION
# ------------------------------------------------------------------------------

def write_binary_stl(filepath, verts, faces, header_title="QUANTUM_CHIBI_AI4D"):
    """Writes binary STL file (80-byte header + triangle count + 50-byte triangles)."""
    header = header_title.encode('ascii')[:80].ljust(80, b'\0')
    num_faces = len(faces)
    
    # Compute per-face normals
    v0 = verts[faces[:, 0]]
    v1 = verts[faces[:, 1]]
    v2 = verts[faces[:, 2]]
    normals = np.cross(v1 - v0, v2 - v0)
    norm_lens = np.linalg.norm(normals, axis=1, keepdims=True)
    norm_lens[norm_lens < 1e-8] = 1.0
    normals /= norm_lens

    with open(filepath, 'wb') as f:
        f.write(header)
        f.write(struct.pack('<I', num_faces))
        for i in range(num_faces):
            nx, ny, nz = normals[i]
            x0, y0, z0 = v0[i]
            x1, y1, z1 = v1[i]
            x2, y2, z2 = v2[i]
            f.write(struct.pack('<3f3f3f3fH', nx, ny, nz, x0, y0, z0, x1, y1, z1, x2, y2, z2, 0))

def generate_chibi_stl(out_path, character_key='einstein', res=0.60):
    t0 = time.time()
    print(f"--- Generating 3D Chibi Model: [{character_key.upper()}] (Voxel Res: {res:.2f}mm) ---")
    
    if character_key == 'diorama':
        x_min, x_max = -115.0, 115.0
        y_min, y_max = -26.0, 26.0
        z_min, z_max = 0.0, 92.0
    else:
        x_min, x_max = -30.0, 30.0
        y_min, y_max = -24.0, 24.0
        z_min, z_max = 0.0, 90.0

    nx = int(np.ceil((x_max - x_min) / res)) + 1
    ny = int(np.ceil((y_max - y_min) / res)) + 1
    nz = int(np.ceil((z_max - z_min) / res)) + 1

    print(f"Grid Dimensions: {nx} x {ny} x {nz} = {nx * ny * nz:,} voxels")

    x = np.linspace(x_min, x_max, nx)
    y = np.linspace(y_min, y_max, ny)
    z = np.linspace(z_min, z_max, nz)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    t_sdf = time.time()
    if character_key == 'einstein':
        dist = build_albert_einstein_sdf(X, Y, Z)
    elif character_key == 'planck':
        dist = build_max_planck_sdf(X, Y, Z)
    elif character_key == 'heisenberg':
        dist = build_werner_heisenberg_sdf(X, Y, Z)
    elif character_key == 'schrodinger':
        dist = build_erwin_schrodinger_sdf(X, Y, Z)
    elif character_key == 'diorama':
        dist = build_quantum_diorama_sdf(X, Y, Z)
    else:
        raise ValueError(f"Unknown character_key: {character_key}")

    print(f"SDF evaluation completed in {time.time() - t_sdf:.2f}s")

    # Marching Cubes
    t_mc = time.time()
    dx = (x_max - x_min) / (nx - 1)
    dy = (y_max - y_min) / (ny - 1)
    dz = (z_max - z_min) / (nz - 1)

    # Pad array to ensure sealed boundary
    dist_padded = np.pad(dist, 1, mode='constant', constant_values=10.0)
    verts, faces, _, _ = measure.marching_cubes(dist_padded, level=0.0, spacing=(dx, dy, dz))

    # Shift vertices back to world space
    verts[:, 0] += (x_min - dx)
    verts[:, 1] += (y_min - dy)
    verts[:, 2] += (z_min - dz)

    # Align base to Z = 0.0
    verts[:, 2] -= verts[:, 2].min()

    print(f"Marching Cubes completed in {time.time() - t_mc:.2f}s | Vertices: {len(verts):,} | Faces: {len(faces):,}")

    # Verify Watertightness (0 boundary edges)
    edges = np.vstack([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    edges.sort(axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    boundary_edges = np.sum(counts == 1)
    print(f"Mesh Topology Check: Boundary Edges = {boundary_edges} (Watertight: {boundary_edges == 0})")

    write_binary_stl(out_path, verts, faces, header_title=f"QUANTUM_CHIBI_{character_key.upper()}_AI4D_RBRU")
    file_size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"Saved: {out_path} ({file_size_mb:.2f} MB) in {time.time() - t0:.2f}s\n")
    return out_path

# ------------------------------------------------------------------------------
# 9. MAIN EXECUTION
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.join(base_dir, "models_3d", "quantum_physicists_chibi")
    os.makedirs(target_dir, exist_ok=True)

    characters = [
        ("einstein", "einstein_chibi_3d.stl"),
        ("planck", "planck_chibi_3d.stl"),
        ("heisenberg", "heisenberg_chibi_3d.stl"),
        ("schrodinger", "schrodinger_chibi_3d.stl"),
        ("diorama", "quantum_quartet_diorama_3d.stl")
    ]

    for char_key, file_name in characters:
        out_file = os.path.join(target_dir, file_name)
        # Use res=0.55 for characters, res=0.75 for diorama to keep files performant
        res = 0.75 if char_key == 'diorama' else 0.55
        generate_chibi_stl(out_file, character_key=char_key, res=res)

    print("[SUCCESS] All 5 Quantum Chibi 3D STL models generated successfully!")
