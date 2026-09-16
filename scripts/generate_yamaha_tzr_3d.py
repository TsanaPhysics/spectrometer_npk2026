#!/usr/bin/env python3
"""
Yamaha TZR Series - 3D Mechanical & Aerodynamic Model Generator
Designed with Skill: motorcycle-3d-cad-architect
Digital Agriphysics & AI Research Unit (JC_AI_SciRBRU)
Department of Physics, Faculty of Science and Technology,
Rambhai Barni Rajabhat University (RBRU)

Generates:
1. models_3d/yamaha_tzr/yamaha_tzr_3d.stl (Pure Motorcycle Model)
2. models_3d/yamaha_tzr/yamaha_tzr_on_stand_3d.stl (Motorcycle on Paddock Stand & Display Plinth)
"""

import os
import time
import struct
import numpy as np
from skimage import measure

# --- Mathematical Signed Distance Functions (SDF) ---

def sdf_box(px, py, pz, cx, cy, cz, sx, sy, sz):
    """SDF for an axis-aligned box centered at (cx, cy, cz) with half-sizes (sx, sy, sz)"""
    dx = np.abs(px - cx) - sx
    dy = np.abs(py - cy) - sy
    dz = np.abs(pz - cz) - sz
    outside = np.sqrt(np.maximum(dx, 0.0)**2 + np.maximum(dy, 0.0)**2 + np.maximum(dz, 0.0)**2)
    inside = np.minimum(np.maximum(dx, np.maximum(dy, dz)), 0.0)
    return outside + inside

def sdf_sphere(px, py, pz, cx, cy, cz, r):
    return np.sqrt((px - cx)**2 + (py - cy)**2 + (pz - cz)**2) - r

def sdf_segment(px, py, pz, ax, ay, az, bx, by, bz, r):
    """SDF for a capsule/cylinder segment between A and B with radius r"""
    p_a_x, p_a_y, p_a_z = px - ax, py - ay, pz - az
    b_a_x, b_a_y, b_a_z = bx - ax, by - ay, bz - az
    ba_len_sq = b_a_x**2 + b_a_y**2 + b_a_z**2
    t = np.clip((p_a_x * b_a_x + p_a_y * b_a_y + p_a_z * b_a_z) / max(ba_len_sq, 1e-6), 0.0, 1.0)
    c_x = ax + t * b_a_x
    c_y = ay + t * b_a_y
    c_z = az + t * b_a_z
    return np.sqrt((px - c_x)**2 + (py - c_y)**2 + (pz - c_z)**2) - r

def sdf_cone_segment(px, py, pz, ax, ay, az, bx, by, bz, ra, rb):
    """SDF for a truncated cone segment between A and B with radii ra and rb"""
    p_a_x, p_a_y, p_a_z = px - ax, py - ay, pz - az
    b_a_x, b_a_y, b_a_z = bx - ax, by - ay, bz - az
    ba_len_sq = b_a_x**2 + b_a_y**2 + b_a_z**2
    t = np.clip((p_a_x * b_a_x + p_a_y * b_a_y + p_a_z * b_a_z) / max(ba_len_sq, 1e-6), 0.0, 1.0)
    c_x = ax + t * b_a_x
    c_y = ay + t * b_a_y
    c_z = az + t * b_a_z
    r_t = ra + t * (rb - ra)
    return np.sqrt((px - c_x)**2 + (py - c_y)**2 + (pz - c_z)**2) - r_t

def sdf_torus_y(px, py, pz, cx, cz, R_major, r_minor):
    """Torus in the XZ plane with central axis along Y"""
    d_xz = np.sqrt((px - cx)**2 + (pz - cz)**2) - R_major
    return np.sqrt(d_xz**2 + py**2) - r_minor

def sdf_ellipsoid(px, py, pz, cx, cy, cz, rx, ry, rz):
    dx = (px - cx) / rx
    dy = (py - cy) / ry
    dz = (pz - cz) / rz
    k0 = np.sqrt(dx**2 + dy**2 + dz**2)
    k1 = np.sqrt((dx/rx)**2 + (dy/ry)**2 + (dz/rz)**2)
    return (k0 - 1.0) * (k0 / np.maximum(k1, 1e-6))

def write_binary_stl(filepath, verts, faces, header_title="YAMAHA_TZR_3D_JC_AI_SciRBRU"):
    header = header_title.encode('ascii')[:80].ljust(80, b'\0')
    num_faces = len(faces)
    
    v0 = verts[faces[:, 0]]
    v1 = verts[faces[:, 1]]
    v2 = verts[faces[:, 2]]
    normals = np.cross(v1 - v0, v2 - v0)
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normals /= norms
    
    with open(filepath, 'wb') as f:
        f.write(header)
        f.write(struct.pack('<I', num_faces))
        for i in range(num_faces):
            f.write(struct.pack('<3f', *normals[i]))
            f.write(struct.pack('<3f', *v0[i]))
            f.write(struct.pack('<3f', *v1[i]))
            f.write(struct.pack('<3f', *v2[i]))
            f.write(struct.pack('<H', 0))
            
    print(f"[SUCCESS] Exported binary STL: {filepath}")
    print(f"          Triangles: {num_faces:,} | File Size: {os.path.getsize(filepath)/1024/1024:.2f} MB")

def build_yamaha_tzr_sdf(X, Y, Z, include_stand=False):
    """
    Constructs comprehensive mathematical Signed Distance Field for Yamaha TZR:
    Deltabox Frame, 2-Stroke YPVS Engine, Tuned Expansion Chamber,
    Wheels, Forks, Swingarm, Aerodynamic Fairing, Fuel Tank, Stepped Seat, Tail Cowl.
    """
    # Start with a very large distance
    d = np.full_like(X, 1000.0, dtype=np.float32)
    
    def add_shape(shape):
        nonlocal d
        d = np.minimum(d, shape)

    # -------------------------------------------------------------
    # 1. WHEELS & RUNNING GEAR (Front X=+67.5, Rear X=-67.5, Z=30.0)
    # -------------------------------------------------------------
    # Front Tire & Rim
    d_f_tire = sdf_torus_y(X, Y, Z, 67.5, 30.0, 24.5, 5.5)
    d_f_rim  = sdf_torus_y(X, Y, Z, 67.5, 30.0, 20.5, 2.0)
    d_f_hub  = sdf_segment(X, Y, Z, 67.5, -7.0, 30.0, 67.5, 7.0, 30.0, 6.5)
    add_shape(d_f_tire)
    add_shape(d_f_rim)
    add_shape(d_f_hub)
    
    # Front 3-Spoke Sport Alloy
    for ang in [0, 120, 240]:
        rad = np.radians(ang)
        spk_x = 67.5 + 19.5 * np.sin(rad)
        spk_z = 30.0 + 19.5 * np.cos(rad)
        d_f_spk = sdf_segment(X, Y, Z, 67.5, 0.0, 30.0, spk_x, 0.0, spk_z, 2.6)
        add_shape(d_f_spk)
        
    # Front Twin Brake Rotors & Calipers
    for side in [-1, 1]:
        d_f_disc = sdf_segment(X, Y, Z, 67.5, side * 6.5, 30.0, 67.5, side * 6.5, 30.0, 15.5)
        # Flatten disc into thin plate
        d_f_disc = np.maximum(d_f_disc, np.abs(Y - side * 6.5) - 0.7)
        add_shape(d_f_disc)
        # Brake Calipers
        d_f_cal = sdf_box(X, Y, Z, 57.0, side * 7.5, 33.0, 4.5, 2.0, 5.0)
        add_shape(d_f_cal)

    # Rear Tire & Rim (Wider Sport Tire)
    d_r_tire = sdf_torus_y(X, Y, Z, -67.5, 30.0, 23.5, 6.5)
    d_r_rim  = sdf_torus_y(X, Y, Z, -67.5, 30.0, 20.0, 2.2)
    d_r_hub  = sdf_segment(X, Y, Z, -67.5, -8.0, 30.0, -67.5, 8.0, 30.0, 7.5)
    add_shape(d_r_tire)
    add_shape(d_r_rim)
    add_shape(d_r_hub)
    
    # Rear 3-Spoke Sport Alloy
    for ang in [60, 180, 300]:
        rad = np.radians(ang)
        spk_x = -67.5 + 19.0 * np.sin(rad)
        spk_z = 30.0 + 19.0 * np.cos(rad)
        d_r_spk = sdf_segment(X, Y, Z, -67.5, 0.0, 30.0, spk_x, 0.0, spk_z, 2.8)
        add_shape(d_r_spk)
        
    # Rear Brake Rotor (Right) & Chain Sprocket (Left)
    d_r_disc = sdf_segment(X, Y, Z, -67.5, -6.5, 30.0, -67.5, -6.5, 30.0, 13.0)
    d_r_disc = np.maximum(d_r_disc, np.abs(Y + 6.5) - 0.7)
    add_shape(d_r_disc)
    
    d_r_sproc = sdf_segment(X, Y, Z, -67.5, 7.0, 30.0, -67.5, 7.0, 30.0, 14.5)
    d_r_sproc = np.maximum(d_r_sproc, np.abs(Y - 7.0) - 0.9)
    add_shape(d_r_sproc)
    
    # Drive Chain (Left side Y=+8.5)
    d_chain_top = sdf_segment(X, Y, Z, -22.0, 8.5, 37.0, -67.5, 8.5, 33.0, 1.8)
    d_chain_bot = sdf_segment(X, Y, Z, -22.0, 8.5, 33.0, -67.5, 8.5, 27.0, 1.8)
    add_shape(d_chain_top)
    add_shape(d_chain_bot)

    # -------------------------------------------------------------
    # 2. FRONT SUSPENSION & COCKPIT
    # -------------------------------------------------------------
    # Telescopic Forks (Left & Right)
    for side in [-1, 1]:
        # Upper Stanchion (Chrome)
        d_fork_up = sdf_segment(X, Y, Z, 38.0, side * 11.5, 74.0, 52.0, side * 11.5, 52.0, 3.2)
        # Lower Slider (Cast Alloy)
        d_fork_lo = sdf_segment(X, Y, Z, 52.0, side * 11.5, 52.0, 67.5, side * 11.5, 30.0, 4.5)
        add_shape(d_fork_up)
        add_shape(d_fork_lo)
        
    # Triple Tree Clamps & Steering Stem
    d_stem   = sdf_segment(X, Y, Z, 38.0, 0.0, 64.0, 38.0, 0.0, 76.0, 7.0)
    d_clamp_up = sdf_box(X, Y, Z, 38.0, 0.0, 74.0, 4.0, 13.5, 2.5)
    d_clamp_lo = sdf_box(X, Y, Z, 42.0, 0.0, 65.0, 5.0, 13.5, 3.0)
    add_shape(d_stem)
    add_shape(d_clamp_up)
    add_shape(d_clamp_lo)
    
    # Clip-on Handlebars (Racing angle)
    for side in [-1, 1]:
        d_bar = sdf_segment(X, Y, Z, 38.0, side * 11.5, 74.0, 30.0, side * 31.0, 69.0, 2.4)
        # Grip & Bar End
        d_grip = sdf_segment(X, Y, Z, 33.0, side * 23.0, 70.5, 30.0, side * 31.0, 69.0, 3.2)
        add_shape(d_bar)
        add_shape(d_grip)
        
    # Cockpit Gauges (Tachometer & Speedometer)
    d_gauge_l = sdf_segment(X, Y, Z, 43.0,  6.0, 76.0, 41.0,  6.0, 79.0, 5.5)
    d_gauge_r = sdf_segment(X, Y, Z, 43.0, -6.0, 76.0, 41.0, -6.0, 79.0, 5.5)
    add_shape(d_gauge_l)
    add_shape(d_gauge_r)

    # -------------------------------------------------------------
    # 3. YAMAHA DELTABOX ALUMINUM FRAME (Twin-Spar Geometry)
    # -------------------------------------------------------------
    for side in [-1, 1]:
        # Main Deltabox Diagonal Spar (Steering head to Swingarm pivot)
        # Segment 1: Head to upper bend
        d_spar1 = sdf_cone_segment(X, Y, Z, 36.0, side * 11.0, 70.0, 15.0, side * 16.0, 60.0, 6.5, 7.5)
        # Segment 2: Upper bend to pivot
        d_spar2 = sdf_cone_segment(X, Y, Z, 15.0, side * 16.0, 60.0, -25.0, side * 18.0, 38.0, 7.5, 8.5)
        add_shape(d_spar1)
        add_shape(d_spar2)
        
        # Engine Cradle Down-tube
        d_down = sdf_segment(X, Y, Z, 34.0, side * 9.0, 64.0, -2.0, side * 12.0, 26.0, 3.2)
        d_cradle_bot = sdf_segment(X, Y, Z, -2.0, side * 12.0, 26.0, -22.0, side * 14.0, 27.0, 3.5)
        add_shape(d_down)
        add_shape(d_cradle_bot)
        
        # Rear Subframe Tubes (supporting seat & tail cowl)
        d_sub1 = sdf_segment(X, Y, Z, -25.0, side * 16.0, 44.0, -78.0, side * 9.0, 66.0, 3.0)
        d_sub2 = sdf_segment(X, Y, Z, -25.0, side * 16.0, 38.0, -55.0, side * 11.0, 58.0, 2.8)
        add_shape(d_sub1)
        add_shape(d_sub2)
        
        # Rider Footpeg & Rearset
        d_peg = sdf_segment(X, Y, Z, -24.0, side * 18.0, 33.0, -24.0, side * 27.0, 33.0, 2.5)
        add_shape(d_peg)

    # Frame Cross-Brace over engine
    d_brace = sdf_box(X, Y, Z, 12.0, 0.0, 63.0, 5.0, 13.0, 3.5)
    add_shape(d_brace)

    # -------------------------------------------------------------
    # 4. 2-STROKE YPVS ENGINE & RADIATOR
    # -------------------------------------------------------------
    # Crankcase Core
    d_crank = sdf_box(X, Y, Z, -7.0, 0.0, 33.0, 14.0, 12.0, 10.0)
    add_shape(d_crank)
    
    # Right Clutch Cover (Large round casing)
    d_clutch = sdf_segment(X, Y, Z, -7.0, -11.0, 33.0, -7.0, -16.0, 33.0, 10.5)
    add_shape(d_clutch)
    
    # Left Magneto / Flywheel Cover
    d_magneto = sdf_segment(X, Y, Z, -7.0, 11.0, 33.0, -7.0, 15.0, 33.0, 9.5)
    add_shape(d_magneto)
    
    # Inclined Cylinder Block (45-degree forward slant)
    d_cylinder = sdf_cone_segment(X, Y, Z, -2.0, 0.0, 40.0, 13.0, 0.0, 55.0, 9.5, 9.0)
    add_shape(d_cylinder)
    
    # Cylinder Head & Spark Plug
    d_head = sdf_sphere(X, Y, Z, 15.0, 0.0, 57.0, 8.5)
    d_plug = sdf_segment(X, Y, Z, 15.0, 0.0, 57.0, 18.0, 0.0, 62.0, 2.2)
    add_shape(d_head)
    add_shape(d_plug)
    
    # YPVS (Yamaha Power Valve System) Servo Chamber on exhaust port
    d_ypvs = sdf_segment(X, Y, Z, 13.0, -8.0, 51.0, 13.0, 8.0, 51.0, 4.2)
    add_shape(d_ypvs)
    
    # Curved Radiator (behind front wheel)
    d_rad = sdf_box(X, Y, Z, 27.0, 0.0, 45.0, 2.5, 16.0, 9.0)
    add_shape(d_rad)

    # -------------------------------------------------------------
    # 5. TUNED EXPANSION CHAMBER EXHAUST (Signature 2T Multi-Cone)
    # -------------------------------------------------------------
    # Header Pipe (exits cylinder front, sweeps down under engine)
    d_exh_h1 = sdf_cone_segment(X, Y, Z, 14.0, 0.0, 49.0, 14.0, -5.0, 32.0, 3.8, 4.2)
    d_exh_h2 = sdf_cone_segment(X, Y, Z, 14.0, -5.0, 32.0, 8.0, -9.0, 22.0, 4.2, 5.0)
    add_shape(d_exh_h1)
    add_shape(d_exh_h2)
    
    # Divergent Diffuser Cone (expanding acoustic cone)
    d_exh_diff = sdf_cone_segment(X, Y, Z, 8.0, -9.0, 22.0, -6.0, -15.0, 20.0, 5.0, 8.5)
    add_shape(d_exh_diff)
    
    # Resonant Belly Chamber (widest section under swingarm pivot)
    d_exh_belly = sdf_segment(X, Y, Z, -6.0, -15.0, 20.0, -24.0, -16.0, 21.0, 8.8)
    add_shape(d_exh_belly)
    
    # Convergent Baffle Cone (tapers acoustic reflection wave)
    d_exh_baffle = sdf_cone_segment(X, Y, Z, -24.0, -16.0, 21.0, -46.0, -18.0, 29.0, 8.8, 3.8)
    add_shape(d_exh_baffle)
    
    # Stinger Pipe
    d_exh_stinger = sdf_segment(X, Y, Z, -46.0, -18.0, 29.0, -52.0, -19.0, 34.0, 3.2)
    add_shape(d_exh_stinger)
    
    # Upswept Aluminum Racing Silencer (ปลายท่อสูตรอลูมิเนียมเชิด)
    d_silencer = sdf_segment(X, Y, Z, -52.0, -19.0, 34.0, -85.0, -23.0, 48.0, 5.8)
    d_tip      = sdf_segment(X, Y, Z, -85.0, -23.0, 48.0, -88.0, -23.5, 49.5, 2.5)
    add_shape(d_silencer)
    add_shape(d_tip)

    # -------------------------------------------------------------
    # 6. REAR SWINGARM & MONOSHOCK
    # -------------------------------------------------------------
    # Aluminum Box-Section Swingarm Arms (Left & Right)
    for side in [-1, 1]:
        d_arm = sdf_segment(X, Y, Z, -25.0, side * 17.0, 38.0, -67.5, side * 11.5, 30.0, 4.0)
        add_shape(d_arm)
        
    # Swingarm Front Pivot Cross-Tube
    d_arm_cross = sdf_segment(X, Y, Z, -25.0, -17.0, 38.0, -25.0, 17.0, 38.0, 5.5)
    # Swingarm Stabilizer Arch over tire
    d_arm_arch  = sdf_segment(X, Y, Z, -42.0, -14.0, 38.0, -42.0, 14.0, 38.0, 3.8)
    add_shape(d_arm_cross)
    add_shape(d_arm_arch)
    
    # Monocross / Monoshock Unit (Central spring-damper)
    d_shock = sdf_segment(X, Y, Z, -22.0, 0.0, 52.0, -32.0, 0.0, 36.0, 4.5)
    add_shape(d_shock)

    # -------------------------------------------------------------
    # 7. BODYWORK: FUEL TANK, SEAT, FAIRINGS & TAIL COWL
    # -------------------------------------------------------------
    # Sculpted Fuel Tank (with knee indents)
    d_tank = sdf_ellipsoid(X, Y, Z, 7.0, 0.0, 64.0, 24.0, 17.0, 11.0)
    # Knee Recesses (hollowed out on sides)
    d_indent_l = sdf_sphere(X, Y, Z, -2.0,  19.0, 63.0, 10.0)
    d_indent_r = sdf_sphere(X, Y, Z, -2.0, -19.0, 63.0, 10.0)
    d_tank = np.maximum(d_tank, -d_indent_l)
    d_tank = np.maximum(d_tank, -d_indent_r)
    # Aircraft-style Fuel Cap
    d_cap = sdf_segment(X, Y, Z, 9.0, 0.0, 74.0, 9.0, 0.0, 76.5, 4.2)
    add_shape(d_tank)
    add_shape(d_cap)
    
    # Stepped Racing Seat
    # Rider Seat (Low pocket)
    d_seat_rider = sdf_box(X, Y, Z, -28.0, 0.0, 60.5, 12.0, 12.5, 3.0)
    # Pillion Seat / Step
    d_seat_pillion = sdf_box(X, Y, Z, -46.0, 0.0, 65.5, 8.0, 10.5, 3.5)
    add_shape(d_seat_rider)
    add_shape(d_seat_pillion)
    
    # Aerodynamic Tail Cowl (Wedge profile tapering rearward)
    d_tail = sdf_cone_segment(X, Y, Z, -45.0, 0.0, 65.0, -90.0, 0.0, 71.0, 13.5, 6.0)
    # Flatten tail sides
    d_tail = np.maximum(d_tail, np.abs(Y) - 13.0)
    add_shape(d_tail)
    
    # Taillight Cluster (Rectangular)
    d_taillight = sdf_box(X, Y, Z, -90.5, 0.0, 71.0, 2.0, 5.5, 3.0)
    add_shape(d_taillight)
    
    # Front Aerodynamic Fairing & Nose Cone
    # Upper Cowl Nose
    d_nose = sdf_ellipsoid(X, Y, Z, 55.0, 0.0, 69.0, 25.0, 18.0, 13.0)
    # Clip off inner engine area
    d_nose = np.maximum(d_nose, -(sdf_box(X, Y, Z, 48.0, 0.0, 65.0, 16.0, 14.0, 10.0)))
    add_shape(d_nose)
    
    # Bubble Windscreen (Sweeping upward)
    d_screen = sdf_cone_segment(X, Y, Z, 55.0, 0.0, 75.0, 32.0, 0.0, 93.0, 12.0, 5.0)
    d_screen = np.maximum(d_screen, np.abs(Y) - 10.0)
    add_shape(d_screen)
    
    # Dual / Rectangular Headlight
    d_light = sdf_box(X, Y, Z, 77.0, 0.0, 67.5, 2.5, 9.5, 4.5)
    add_shape(d_light)
    
    # Side Fairings (Lower panels with NACA duct cutout)
    for side in [-1, 1]:
        d_side_fairing = sdf_box(X, Y, Z, 24.0, side * 19.0, 50.0, 20.0, 2.0, 12.0)
        # Duct cutout
        d_duct = sdf_sphere(X, Y, Z, 20.0, side * 19.0, 48.0, 6.5)
        d_side_fairing = np.maximum(d_side_fairing, -d_duct)
        add_shape(d_side_fairing)
        
    # Front Hugger Mudguard (over front tire)
    d_fender = sdf_torus_y(X, Y, Z, 67.5, 30.0, 26.5, 2.2)
    # Only keep upper sector of fender (Z > 33, X between 48 and 82)
    d_fender = np.maximum(d_fender, -(Z - 32.0))
    d_fender = np.maximum(d_fender, -(X - 48.0))
    d_fender = np.maximum(d_fender, (X - 82.0))
    d_fender = np.maximum(d_fender, np.abs(Y) - 9.0)
    add_shape(d_fender)

    # -------------------------------------------------------------
    # 8. PADDOCK RACING STAND & GROUND PEDESTAL (Optional)
    # -------------------------------------------------------------
    if include_stand:
        # Racing Stand (Red Tubular Frame lifting rear swingarm spools)
        for side in [-1, 1]:
            # Stand upright tube
            d_st_up = sdf_segment(X, Y, Z, -67.5, side * 24.0, 30.0, -85.0, side * 24.0, 3.0, 2.5)
            # Stand base runner
            d_st_base = sdf_segment(X, Y, Z, -85.0, side * 24.0, 3.0, -100.0, side * 24.0, 3.0, 2.5)
            # Spool cradle arm
            d_st_arm = sdf_segment(X, Y, Z, -67.5, side * 13.0, 30.0, -67.5, side * 24.0, 30.0, 2.2)
            add_shape(d_st_up)
            add_shape(d_st_base)
            add_shape(d_st_arm)
            
        # Stand handle crossbar
        d_st_cross = sdf_segment(X, Y, Z, -100.0, -24.0, 3.0, -100.0, 24.0, 3.0, 2.5)
        add_shape(d_st_cross)
        
        # Ground Plinth Plate (Z = 0 to 2.5mm)
        d_plinth = sdf_box(X, Y, Z, -5.0, 0.0, 1.25, 105.0, 34.0, 1.25)
        add_shape(d_plinth)

    return d

def generate_tzr_stl(out_path, include_stand=False, res=0.55):
    t0 = time.time()
    print(f"\n=======================================================")
    print(f"Generating Yamaha TZR 3D Solid Model: {os.path.basename(out_path)}")
    print(f"Stand mode: {include_stand} | Voxel Resolution: {res:.2f} mm")
    print(f"=======================================================")
    
    # Domain bounds (mm)
    x_min, x_max = -112.0, 98.0
    y_min, y_max = -38.0, 38.0
    z_min, z_max = -0.5, 106.0
    
    nx = int(round((x_max - x_min) / res))
    ny = int(round((y_max - y_min) / res))
    nz = int(round((z_max - z_min) / res))
    
    print(f"Computing 3D Grid: {nx} x {ny} x {nz} ({nx*ny*nz/1e6:.1f} M voxels)...")
    
    x = np.linspace(x_min, x_max, nx)
    y = np.linspace(y_min, y_max, ny)
    z = np.linspace(z_min, z_max, nz)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    
    t_sdf = time.time()
    dist = build_yamaha_tzr_sdf(X, Y, Z, include_stand=include_stand)
    print(f"SDF evaluation completed in {time.time() - t_sdf:.2f}s")
    
    # Marching Cubes
    t_mc = time.time()
    dx = (x_max - x_min) / (nx - 1)
    dy = (y_max - y_min) / (ny - 1)
    dz = (z_max - z_min) / (nz - 1)
    
    # Pad array with +1 so the boundaries are clean
    dist_padded = np.pad(dist, 1, mode='constant', constant_values=10.0)
    verts, faces, normals, _ = measure.marching_cubes(dist_padded, level=0.0, spacing=(dx, dy, dz))
    
    # Shift vertices back to real-world mm coordinates
    verts[:, 0] += (x_min - dx)
    verts[:, 1] += (y_min - dy)
    verts[:, 2] += (z_min - dz)
    
    # Align model bottom to Z = 0.0
    verts[:, 2] -= verts[:, 2].min()
    
    print(f"Marching Cubes finished in {time.time() - t_mc:.2f}s | Vertices: {len(verts):,} | Faces: {len(faces):,}")
    
    # Verify watertightness (check edge counts)
    edges = np.vstack([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    edges.sort(axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    boundary_edges = np.sum(counts == 1)
    print(f"Mesh Topology Check: Boundary Edges = {boundary_edges} (Watertight: {boundary_edges == 0})")
    
    write_binary_stl(out_path, verts, faces, header_title=f"YAMAHA_TZR_{'STAND' if include_stand else 'SOLO'}_JC_AI_SciRBRU")
    print(f"Total processing time: {time.time() - t0:.2f}s\n")
    return out_path

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tzr_dir = os.path.join(base_dir, "models_3d", "yamaha_tzr")
    os.makedirs(tzr_dir, exist_ok=True)
    
    # 1. Generate Pure Motorcycle Model (for desktop display & 3D printing)
    solo_stl = os.path.join(tzr_dir, "yamaha_tzr_3d.stl")
    generate_tzr_stl(solo_stl, include_stand=False, res=0.50)
    
    # 2. Generate Motorcycle on Racing Stand & Display Plinth
    stand_stl = os.path.join(tzr_dir, "yamaha_tzr_on_stand_3d.stl")
    generate_tzr_stl(stand_stl, include_stand=True, res=0.50)
    
    print("[ALL DONE] Yamaha TZR 3D STL models generated successfully!")
