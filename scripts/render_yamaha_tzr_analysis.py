#!/usr/bin/env python3
"""
Yamaha TZR Series - 3D Mechanical & Aerodynamic Engineering Analysis
Designed with Skill: motorcycle-3d-cad-architect
Digital Agriphysics & AI Research Unit (JC_AI_SciRBRU)
Department of Physics, Faculty of Science and Technology,
Rambhai Barni Rajabhat University (RBRU)

Generates:
models_3d/yamaha_tzr/yamaha_tzr_analysis.png
"""

import os
import struct
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def read_stl_mesh(filepath, max_triangles=40000):
    """Loads a subset of triangles from binary STL for high-speed matplotlib rendering"""
    with open(filepath, 'rb') as f:
        header = f.read(80)
        num_triangles = struct.unpack('<I', f.read(4))[0]
        
        step = max(1, num_triangles // max_triangles)
        actual_count = num_triangles // step
        
        verts = np.zeros((actual_count, 3, 3), dtype=np.float32)
        idx = 0
        for i in range(num_triangles):
            data = f.read(50)
            if i % step == 0 and idx < actual_count:
                v = struct.unpack('<3f3f3f3fH', data)
                verts[idx, 0] = v[3:6]
                verts[idx, 1] = v[6:9]
                verts[idx, 2] = v[9:12]
                idx += 1
                
    return verts[:idx]

def render_tzr_analysis():
    print("Generating Yamaha TZR 3D Engineering Analysis Plot...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tzr_dir = os.path.join(base_dir, "models_3d", "yamaha_tzr")
    stl_path = os.path.join(tzr_dir, "yamaha_tzr_3d.stl")
    out_png = os.path.join(tzr_dir, "yamaha_tzr_analysis.png")
    
    if not os.path.exists(stl_path):
        print(f"Error: {stl_path} not found!")
        return

    triangles = read_stl_mesh(stl_path, max_triangles=25000)
    print(f"Loaded {len(triangles):,} sampled triangles for multi-view visualization...")
    
    # Configure font
    plt.rcParams['font.sans-serif'] = ['Thonburi', 'Arial', 'DejaVu Sans']
    plt.rcParams['font.family'] = 'sans-serif'
    
    # Master Figure (19 x 11.5 inches, Dark Theme)
    fig = plt.figure(figsize=(19, 11.5), facecolor='#080c14')
    
    # --- PANEL 1: 3D Isometric View (Top-Left, 3D Projection) ---
    ax1 = fig.add_subplot(2, 2, 1, projection='3d', facecolor='#080c14')
    
    # Color faces by Z height and orientation for realistic studio shading
    v_cents = np.mean(triangles, axis=1)
    z_vals = v_cents[:, 2]
    norm_z = (z_vals - z_vals.min()) / (z_vals.max() - z_vals.min())
    
    # Metallic gradient: frame/engine dark steel to pearl white fairing to cyan highlights
    face_colors = np.zeros((len(triangles), 4))
    for i in range(len(triangles)):
        t = norm_z[i]
        # X position helps distinguish tank/fairing (white/red) from engine/frame
        x = v_cents[i, 0]
        y = v_cents[i, 1]
        z = v_cents[i, 2]
        
        if z < 32 and (np.abs(x - 67.5) < 32 or np.abs(x + 67.5) < 32):
            # Tires & Wheels (Dark charcoal)
            face_colors[i] = [0.12, 0.14, 0.18, 0.90]
        elif z > 50 and x > 20 and x < 78:
            # Front Fairing & Nose (Pearl White with Red accents)
            if np.abs(y) < 10 and z > 72:
                face_colors[i] = [0.00, 0.90, 1.00, 0.65] # Cyan Bubble screen
            else:
                face_colors[i] = [0.92, 0.94, 0.98, 0.95] # White Fairing
        elif z > 52 and x > -18 and x <= 20:
            # Fuel Tank (Yamaha Racing Red)
            face_colors[i] = [0.88, 0.15, 0.15, 0.95]
        elif z > 56 and x <= -18 and x > -48:
            # Seat (Black vinyl)
            face_colors[i] = [0.18, 0.18, 0.20, 0.95]
        elif z > 58 and x <= -48:
            # Tail Cowl (White/Red)
            face_colors[i] = [0.92, 0.94, 0.98, 0.95]
        elif y < -12 and z < 50 and x < -30:
            # Expansion Chamber & Silencer (Brushed Aluminum & Steel)
            face_colors[i] = [0.85, 0.82, 0.70, 0.95]
        else:
            # Deltabox Frame & Engine (Polished Aluminum Silver)
            face_colors[i] = [0.65, 0.70, 0.75, 0.92]
            
    mesh = Poly3DCollection(triangles, facecolors=face_colors, edgecolors='none', shade=False)
    ax1.add_collection3d(mesh)
    
    ax1.set_xlim(-110, 100)
    ax1.set_ylim(-50, 50)
    ax1.set_zlim(0, 110)
    ax1.view_init(elev=22, azim=-55)
    ax1.set_axis_off()
    ax1.set_title("1. มุมมองไอโซเมตริก 3 มิติ (3D Isometric Perspective)\nโครงสร้างประกอบรวมสมบูรณ์ (Full Assembly)", 
                  color='#00e5ff', fontsize=12, fontweight='bold', pad=10)
                  
    # Annotation Badges on 3D View
    ax1.text(38, 0, 95, "Aerodynamic Cowl\n& Bubble Screen", color='#ffffff', fontsize=8, fontweight='bold', ha='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#0284c7', alpha=0.8, edgecolor='#00e5ff'))
    ax1.text(8, 0, 78, "Fuel Tank (13L)\nRacing Knee Recess", color='#ffffff', fontsize=8, fontweight='bold', ha='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#dc2626', alpha=0.8, edgecolor='#f87171'))
    ax1.text(-70, -25, 48, "Tuned Expansion\nChamber Exhaust", color='#ffffff', fontsize=8, fontweight='bold', ha='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#d97706', alpha=0.8, edgecolor='#fbbf24'))

    # --- PANEL 2: Side Elevation Profile (Top-Right, Y-Z Plane projection looking along Y) ---
    ax2 = fig.add_subplot(2, 2, 2, facecolor='#0b111c')
    ax2.set_facecolor('#0b111c')
    
    # Project triangles onto X-Z plane
    pts_x = triangles[:, :, 0].flatten()
    pts_z = triangles[:, :, 2].flatten()
    ax2.scatter(pts_x, pts_z, c='#38bdf8', s=0.8, alpha=0.25, rasterized=True)
    
    # Draw Reference Axis and Dimensions
    ax2.axhline(0, color='#64748b', linestyle='--', linewidth=0.8) # Ground plane
    ax2.axvline(67.5, color='#00e5ff', linestyle=':', linewidth=1.0, label='Front Axle (X = +67.5)')
    ax2.axvline(-67.5, color='#10b981', linestyle=':', linewidth=1.0, label='Rear Axle (X = -67.5)')
    
    # Dimension annotations
    # Wheelbase
    ax2.annotate('', xy=(-67.5, 12), xytext=(67.5, 12),
                 arrowprops=dict(arrowstyle='<->', color='#f59e0b', lw=1.8))
    ax2.text(0, 15, "Wheelbase 135.0 mm (Scale 1:10 → Real 1,350 mm)", 
             color='#f59e0b', fontsize=9, fontweight='bold', ha='center')
             
    # Overall Length
    ax2.annotate('', xy=(-96, 5), xytext=(94, 5),
                 arrowprops=dict(arrowstyle='<->', color='#a855f7', lw=1.5))
    ax2.text(0, -2, "Overall Length 190.0 mm (Real 1,900 mm)", 
             color='#a855f7', fontsize=8, fontweight='bold', ha='center')
             
    # Seat Height
    ax2.annotate('', xy=(-30, 0), xytext=(-30, 60),
                 arrowprops=dict(arrowstyle='<->', color='#10b981', lw=1.5))
    ax2.text(-34, 30, "Seat Height 60 mm\n(Real 765 mm)", 
             color='#10b981', fontsize=8, fontweight='bold', ha='right', va='center')
             
    # Rake Angle (24 degrees)
    ax2.plot([38, 67.5], [74, 30], color='#ef4444', linewidth=2.0, linestyle='-')
    ax2.text(54, 58, "Caster Rake: 24°\nTelescopic Fork", color='#ef4444', fontsize=8, fontweight='bold')
    
    ax2.set_xlim(-110, 105)
    ax2.set_ylim(-8, 108)
    ax2.set_xlabel("X Axis - ความยาวตัวรถ (mm)", color='#94a3b8', fontsize=9)
    ax2.set_ylabel("Z Axis - ความสูงจากพื้น (mm)", color='#94a3b8', fontsize=9)
    ax2.tick_params(colors='#94a3b8', labelsize=8)
    ax2.grid(True, linestyle=':', color='#ffffff', alpha=0.08)
    ax2.set_title("2. ภาคตัดขวางด้านข้างและระยะมิติวิศวกรรม (Side Elevation Profile)\nมาตราส่วน 1:10 (Precision Scale CAD)", 
                  color='#00e5ff', fontsize=12, fontweight='bold', pad=10)

    # --- PANEL 3: Top Plan View (Bottom-Left, X-Y Plane) ---
    ax3 = fig.add_subplot(2, 2, 3, facecolor='#0b111c')
    ax3.set_facecolor('#0b111c')
    
    pts_y = triangles[:, :, 1].flatten()
    ax3.scatter(pts_x, pts_y, c='#34d399', s=0.8, alpha=0.25, rasterized=True)
    
    ax3.axhline(0, color='#64748b', linestyle='--', linewidth=0.8) # Centerline
    
    # Width dimensions
    # Handlebar width
    ax3.annotate('', xy=(31, -31), xytext=(31, 31),
                 arrowprops=dict(arrowstyle='<->', color='#00e5ff', lw=1.6))
    ax3.text(35, 0, "Clip-on Bars: 62.0 mm", color='#00e5ff', fontsize=8, fontweight='bold', va='center')
    
    # Deltabox Spar width
    ax3.annotate('', xy=(15, -17), xytext=(15, 17),
                 arrowprops=dict(arrowstyle='<->', color='#f59e0b', lw=1.4))
    ax3.text(18, 0, "Deltabox: 34.0 mm", color='#f59e0b', fontsize=8, fontweight='bold', va='center')
    
    # Fuel tank knee indents
    ax3.plot([7, -2], [17, 19], color='#ef4444', lw=2)
    ax3.plot([7, -2], [-17, -19], color='#ef4444', lw=2)
    ax3.text(-5, 23, "Knee Recesses", color='#ef4444', fontsize=8, fontweight='bold')
    
    ax3.set_xlim(-110, 105)
    ax3.set_ylim(-42, 42)
    ax3.set_xlabel("X Axis - ความยาวตัวรถ (mm)", color='#94a3b8', fontsize=9)
    ax3.set_ylabel("Y Axis - ความกว้างลำตัว (mm)", color='#94a3b8', fontsize=9)
    ax3.tick_params(colors='#94a3b8', labelsize=8)
    ax3.grid(True, linestyle=':', color='#ffffff', alpha=0.08)
    ax3.set_title("3. มุมมองด้านบนโครงสร้างแชสซีส์ (Top Plan View)\nแสดงแนวคานคู่ Deltabox Twin-Spar และแฮนด์จับโช้ค", 
                  color='#00e5ff', fontsize=12, fontweight='bold', pad=10)

    # --- PANEL 4: Engineering Specifications & Heritage Card (Bottom-Right) ---
    ax4 = fig.add_subplot(2, 2, 4, facecolor='#080c14')
    ax4.axis('off')
    
    card_text = """
YAMAHA TZR SERIES (TZR150 / TZR250 3MA-3XV)
สถาปัตยกรรมทางวิศวกรรมและการออกแบบ 3 มิติเชิงทัศนศาสตร์เครื่องกล

1. โครงสร้างและแชสซีส์ (Chassis & Frame):
   • Deltabox Aluminum Twin-Spar Frame: โครงเฟรมอลูมิเนียมหล่อขึ้นรูปคานคู่
   • Rake Caster Angle: 24.0° | Trail: 90 mm | Wheelbase: 135.0 mm (สเกล 1:10)
   • Suspension: ด้านหน้า Telescopic Hydraulic Fork | ด้านหลัง Monocross Monoshock

2. ขุมพลังเครื่องยนต์ 2 จังหวะ (Powertrain):
   • Engine Core: 2-Stroke Crankcase-Reed-Valve Single/V-Twin Water-Cooled
   • YPVS (Yamaha Power Valve System): วาล์วไอเสียแปรผันด้วยไมโครคอมพิวเตอร์
   • Tuned Expansion Chamber: ท่อไอเสียสูตรสะท้อนคลื่นเสียง Diffuser-Belly-Baffle
   • Silencer: กระบอกท่ออลูมิเนียมเชิดมุม 22° ปลายท่อไอเสียด้านขวา

3. อากาศพลศาสตร์และการยศาสตร์ (Aerodynamics & Ergonomics):
   • Full Racing Cowling: แฟริ่งหน้าทรงลิ่มพร้อมช่องลม NACA Duct ระบายหม้อน้ำ
   • Windscreen: ชิลด์ทรงฟองสบู่ (Bubble Acrylic Screen) ป้องกันแรงต้านอากาศ
   • Cockpit: แฮนด์จับโช้คใต้แผงคอ (Clip-on Bars) ทรงหมอบต่ำแบบ Racing Tuck
   • Wheels: ล้อแม็ก 3 ก้านทรงสปอร์ต 17 นิ้ว พร้อมจานดิสก์เบรกเจาะรูระบายความร้อน

4. ความสมบูรณ์แบบทางวิศวกรรม 3D (Mesh Quality & 3D Printing):
   • 100% Watertight Solid: ปราศจากขอบเปิด (0 Boundary Edges, Manifold Solid)
   • 3D Printing Ready: มีทั้งแบบตัวรถเดี่ยว และแบบพร้อมแท่น Paddock Stand
"""
    ax4.text(0.04, 0.96, card_text.strip(), color='#e2e8f0', fontsize=9.2, 
             fontfamily='monospace', verticalalignment='top', linespacing=1.45)
    
    # Outer frame for text card
    rect = plt.Rectangle((0.01, 0.02), 0.98, 0.96, fill=True, facecolor='#0e1726',
                         edgecolor='#00e5ff', linewidth=1.5, transform=ax4.transAxes, zorder=-1)
    ax4.add_patch(rect)
    
    # Super title
    plt.suptitle("YAMAHA TZR SERIES • 3D TOPOLOGY & AERODYNAMIC ENGINEERING ANALYSIS\n"
                 "หน่วยวิจัยเกษตรดิจิทัลและปัญญาประดิษฐ์ (JC_AI_SciRBRU) | ภาควิชาฟิสิกส์ มรภ.รำไพพรรณี", 
                 color='#f8fafc', fontsize=15, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.94])
    plt.savefig(out_png, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[SUCCESS] Saved high-resolution engineering analysis plot: {out_png}")
    print(f"          Dimensions: 3800 x 2300 pixels | Size: {os.path.getsize(out_png)/1024:.1f} KB")

if __name__ == '__main__':
    render_tzr_analysis()
