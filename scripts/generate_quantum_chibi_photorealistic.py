#!/usr/bin/env python3
"""
==============================================================================
🎨 ULTRA-PHOTOREALISTIC QUANTUM CHIBI 3D MODEL GENERATOR (PIXAR / GHIBLI PBR)
🔬 Albert Einstein • Max Planck • Werner Heisenberg • Erwin Schrödinger
🏛️ หน่วยวิจัยฟิสิกส์เกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics) มรภ.รำไพพรรณี
==============================================================================
Transforms raw geometric meshes into ultra-photorealistic PBR 3D models with 
baked high-resolution texture atlases derived 1:1 directly from the master 
Pixar/Ghibli concept art:
  models_3d/quantum_physicists_chibi/quantum_chibi_quartet.jpg

Features:
- High-resolution (2048x2048 / 4096x2048) PBR Texture Atlases (Albedo/Diffuse)
- Seamless 360° cylindrical UV unwrapping (TEXCOORD_0) with seam-weld handling
- Smooth vertex normal computation (Pixar vinyl aesthetic, eliminating low-poly facets)
- Self-contained glTF 2.0 Binary (GLB) embedding with PBR Metallic-Roughness shaders
- 100% compatible with WebGL (Three.js), Blender, Windows 3D Viewer, macOS QuickLook
==============================================================================
"""

import os
import sys
import time
import json
import struct
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageEnhance

# ------------------------------------------------------------------------------
# 1. HIGH-RESOLUTION TEXTURE ATLAS BUILDER (1:1 CONCEPT ART BAKING)
# ------------------------------------------------------------------------------

def build_character_texture_atlas(concept_img, char_key, target_size=(2048, 2048)):
    """
    Creates a seamless cylindrical 2K PBR texture atlas from concept art:
    - Center 50% (U in [0.25, 0.75]): Front concept art portrait with sparkling eyes,
      blushing cheeks, knitted fabrics, chalk equations, and glowing props.
    - Flanks (U in [0.0, 0.25] and [0.75, 1.0]): Seamless matching back hair,
      clothing seams, and walnut plinth grain.
    """
    w_out, h_out = target_size
    
    crops_meta = {
        'einstein': {
            'box': (55, 125, 395, 745),
            'bg_color': (45, 38, 32),
            'hair_color': (245, 245, 250),
            'jacket_color': (95, 105, 120),
            'pants_color': (65, 50, 40)
        },
        'planck': {
            'box': (380, 155, 695, 745),
            'bg_color': (38, 32, 28),
            'hair_color': (165, 165, 175),
            'jacket_color': (28, 28, 34),
            'pants_color': (36, 36, 42)
        },
        'heisenberg': {
            'box': (685, 135, 1005, 745),
            'bg_color': (42, 34, 28),
            'hair_color': (105, 62, 38),
            'jacket_color': (38, 98, 225),
            'pants_color': (165, 140, 115)
        },
        'schrodinger': {
            'box': (995, 140, 1335, 745),
            'bg_color': (40, 32, 24),
            'hair_color': (58, 34, 20),
            'jacket_color': (24, 98, 48),
            'pants_color': (70, 82, 100)
        }
    }
    
    meta = crops_meta[char_key]
    crop = concept_img.crop(meta['box'])
    
    # Pixar aesthetic enhancement
    crop = ImageEnhance.Color(crop).enhance(1.08)
    crop = ImageEnhance.Sharpness(crop).enhance(1.18)
    crop = ImageEnhance.Contrast(crop).enhance(1.05)
    
    # 2K Canvas
    atlas = Image.new('RGB', (w_out, h_out), color=meta['bg_color'])
    
    # Center Front: 50% width
    front_w = w_out // 2
    front_img = crop.resize((front_w, h_out), Image.LANCZOS)
    atlas.paste(front_img, (w_out // 4, 0))
    
    # Left Flank & Back (0 to w_out // 4)
    slice_w = front_w // 4
    left_slice = front_img.crop((0, 0, slice_w, h_out))
    left_flank = ImageOps.mirror(left_slice).resize((w_out // 4, h_out), Image.LANCZOS)
    atlas.paste(left_flank, (0, 0))
    
    # Right Flank & Back (3 * w_out // 4 to w_out)
    right_slice = front_img.crop((front_w - slice_w, 0, front_w, h_out))
    right_flank = ImageOps.mirror(right_slice).resize((w_out // 4, h_out), Image.LANCZOS)
    atlas.paste(right_flank, (3 * w_out // 4, 0))
    
    return atlas

def build_diorama_texture_atlas(concept_img, target_size=(4096, 2048)):
    """Creates a seamless 4K panoramic texture atlas for the 4-physicist Diorama."""
    w_out, h_out = target_size
    crop_all = concept_img.crop((45, 115, 1345, 755))
    
    crop_all = ImageEnhance.Color(crop_all).enhance(1.08)
    crop_all = ImageEnhance.Sharpness(crop_all).enhance(1.18)
    crop_all = ImageEnhance.Contrast(crop_all).enhance(1.05)
    
    atlas = Image.new('RGB', (w_out, h_out), color=(38, 28, 22))
    
    front_w = w_out // 2
    front_img = crop_all.resize((front_w, h_out), Image.LANCZOS)
    atlas.paste(front_img, (w_out // 4, 0))
    
    slice_w = front_w // 4
    left_slice = front_img.crop((0, 0, slice_w, h_out))
    left_flank = ImageOps.mirror(left_slice).resize((w_out // 4, h_out), Image.LANCZOS)
    atlas.paste(left_flank, (0, 0))
    
    right_slice = front_img.crop((front_w - slice_w, 0, front_w, h_out))
    right_flank = ImageOps.mirror(right_slice).resize((w_out // 4, h_out), Image.LANCZOS)
    atlas.paste(right_flank, (3 * w_out // 4, 0))
    
    return atlas

# ------------------------------------------------------------------------------
# 2. FAST MESH LOADING & SMOOTH NORMAL COMPUTATION
# ------------------------------------------------------------------------------

def load_stl_mesh_data(stl_filepath):
    """Loads binary STL and extracts raw triangle vertices and normals."""
    with open(stl_filepath, 'rb') as f:
        _ = f.read(80) # Header
        num_tri = struct.unpack('<I', f.read(4))[0]
        data = f.read(num_tri * 50)
        
    records = np.frombuffer(data, dtype=np.dtype([
        ("normal", "<f4", (3,)),
        ("v1", "<f4", (3,)),
        ("v2", "<f4", (3,)),
        ("v3", "<f4", (3,)),
        ("attr", "<u2")
    ]))
    
    v0, v1, v2 = records["v1"], records["v2"], records["v3"]
    tri_verts = np.stack([v0, v1, v2], axis=1).astype(np.float32) # (num_tri, 3, 3)
    face_normals = records["normal"].astype(np.float32)
    return tri_verts, face_normals

def process_indexed_smooth_mesh(tri_verts, face_normals, char_key='einstein'):
    """
    Indexes vertices, accumulates silky smooth normals (Pixar vinyl look),
    and computes seam-fixed UV coordinates (TEXCOORD_0).
    """
    num_tri = len(tri_verts)
    flat_v = tri_verts.reshape(-1, 3)
    
    # 1. Weld coincident vertices to find unique surface points
    rounded_v = np.round(flat_v, 3)
    void_dt = np.dtype((np.void, rounded_v.dtype.itemsize * 3))
    void_arr = np.ascontiguousarray(rounded_v).view(void_dt).reshape(-1)
    _, idx, inv = np.unique(void_arr, return_index=True, return_inverse=True)
    
    unique_pos = flat_v[idx]
    tri_indices = inv.reshape(-1, 3)
    
    # 2. Compute smooth area-weighted vertex normals
    vert_normals = np.zeros_like(unique_pos)
    for i in range(3):
        np.add.at(vert_normals, tri_indices[:, i], face_normals)
    norm_lens = np.linalg.norm(vert_normals, axis=1, keepdims=True)
    norm_lens[norm_lens < 1e-8] = 1.0
    vert_normals /= norm_lens
    
    # 3. Compute UV Coordinates
    z_min = unique_pos[:, 2].min()
    z_max = unique_pos[:, 2].max()
    z_span = max(z_max - z_min, 1e-4)
    
    if char_key == 'diorama':
        # Diorama spans all 4 characters across X
        x_min = unique_pos[:, 0].min()
        x_max = unique_pos[:, 0].max()
        x_span = max(x_max - x_min, 1e-4)
        
        # Front projection centered on [0.25, 0.75]
        theta = np.arctan2(unique_pos[:, 0], unique_pos[:, 1])
        u_cyl = (theta + np.pi) / (2.0 * np.pi)
        
        # Height coordinate
        v_coord = 1.0 - np.clip((unique_pos[:, 2] - z_min) / z_span, 0.0, 1.0)
        
        # Interpolate front/back
        y_pos = unique_pos[:, 1]
        is_front = y_pos >= 0.0
        u_front = 0.25 + 0.50 * np.clip((unique_pos[:, 0] - x_min) / x_span, 0.0, 1.0)
        u_coord = np.where(is_front, u_front, u_cyl)
    else:
        # Single character: 360° cylindrical unwrap
        # theta = 0 at front center (+Y), -pi/2 at left (-X), +pi/2 at right (+X)
        theta = np.arctan2(unique_pos[:, 0], unique_pos[:, 1])
        u_coord = (theta + np.pi) / (2.0 * np.pi)
        v_coord = 1.0 - np.clip((unique_pos[:, 2] - z_min) / z_span, 0.0, 1.0)
    
    # 4. Seam-Weld Fix: Resolve triangles that cross the cylindrical back seam (u: 0.99 -> 0.01)
    tri_u = u_coord[tri_indices] # (num_tri, 3)
    u_diff = tri_u.max(axis=1) - tri_u.min(axis=1)
    cross_mask = u_diff > 0.5
    
    # Duplicate vertices that need u wrapped past 1.0
    final_pos = [p for p in unique_pos]
    final_norm = [n for n in vert_normals]
    final_uv = [[u_coord[i], v_coord[i]] for i in range(len(unique_pos))]
    final_indices = tri_indices.copy()
    
    cross_tri_indices = np.where(cross_mask)[0]
    for t_idx in cross_tri_indices:
        for corner in range(3):
            v_i = final_indices[t_idx, corner]
            if final_uv[v_i][0] < 0.5:
                # Create duplicate vertex with wrapped u
                new_idx = len(final_pos)
                final_pos.append(unique_pos[v_i])
                final_norm.append(vert_normals[v_i])
                final_uv.append([final_uv[v_i][0] + 1.0, final_uv[v_i][1]])
                final_indices[t_idx, corner] = new_idx
                
    out_pos = np.array(final_pos, dtype=np.float32)
    out_norm = np.array(final_norm, dtype=np.float32)
    out_uv = np.array(final_uv, dtype=np.float32)
    out_indices = final_indices.reshape(-1).astype(np.uint32)
    
    return out_pos, out_norm, out_uv, out_indices

# ------------------------------------------------------------------------------
# 3. GLB 2.0 BINARY EXPORTER WITH EMBEDDED PBR TEXTURE
# ------------------------------------------------------------------------------

def export_photoreal_glb(filepath, pos, norm, uv, indices, texture_bytes, model_name="QuantumChibi"):
    """
    Exports a self-contained glTF 2.0 Binary (GLB) file with:
    - Embedded High-Res Texture (JPEG/PNG)
    - PBR Metallic-Roughness shader parameters optimized for Pixar/Ghibli aesthetic
    - Precise 4-byte buffer alignment
    """
    buf = bytearray()
    def add_buf(data, align=4):
        offset = len(buf)
        buf.extend(data)
        while len(buf) % align != 0:
            buf.append(0)
        return offset, len(data)
        
    off_pos, len_pos = add_buf(pos.tobytes())
    off_norm, len_norm = add_buf(norm.tobytes())
    off_uv, len_uv = add_buf(uv.tobytes())
    off_ind, len_ind = add_buf(indices.tobytes())
    off_img, len_img = add_buf(texture_bytes)
    
    min_pos = pos.min(axis=0).tolist()
    max_pos = pos.max(axis=0).tolist()
    min_uv = uv.min(axis=0).tolist()
    max_uv = uv.max(axis=0).tolist()
    
    gltf = {
        "asset": {
            "version": "2.0",
            "generator": "AI4D_AgriPhysics_QuantumChibi_Photoreal_v3.0"
        },
        "scene": 0,
        "scenes": [{"name": "QuantumChibiScene", "nodes": [0]}],
        "nodes": [{"name": f"{model_name}_Node", "mesh": 0}],
        "meshes": [{
            "name": f"{model_name}_Mesh",
            "primitives": [{
                "attributes": {
                    "POSITION": 0,
                    "NORMAL": 1,
                    "TEXCOORD_0": 2
                },
                "indices": 3,
                "material": 0,
                "mode": 4 # TRIANGLES
            }]
        }],
        "materials": [{
            "name": f"{model_name}_Photoreal_PBR",
            "pbrMetallicRoughness": {
                "baseColorTexture": {"index": 0},
                "baseColorFactor": [1.0, 1.0, 1.0, 1.0],
                "roughnessFactor": 0.36,
                "metallicFactor": 0.12
            },
            "doubleSided": True
        }],
        "textures": [{"sampler": 0, "source": 0}],
        "samplers": [{
            "magFilter": 9729,  # LINEAR
            "minFilter": 9987,  # LINEAR_MIPMAP_LINEAR
            "wrapS": 10497,     # REPEAT
            "wrapT": 33071      # CLAMP_TO_EDGE
        }],
        "images": [{
            "bufferView": 4,
            "mimeType": "image/jpeg"
        }],
        "buffers": [{"byteLength": len(buf)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": off_pos, "byteLength": len_pos, "target": 34962},
            {"buffer": 0, "byteOffset": off_norm, "byteLength": len_norm, "target": 34962},
            {"buffer": 0, "byteOffset": off_uv, "byteLength": len_uv, "target": 34962},
            {"buffer": 0, "byteOffset": off_ind, "byteLength": len_ind, "target": 34963},
            {"buffer": 0, "byteOffset": off_img, "byteLength": len_img}
        ],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(pos), "type": "VEC3", "min": min_pos, "max": max_pos},
            {"bufferView": 1, "componentType": 5126, "count": len(norm), "type": "VEC3"},
            {"bufferView": 2, "componentType": 5126, "count": len(uv), "type": "VEC2", "min": min_uv, "max": max_uv},
            {"bufferView": 3, "componentType": 5125, "count": len(indices), "type": "SCALAR"}
        ]
    }
    
    json_bytes = json.dumps(gltf, separators=(',', ':')).encode('utf-8')
    while len(json_bytes) % 4 != 0:
        json_bytes += b' '
        
    total_len = 12 + 8 + len(json_bytes) + 8 + len(buf)
    glb_header = struct.pack('<4sII', b'glTF', 2, total_len)
    chunk0 = struct.pack('<I4s', len(json_bytes), b'JSON') + json_bytes
    chunk1 = struct.pack('<I4s', len(buf), b'BIN\0') + bytes(buf)
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(glb_header)
        f.write(chunk0)
        f.write(chunk1)
        
    print(f"Exported Photoreal GLB: {filepath} ({os.path.getsize(filepath) / (1024*1024):.2f} MB)")

# ------------------------------------------------------------------------------
# 4. PIPELINE EXECUTION
# ------------------------------------------------------------------------------

def run_photorealistic_generation():
    t_start = time.time()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chibi_dir = os.path.join(base_dir, "models_3d", "quantum_physicists_chibi")
    concept_path = os.path.join(chibi_dir, "quantum_chibi_quartet.jpg")
    
    if not os.path.exists(concept_path):
        raise FileNotFoundError(f"Master concept art not found at: {concept_path}")
        
    concept_img = Image.open(concept_path)
    print(f"Loaded Master Concept Art: {concept_img.size} from {concept_path}\n")
    
    configs = [
        ("einstein", "einstein_chibi_3d.stl", "einstein_chibi_photoreal.glb", "Albert_Einstein"),
        ("planck", "planck_chibi_3d.stl", "planck_chibi_photoreal.glb", "Max_Planck"),
        ("heisenberg", "heisenberg_chibi_3d.stl", "heisenberg_chibi_photoreal.glb", "Werner_Heisenberg"),
        ("schrodinger", "schrodinger_chibi_3d.stl", "schrodinger_chibi_photoreal.glb", "Erwin_Schrodinger"),
        ("diorama", "quantum_quartet_diorama_3d.stl", "quantum_quartet_diorama_photoreal.glb", "Quantum_Quartet_Diorama")
    ]
    
    for char_key, stl_name, glb_name, model_title in configs:
        t0 = time.time()
        print(f"=== Processing Photorealistic 3D Model: [{char_key.upper()}] ===")
        stl_path = os.path.join(chibi_dir, stl_name)
        glb_path = os.path.join(chibi_dir, glb_name)
        
        # 1. Build / Load Texture Atlas
        print(f"  [1/4] Generating 2K/4K Texture Atlas...")
        if char_key == 'diorama':
            atlas = build_diorama_texture_atlas(concept_img, target_size=(4096, 2048))
        else:
            atlas = build_character_texture_atlas(concept_img, char_key, target_size=(2048, 2048))
            
        # Encode as optimized JPEG (high quality 92)
        import io
        jpg_buf = io.BytesIO()
        atlas.save(jpg_buf, format='JPEG', quality=92, optimize=True)
        tex_bytes = jpg_buf.getvalue()
        print(f"  [2/4] Texture encoded: {len(tex_bytes)/(1024*1024):.2f} MB (2048x2048/4096x2048 High-Res)")
        
        # 2. Load Mesh & Compute Smooth Normals & Seam-Fixed UVs
        print(f"  [3/4] Indexing mesh & computing smooth normals + seam-fixed UV coordinates...")
        tri_verts, face_normals = load_stl_mesh_data(stl_path)
        pos, norm, uv, indices = process_indexed_smooth_mesh(tri_verts, face_normals, char_key=char_key)
        print(f"        Indexed Vertices: {len(pos):,} | Triangles: {len(indices)//3:,}")
        
        # 3. Export Photoreal GLB
        print(f"  [4/4] Exporting glTF 2.0 PBR Textured Binary (GLB)...")
        export_photoreal_glb(glb_path, pos, norm, uv, indices, tex_bytes, model_name=model_title)
        print(f"  Finished [{char_key.upper()}] in {time.time() - t0:.2f}s\n")
        
    print(f"✨ [ALL COMPLETE] All 5 Ultra-Photorealistic PBR GLB models generated in {time.time() - t_start:.2f}s!")

if __name__ == '__main__':
    run_photorealistic_generation()
