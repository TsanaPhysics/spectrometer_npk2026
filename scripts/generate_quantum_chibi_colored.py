#!/usr/bin/env python3
"""
==============================================================================
🎨 FULL-COLOR QUANTUM CHIBI 3D MODEL GENERATOR (PIXAR / GHIBLI PBR)
🔬 Albert Einstein • Max Planck • Werner Heisenberg • Erwin Schrödinger
🏛️ หน่วยวิจัยฟิสิกส์เกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics) มรภ.รำไพพรรณี
==============================================================================
Generates full-color 3D models in GLB (glTF 2.0 Binary with PBR materials) 
and Color PLY (Polygon File Format with RGBA vertex colors) exactly matching
the Pixar/Ghibli concept art:
  models_3d/quantum_physicists_chibi/quantum_chibi_quartet.jpg
"""

import os
import sys
import time
import json
import struct
import numpy as np
from skimage import measure

# Import SDF primitives from our existing generator
from generate_quantum_chibi_3d import (
    build_albert_einstein_sdf,
    build_max_planck_sdf,
    build_werner_heisenberg_sdf,
    build_erwin_schrodinger_sdf,
    build_quantum_diorama_sdf
)

# ------------------------------------------------------------------------------
# 1. PIXAR / GHIBLI PHOTOREALISTIC COLOR & TEXTURE SHADING ENGINE
# ------------------------------------------------------------------------------

def hex_to_rgb(hex_str):
    hex_clean = hex_str.lstrip('#')
    return np.array([int(hex_clean[i:i+2], 16) / 255.0 for i in (0, 2, 4)], dtype=np.float32)

def compute_photorealistic_colors(verts, char_key='einstein'):
    """
    Computes precise, multi-zone Pixar/Ghibli style PBR vertex colors, 
    including eyes with gloss reflections, blush cheeks, tweed/knitted fabrics,
    glowing energy orbs, and walnut plinths with engraved brass plaques.
    """
    count = len(verts)
    colors = np.zeros((count, 4), dtype=np.float32)
    emissive = np.zeros((count, 3), dtype=np.float32)

    X = verts[:, 0]
    Y = verts[:, 1]
    Z = verts[:, 2]

    # Pre-defined palette from concept art
    c_walnut     = hex_to_rgb("#3e2723") # Dark walnut wood
    c_walnut_top = hex_to_rgb("#4e342e") # Lighter top bevel
    c_brass      = hex_to_rgb("#d4af37") # Polished brass plaque
    c_brass_edge = hex_to_rgb("#aa8c2c") # Darkened brass border
    c_skin_base  = hex_to_rgb("#fcd5be") # Warm peach skin
    c_skin_blush = hex_to_rgb("#fca5a5") # Soft rosy cheek blush
    c_nose_tip   = hex_to_rgb("#f87171") # Button nose gentle pink
    c_eye_pupil  = hex_to_rgb("#111827") # Deep black glossy pupil
    c_eye_iris   = hex_to_rgb("#3b2014") # Warm dark espresso iris
    c_eye_shine  = hex_to_rgb("#ffffff") # Pure white specular reflection dot
    c_white_hair = hex_to_rgb("#f8fafc") # Fluffy white hair
    c_white_shad = hex_to_rgb("#e2e8f0") # Hair soft shadow
    c_chestnut   = hex_to_rgb("#6b3e26") # Heisenberg chestnut brown hair
    c_dark_brown = hex_to_rgb("#3a2312") # Schrödinger dark brown hair
    c_silver_hair= hex_to_rgb("#a1a1aa") # Planck distinguished silver hair
    
    # Character-specific clothing palettes
    c_grey_knit  = hex_to_rgb("#64748b") # Einstein heather grey sweater
    c_brown_pant = hex_to_rgb("#4a3728") # Einstein brown trousers
    c_tuxedo     = hex_to_rgb("#18181b") # Planck black tuxedo coat
    c_white_shirt= hex_to_rgb("#fdfcf7") # Crisp white dress shirt
    c_black_tie  = hex_to_rgb("#09090b") # Black bowtie
    c_blue_cardi = hex_to_rgb("#2563eb") # Heisenberg royal blue cardigan
    c_blue_tie   = hex_to_rgb("#1e3a8a") # Navy blue tie
    c_tan_chino  = hex_to_rgb("#a89078") # Tan trousers
    c_green_vest = hex_to_rgb("#166534") # Schrödinger dark green vest
    c_gold_orb   = hex_to_rgb("#fbbf24") # Glowing quantum orb
    c_gold_core  = hex_to_rgb("#fffbeb") # Intense core of orb
    c_cyan_atom  = hex_to_rgb("#00e5ff") # Glowing uncertainty ring
    c_cat_ginger = hex_to_rgb("#ea580c") # Schrödinger ginger cat
    c_cat_white  = hex_to_rgb("#fff7ed") # Cat cream muzzle & paws
    c_cat_pink   = hex_to_rgb("#f472b6") # Cat pink inner ears & nose
    c_box_kraft  = hex_to_rgb("#d97706") # Kraft cardboard box
    c_slate_board= hex_to_rgb("#1e293b") # Chalkboard slate
    c_chalk_text = hex_to_rgb("#f8fafc") # White chalk text

    def get_character_subzone(cx, cy, cz, key):
        # 1. Base Plinth & Brass Nameplate
        if cz <= 10.0:
            if cy < -16.0 and cz >= 3.0 and cz <= 8.5:
                # Nameplate brass with dark beveled frame
                if np.abs(cx) < 20.0:
                    return c_brass
                else:
                    return c_brass_edge
            elif cz > 7.5:
                return c_walnut_top
            else:
                return c_walnut

        # 2. Shoes
        if cz < 14.5 and np.abs(cy) < 13.0:
            if key in ['einstein', 'heisenberg']:
                return hex_to_rgb("#2d1a10") # Dark brown leather
            else:
                return hex_to_rgb("#111827") # Polished black oxford

        # 3. Trousers
        if cz < 25.0:
            if key == 'einstein':
                return c_brown_pant
            elif key == 'planck':
                return hex_to_rgb("#27272a") # Dark formal trousers
            elif key == 'heisenberg':
                return c_tan_chino
            else:
                return hex_to_rgb("#475569") # Grey tweed

        # 4. Torso & Clothing
        if cz < 50.0:
            # Props in front of chest (cy > 10.0)
            if cy > 9.5:
                # EINSTEIN: Chalkboard E=mc²
                if key == 'einstein':
                    if np.abs(cx) < 11.0 and cz > 33.0 and cz < 45.0:
                        # Center chalk formula area
                        if cz > 37.5 and cz < 41.0 and np.abs(cx) < 8.0 and cy > 15.5:
                            return c_chalk_text # "E=mc²" chalk
                        return c_slate_board # Dark slate
                    else:
                        return hex_to_rgb("#b45309") # Golden oak frame

                # PLANCK: Glowing Honey-Gold Quantum Orb (hν)
                elif key == 'planck':
                    d_orb = np.sqrt(cx**2 + (cy - 15.0)**2 + (cz - 38.0)**2)
                    if d_orb < 4.0:
                        return c_gold_core
                    elif d_orb < 7.0:
                        return c_gold_orb
                    else:
                        return hex_to_rgb("#f59e0b") # Orbital ring

                # HEISENBERG: Glowing Electric Cyan Uncertainty Atom Orbital
                elif key == 'heisenberg':
                    d_atom = np.sqrt((cx - 13.0)**2 + (cy - 14.0)**2 + (cz - 43.0)**2)
                    if d_atom < 3.8:
                        return hex_to_rgb("#e0f2fe") # Glowing atomic nucleus
                    else:
                        return c_cyan_atom # Orbital cloud

                # SCHRÖDINGER: Cat in Box
                elif key == 'schrodinger':
                    # Cat head & ears peeking out
                    if cz > 42.0:
                        # Pink ears
                        if cz > 48.0 and (np.abs(cx - 8.0) > 2.5):
                            return c_cat_pink
                        # Cute pink nose
                        elif cy > 17.5 and cz > 44.5 and cz < 46.5 and np.abs(cx - 8.0) < 1.5:
                            return c_cat_pink
                        # White muzzle & paws
                        elif cy > 16.5 or cz < 43.5:
                            return c_cat_white
                        else:
                            return c_cat_ginger
                    else:
                        # Cardboard box with black psi symbol
                        if cy > 18.5 and np.abs(cx - 8.0) < 3.0 and cz > 34.0 and cz < 38.0:
                            return hex_to_rgb("#1e293b") # "Ψ?" label
                        return c_box_kraft

            # Body Clothing (Sweater / Tuxedo / Cardigan / Vest)
            if key == 'einstein':
                # Grey knit sweater with subtle ribbed texture
                rib = 0.05 * np.sin(cz * 2.0)
                return c_grey_knit * (1.0 + rib)
            elif key == 'planck':
                if cy > 5.5 and cz > 42.0 and np.abs(cx) < 4.0:
                    if cz > 44.0:
                        return c_black_tie # Bowtie
                    return c_white_shirt # White shirt bib
                return c_tuxedo # Black coat
            elif key == 'heisenberg':
                if cy > 5.5 and cz > 38.0 and np.abs(cx) < 3.5:
                    if np.abs(cx) < 1.5 and cz < 44.0:
                        return c_blue_tie # Necktie
                    return c_white_shirt
                return c_blue_cardi # Blue cardigan
            else:
                # Schrödinger: green argyle vest over shirt
                if cy > 5.5 and cz > 43.0 and np.abs(cx) < 3.5:
                    return c_white_shirt
                # Argyle pattern simulation
                argyle = 0.12 * np.sin(cx * 0.8) * np.sin(cz * 0.8)
                return c_green_vest * (1.0 + argyle)

        # 5. Head, Facial Features, Eyes, and Hair
        # Head center: (0, 0, 62)
        dist_radial = np.sqrt(cx**2 + cy**2)

        # A. Hair
        is_hair = False
        if cz > 71.0 or cy < -6.0 or (dist_radial > 17.5 and cy < 8.0):
            is_hair = True
        if key == 'einstein' and (cz > 65.0 and dist_radial > 15.0):
            is_hair = True # Fluffy white curls expand wider

        if is_hair:
            if key == 'einstein':
                # White fluffy hair with soft ambient shadow
                curl = 0.08 * np.sin(cx * 1.5) * np.cos(cz * 1.5)
                return np.clip(c_white_hair * (0.95 + curl), 0.0, 1.0)
            elif key == 'planck':
                return c_silver_hair
            elif key == 'heisenberg':
                wavy = 0.08 * np.sin(cz * 1.2 + cx * 0.5)
                return c_chestnut * (1.0 + wavy)
            else:
                return c_dark_brown

        # B. Mustache
        if cy > 14.5 and cz > 53.5 and cz < 58.5:
            if key == 'einstein':
                return c_white_hair
            elif key == 'planck':
                return c_silver_hair

        # C. Spectacles (Planck & Schrödinger)
        if (key in ['planck', 'schrodinger']) and cy > 16.5 and cz > 57.5 and cz < 65.5:
            d_lens_l = np.sqrt((cx + 6.6)**2 + (cz - 61.5)**2)
            d_lens_r = np.sqrt((cx - 6.6)**2 + (cz - 61.5)**2)
            if (d_lens_l > 4.6 and d_lens_l < 6.0) or (d_lens_r > 4.6 and d_lens_r < 6.0) or (np.abs(cx) < 2.5 and np.abs(cz - 61.5) < 1.0):
                return hex_to_rgb("#374151") # Wireframe rim & bridge

        # D. Eyes with Glossy Pupil, Iris, and Specular Highlight
        if cy > 14.8 and cz > 58.0 and cz < 64.5:
            for side in [-1, 1]:
                eye_cx = side * 7.5
                eye_cz = 61.5
                d_eye = np.sqrt((cx - eye_cx)**2 + (cz - eye_cz)**2)
                if d_eye < 4.2:
                    # Specular Highlight Dot (top-right of pupil)
                    d_shine = np.sqrt((cx - (eye_cx + 1.2))**2 + (cz - (eye_cz + 1.2))**2)
                    if d_shine < 1.1:
                        return c_eye_shine # Pure white sparkle
                    elif d_eye < 2.2:
                        return c_eye_pupil # Deep dark pupil
                    else:
                        return c_eye_iris # Warm rich iris

        # E. Soft Button Nose
        if cy > 16.5 and cz > 58.0 and cz < 61.5 and np.abs(cx) < 2.5:
            return c_nose_tip

        # F. Rosy Blush Cheeks
        if cy > 9.0 and cz > 54.0 and cz < 60.0 and np.abs(cx) > 8.0 and np.abs(cx) < 17.0:
            return c_skin_blush

        # G. Base Skin Tone
        return c_skin_base

    # Process all vertices
    if char_key == 'diorama':
        # Coordinates in diorama:
        # Einstein: X in [-105, -52] (center -78)
        # Planck:   X in [-52, 0]    (center -26)
        # Heisenberg: X in [0, 52]   (center +26)
        # Schrödinger: X in [52, 105](center +78)
        for i in range(count):
            vx, vy, vz = X[i], Y[i], Z[i]
            if vx < -52.0:
                col = get_character_subzone(vx + 78.0, vy, vz, 'einstein')
            elif vx < 0.0:
                col = get_character_subzone(vx + 26.0, vy, vz, 'planck')
                if vy > 10.0 and np.sqrt((vx + 26.0)**2 + (vy - 15.0)**2 + (vz - 38.0)**2) < 7.0:
                    emissive[i] = [1.0, 0.75, 0.15] # Glowing honey gold
            elif vx < 52.0:
                col = get_character_subzone(vx - 26.0, vy, vz, 'heisenberg')
                if vy > 10.0 and np.sqrt((vx - 26.0 - 13.0)**2 + (vy - 14.0)**2 + (vz - 43.0)**2) < 10.0:
                    emissive[i] = [0.0, 0.9, 1.0] # Glowing cyan
            else:
                col = get_character_subzone(vx - 78.0, vy, vz, 'schrodinger')
            colors[i, :3] = col
            colors[i, 3] = 1.0
    else:
        for i in range(count):
            vx, vy, vz = X[i], Y[i], Z[i]
            col = get_character_subzone(vx, vy, vz, char_key)
            colors[i, :3] = col
            colors[i, 3] = 1.0
            
            # Set Emissive flags for glowing props
            if char_key == 'planck' and vy > 10.0 and np.sqrt(vx**2 + (vy - 15.0)**2 + (vz - 38.0)**2) < 7.0:
                emissive[i] = [1.0, 0.75, 0.15]
            elif char_key == 'heisenberg' and vy > 10.0 and np.sqrt((vx - 13.0)**2 + (vy - 14.0)**2 + (vz - 43.0)**2) < 10.0:
                emissive[i] = [0.0, 0.9, 1.0]

    return colors, emissive

# ------------------------------------------------------------------------------
# 2. GLB (glTF 2.0 BINARY) EXPORTER WITH FULL PBR MATERIALS
# ------------------------------------------------------------------------------

def export_full_color_glb(filepath, verts, faces, normals, colors, emissive=None, model_name="QuantumChibi"):
    """
    Exports a binary glTF 2.0 (.glb) with embedded PBR metallic-roughness materials
    and per-vertex photorealistic color attributes.
    """
    v_pos = verts.astype(np.float32)
    v_norm = normals.astype(np.float32)
    v_col = colors.astype(np.float32) # (N, 4)
    f_ind = faces.flatten().astype(np.uint32)

    min_pos = v_pos.min(axis=0).tolist()
    max_pos = v_pos.max(axis=0).tolist()

    # Build binary buffer
    bin_buf = bytearray()
    
    # Position bufferView
    pos_offset = len(bin_buf)
    bin_buf.extend(v_pos.tobytes())
    pos_length = len(bin_buf) - pos_offset

    # Normal bufferView
    norm_offset = len(bin_buf)
    bin_buf.extend(v_norm.tobytes())
    norm_length = len(bin_buf) - norm_offset

    # Color bufferView
    col_offset = len(bin_buf)
    bin_buf.extend(v_col.tobytes())
    col_length = len(bin_buf) - col_offset

    # Indices bufferView
    ind_offset = len(bin_buf)
    bin_buf.extend(f_ind.tobytes())
    ind_length = len(bin_buf) - ind_offset

    # 4-byte alignment
    while len(bin_buf) % 4 != 0:
        bin_buf.append(0)

    # glTF JSON Document
    gltf = {
        "asset": {
            "version": "2.0",
            "generator": "AI4D_AgriPhysics_QuantumChibi_Engine_v2.0"
        },
        "scene": 0,
        "scenes": [{"name": "QuantumChibiScene", "nodes": [0]}],
        "nodes": [{"name": model_name, "mesh": 0}],
        "meshes": [{
            "name": f"{model_name}_Mesh",
            "primitives": [{
                "attributes": {
                    "POSITION": 0,
                    "NORMAL": 1,
                    "COLOR_0": 2
                },
                "indices": 3,
                "material": 0,
                "mode": 4 # TRIANGLES
            }]
        }],
        "materials": [{
            "name": f"{model_name}_PixarPBR",
            "pbrMetallicRoughness": {
                "baseColorFactor": [1.0, 1.0, 1.0, 1.0],
                "roughnessFactor": 0.42,
                "metallicFactor": 0.15
            },
            "emissiveFactor": [0.0, 0.0, 0.0],
            "doubleSided": False
        }],
        "buffers": [{"byteLength": len(bin_buf)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": pos_offset, "byteLength": pos_length, "target": 34962},
            {"buffer": 0, "byteOffset": norm_offset, "byteLength": norm_length, "target": 34962},
            {"buffer": 0, "byteOffset": col_offset, "byteLength": col_length, "target": 34962},
            {"buffer": 0, "byteOffset": ind_offset, "byteLength": ind_length, "target": 34963}
        ],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(v_pos), "type": "VEC3", "min": min_pos, "max": max_pos},
            {"bufferView": 1, "componentType": 5126, "count": len(v_norm), "type": "VEC3"},
            {"bufferView": 2, "componentType": 5126, "count": len(v_col), "type": "VEC4"},
            {"bufferView": 3, "componentType": 5125, "count": len(f_ind), "type": "SCALAR"}
        ]
    }

    json_str = json.dumps(gltf, separators=(',', ':'))
    json_bytes = json_str.encode('utf-8')
    while len(json_bytes) % 4 != 0:
        json_bytes += b' '

    total_length = 12 + 8 + len(json_bytes) + 8 + len(bin_buf)
    
    # 12-byte header
    glb_header = struct.pack('<4sII', b'glTF', 2, total_length)
    # JSON chunk
    chunk0 = struct.pack('<I4s', len(json_bytes), b'JSON') + json_bytes
    # BIN chunk
    chunk1 = struct.pack('<I4s', len(bin_buf), b'BIN\0') + bytes(bin_buf)

    with open(filepath, 'wb') as f:
        f.write(glb_header)
        f.write(chunk0)
        f.write(chunk1)

    print(f"Exported PBR Colored GLB: {filepath} ({os.path.getsize(filepath) / (1024*1024):.2f} MB)")

# ------------------------------------------------------------------------------
# 3. COLOR PLY EXPORTER
# ------------------------------------------------------------------------------

def export_color_ply(filepath, verts, faces, colors):
    """Exports full-color binary PLY with per-vertex RGB."""
    num_verts = len(verts)
    num_faces = len(faces)
    rgb_uint8 = np.clip(colors[:, :3] * 255.0, 0, 255).astype(np.uint8)

    header = (
        "ply\n"
        "format binary_little_endian 1.0\n"
        "comment AI4D AgriPhysics Quantum Chibi Colored 3D Mesh\n"
        f"element vertex {num_verts}\n"
        "property float x\n"
        "property float y\n"
        "property float z\n"
        "property uchar red\n"
        "property uchar green\n"
        "property uchar blue\n"
        f"element face {num_faces}\n"
        "property list uchar int vertex_indices\n"
        "end_header\n"
    ).encode('ascii')

    with open(filepath, 'wb') as f:
        f.write(header)
        # Write vertices (3 floats + 3 uchar)
        for i in range(num_verts):
            f.write(struct.pack('<fffBBB', verts[i, 0], verts[i, 1], verts[i, 2],
                                rgb_uint8[i, 0], rgb_uint8[i, 1], rgb_uint8[i, 2]))
        # Write faces (1 uchar=3 + 3 ints)
        for i in range(num_faces):
            f.write(struct.pack('<Biii', 3, faces[i, 0], faces[i, 1], faces[i, 2]))

    print(f"Exported Color PLY: {filepath} ({os.path.getsize(filepath) / (1024*1024):.2f} MB)")

# ------------------------------------------------------------------------------
# 4. MAIN WORKFLOW
# ------------------------------------------------------------------------------

def process_character_model(char_key, base_dir):
    t0 = time.time()
    chibi_dir = os.path.join(base_dir, "models_3d", "quantum_physicists_chibi")
    
    # Grid domain
    if char_key == 'diorama':
        res = 0.75
        x_min, x_max = -115.0, 115.0
        y_min, y_max = -26.0, 26.0
        z_min, z_max = 0.0, 92.0
    else:
        res = 0.55
        x_min, x_max = -30.0, 30.0
        y_min, y_max = -24.0, 24.0
        z_min, z_max = 0.0, 90.0

    nx = int(np.ceil((x_max - x_min) / res)) + 1
    ny = int(np.ceil((y_max - y_min) / res)) + 1
    nz = int(np.ceil((z_max - z_min) / res)) + 1

    x = np.linspace(x_min, x_max, nx)
    y = np.linspace(y_min, y_max, ny)
    z = np.linspace(z_min, z_max, nz)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    print(f"\n>>> Processing Full-Color 3D Mesh: [{char_key.upper()}] <<<")
    if char_key == 'einstein':
        dist = build_albert_einstein_sdf(X, Y, Z)
    elif char_key == 'planck':
        dist = build_max_planck_sdf(X, Y, Z)
    elif char_key == 'heisenberg':
        dist = build_werner_heisenberg_sdf(X, Y, Z)
    elif char_key == 'schrodinger':
        dist = build_erwin_schrodinger_sdf(X, Y, Z)
    elif char_key == 'diorama':
        dist = build_quantum_diorama_sdf(X, Y, Z)

    # Marching Cubes
    dx = (x_max - x_min) / (nx - 1)
    dy = (y_max - y_min) / (ny - 1)
    dz = (z_max - z_min) / (nz - 1)

    dist_padded = np.pad(dist, 1, mode='constant', constant_values=10.0)
    verts, faces, normals, _ = measure.marching_cubes(dist_padded, level=0.0, spacing=(dx, dy, dz))

    verts[:, 0] += (x_min - dx)
    verts[:, 1] += (y_min - dy)
    verts[:, 2] += (z_min - dz)
    verts[:, 2] -= verts[:, 2].min() # Floor align

    # Compute Pixar/Ghibli photorealistic colors
    colors, emissive = compute_photorealistic_colors(verts, char_key=char_key)

    # Export Full-Color GLB
    glb_name = f"{char_key}_chibi_colored.glb" if char_key != 'diorama' else "quantum_quartet_diorama_colored.glb"
    glb_path = os.path.join(chibi_dir, glb_name)
    export_full_color_glb(glb_path, verts, faces, normals, colors, emissive=emissive, model_name=f"Quantum_{char_key.capitalize()}")

    # Export Color PLY
    ply_name = f"{char_key}_chibi_colored.ply" if char_key != 'diorama' else "quantum_quartet_diorama_colored.ply"
    ply_path = os.path.join(chibi_dir, ply_name)
    export_color_ply(ply_path, verts, faces, colors)

    print(f"Finished [{char_key.upper()}] in {time.time() - t0:.2f}s")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for char in ['einstein', 'planck', 'heisenberg', 'schrodinger', 'diorama']:
        process_character_model(char, base_dir)
    print("\n[ALL DONE] All 5 Full-Color PBR GLB and PLY models generated successfully!")
