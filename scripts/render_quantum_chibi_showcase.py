#!/usr/bin/env python3
"""
==============================================================================
🎨 QUANTUM PHYSICISTS CHIBI 3D SHOWCASE RENDERER
🔬 Albert Einstein • Max Planck • Werner Heisenberg • Erwin Schrödinger
🏛️ หน่วยวิจัยฟิสิกส์เกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics) มรภ.รำไพพรรณี
==============================================================================
Renders high-resolution 4-panel visual comparison of the 3D STL meshes.
"""

import os
import struct
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = ['Sarabun', 'Thonburi', 'DejaVu Sans']
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def read_binary_stl(filepath):
    """Reads binary STL and returns vertices and faces."""
    with open(filepath, 'rb') as f:
        _ = f.read(80) # Header
        num_triangles = struct.unpack('<I', f.read(4))[0]
        data = f.read(num_triangles * 50)
        
    records = struct.iter_unpack('<3f3f3f3fH', data)
    triangles = []
    for r in records:
        triangles.append([
            [r[3], r[4], r[5]],
            [r[6], r[7], r[8]],
            [r[9], r[10], r[11]]
        ])
    return np.array(triangles)

def compute_shaded_facecolors(triangles, base_rgb, light_dir=(0.5, -0.6, 0.8), ambient=0.45):
    """Computes directional diffuse shading for 3D collection."""
    v0 = triangles[:, 0]
    v1 = triangles[:, 1]
    v2 = triangles[:, 2]
    normals = np.cross(v1 - v0, v2 - v0)
    norm_lens = np.linalg.norm(normals, axis=1, keepdims=True)
    norm_lens[norm_lens < 1e-8] = 1.0
    normals /= norm_lens

    l = np.array(light_dir)
    l /= np.linalg.norm(l)
    diffuse = np.maximum(0.0, np.dot(normals, l))
    intensity = np.clip(ambient + (1.0 - ambient) * diffuse, 0.0, 1.0)
    
    colors = np.zeros((len(triangles), 4))
    colors[:, 0] = base_rgb[0] * intensity
    colors[:, 1] = base_rgb[1] * intensity
    colors[:, 2] = base_rgb[2] * intensity
    colors[:, 3] = 1.0
    return colors

def render_showcase(target_png):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chibi_dir = os.path.join(base_dir, "models_3d", "quantum_physicists_chibi")
    
    configs = [
        {
            "stl": os.path.join(chibi_dir, "einstein_chibi_3d.stl"),
            "name": "Albert Einstein",
            "title": "อัลเบิร์ต ไอน์สไตน์ (Albert Einstein)",
            "subtitle": "บิดาแห่งทฤษฎีสัมพัทธภาพ & ปรากฏการณ์โฟโตอิเล็กทริก",
            "formula": "E = mc²  |  hν = W + Ek",
            "prop": "กระดานชนวนชอล์ก E=mc² • ทรงผมฟูฟ่อง • หนวดหนา",
            "color": [0.85, 0.65, 0.55], # Warm coral terracotta
            "badge": "#f59e0b"
        },
        {
            "stl": os.path.join(chibi_dir, "planck_chibi_3d.stl"),
            "name": "Max Planck",
            "title": "มักซ์ พลังค์ (Max Planck)",
            "subtitle": "ผู้ให้กำเนิดแนวคิดควอนตัมแห่งพลังงาน (E = nhν)",
            "formula": "E = hν  |  h = 6.626 × 10⁻³⁴ J·s",
            "prop": "ลูกแก้วพลังงานควอนตัมเรืองแสง • แว่นตาหนีบจมูก • สูททักซิโด้",
            "color": [0.80, 0.72, 0.50], # Warm golden brass
            "badge": "#eab308"
        },
        {
            "stl": os.path.join(chibi_dir, "heisenberg_chibi_3d.stl"),
            "name": "Werner Heisenberg",
            "title": "แวร์เนอร์ ไฮเซินแบร์ก (Werner Heisenberg)",
            "subtitle": "กลศาสตร์เมทริกซ์ & หลักความไม่แน่นอน",
            "formula": "Δx · Δp ≥ ℏ/2  |  Matrix Mechanics",
            "prop": "วงแหวนออร์บิทัลอะตอมควอนตัม • ทรงผมลอน 1920s • เนกไท",
            "color": [0.45, 0.75, 0.88], # Quantum cyan blue
            "badge": "#06b6d4"
        },
        {
            "stl": os.path.join(chibi_dir, "schrodinger_chibi_3d.stl"),
            "name": "Erwin Schrödinger",
            "title": "แอร์วิน ชเรอดิงเงอร์ (Erwin Schrödinger)",
            "subtitle": "กลศาสตร์คลื่น & การทดลองทางความคิดแมวชเรอดิงเงอร์",
            "formula": "iℏ ∂ψ/∂t = Ĥψ  |  Schrödinger's Cat",
            "prop": "กล่องทดลองพร้อมน้องแมวโผล่หัว • แว่นตากลม • เสื้อกั๊กไหมพรม",
            "color": [0.55, 0.82, 0.60], # Emerald sage green
            "badge": "#10b981"
        }
    ]

    fig = plt.figure(figsize=(26, 14), facecolor='#070b14')
    
    # Master Header
    plt.figtext(0.5, 0.965, "THE QUANTUM QUARTET • 3D CHIBI PIXAR/GHIBLI FIGURINE COLLECTION",
                fontsize=22, fontweight='bold', color='#00e5ff', ha='center')
    plt.figtext(0.5, 0.938, "แบบจำลอง 3 มิติหัวโตสไตล์พิกซาร์-จิบลิ: สี่บิดาแห่งฟิสิกส์ควอนตัม • หน่วยวิจัยฟิสิกส์เกษตรดิจิทัล AI4D AgriPhysics มรภ.รำไพพรรณี",
                fontsize=13, color='#94a3b8', ha='center')

    for idx, cfg in enumerate(configs):
        ax = fig.add_subplot(1, 4, idx + 1, projection='3d', facecolor='#070b14')
        ax.set_box_aspect([1, 1, 1.4])
        
        # Load mesh
        triangles = read_binary_stl(cfg["stl"])
        # Downsample for fast vector rendering if needed (step of 2)
        step = max(1, len(triangles) // 35000)
        tri_sub = triangles[::step]
        
        facecolors = compute_shaded_facecolors(tri_sub, cfg["color"], light_dir=(0.4, -0.6, 0.8), ambient=0.42)
        
        mesh_col = Poly3DCollection(tri_sub, facecolors=facecolors, edgecolors='none', shade=False)
        ax.add_collection3d(mesh_col)
        
        # Limits
        ax.set_xlim(-28, 28)
        ax.set_ylim(-25, 25)
        ax.set_zlim(0, 92)
        
        # Camera angle (charming front isometric view)
        ax.view_init(elev=18, azim=-62)
        ax.axis('off')
        
        # Panel Title Card
        y_pos = 0.22
        plt.figtext(0.125 + idx * 0.25, y_pos, cfg["title"],
                    fontsize=14, fontweight='bold', color='#ffffff', ha='center')
        plt.figtext(0.125 + idx * 0.25, y_pos - 0.024, cfg["subtitle"],
                    fontsize=10.5, color='#94a3b8', ha='center')
        
        # Formula Badge
        plt.figtext(0.125 + idx * 0.25, y_pos - 0.052, f"  {cfg['formula']}  ",
                    fontsize=11, fontweight='bold', color=cfg['badge'], ha='center',
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='#0f172a', edgecolor=cfg['badge'], linewidth=1.2))
        
        # Props detail
        plt.figtext(0.125 + idx * 0.25, y_pos - 0.086, f"✦ พร็อพเด่น: {cfg['prop']}",
                    fontsize=9.5, color='#cbd5e1', ha='center')
        plt.figtext(0.125 + idx * 0.25, y_pos - 0.110, f"✦ ขนาด: สเกลจำลอง 90 mm | 100% Watertight Solid",
                    fontsize=8.5, color='#64748b', ha='center')

    # Footer note
    plt.figtext(0.5, 0.025, "Marching Cubes SDF 3D Engine • 100% Watertight Manifold Topology • 3D Printing Ready (FDM / Resin SLA)",
                fontsize=10, color='#64748b', ha='center')

    plt.subplots_adjust(left=0.02, right=0.98, top=0.91, bottom=0.25, wspace=0.02)
    os.makedirs(os.path.dirname(target_png), exist_ok=True)
    plt.savefig(target_png, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Showcase graphic saved to: {target_png}")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_img = os.path.join(base_dir, "models_3d", "quantum_physicists_chibi", "quantum_chibi_showcase.png")
    render_showcase(target_img)
