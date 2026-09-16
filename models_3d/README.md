# ศูนย์รวมแบบจำลอง 3 มิติ (3D CAD & Topographic Engineering Repository)
### หน่วยวิจัยฟิสิกส์เกษตรดิจิทัลและปัญญาประดิษฐ์ (JC_AI_SciRBRU)
**สาขาวิชาฟิสิกส์ คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี**

---

## 1. ผังโครงสร้างการจัดเก็บไฟล์ (Directory Architecture)

โฟลเดอร์ `models_3d/` ได้รับการจัดหมวดหมู่อย่างเป็นระบบ แบ่งตามสายงานวิศวกรรมและโครงการวิจัยออกเป็น 2 กลุ่มหลัก เพื่อรองรับการพัฒนาต่อยอดในอนาคต:

```
models_3d/
├── spectrometer/                         # 🔬 โครงการสเปกโทรโฟโตมิเตอร์วัดธาตุอาหาร NPK & pH
│   ├── v4_chamber/                       # โมเดลห้องวัดแสงแยกชิ้น (Modular Optical Chamber) & SpectorV4
│   │   ├── SpectorV4.stl                 # ต้นแบบเชลล์ภายนอกดั้งเดิม (13,120 Triangles)
│   │   ├── cuvette_optical_chamber.scad  # สคริปต์ OpenSCAD ห้องวัดแสงโมดูลาร์
│   │   ├── cuvette_optical_chamber.stl   # ไฟล์ STL ห้องวัดแสงพร้อมพิมพ์ (Watertight 100%)
│   │   ├── light_tight_lid.scad          # สคริปต์ OpenSCAD ฝาครอบกันแสงเขี้ยวซ้อน
│   │   ├── light_tight_lid.stl           # ไฟล์ STL ฝาครอบกันแสงพร้อมพิมพ์ (Watertight 100%)
│   │   ├── spectrometer_assembly.scad    # สคริปต์แบบจำลองประกอบรวมและลำแสงเลเซอร์
│   │   ├── spector_v4_analysis.png       # ภาพวิเคราะห์เรขาคณิตเมช 3D
│   │   ├── spector_v4_slices.png         # ภาพวิเคราะห์เลเยอร์การพิมพ์
│   │   └── README.md                     # เอกสารกำกับโมเดลห้องวัดแสงแยกชิ้น
│   │
│   ├── v5_workstation/                   # โมเดลสถานีตรวจวัด All-in-One เจนเนอเรชันใหม่ (SpectorV5-Pro)
│   │   ├── spector_v5_workstation.scad   # สคริปต์ OpenSCAD แท่นสถานีบูรณาการ Wio Terminal
│   │   ├── spector_v5_workstation.stl    # ไฟล์ STL แท่นสถานีพร้อมพิมพ์ (585,536 Triangles)
│   │   ├── spector_v5_lid.scad           # สคริปต์ OpenSCAD ฝาปิดเขี้ยวซ้อนพร้อมกริปกันลื่น
│   │   ├── spector_v5_lid.stl            # ไฟล์ STL ฝาปิดเขี้ยวซ้อนพร้อมพิมพ์ (148,484 Triangles)
│   │   ├── spector_v5_analysis.png       # ภาพวิเคราะห์มิติวิศวกรรม 4 มุมมอง
│   │   └── README.md                     # เอกสารกำกับโมเดล SpectorV5-Pro
│   │
│   ├── viewer_3d.html                    # เว็บแอป Three.js จำลอง 3D สเปกโทรโฟโตมิเตอร์แบบโต้ตอบ
│   └── README.md                         # คู่มือวิศวกรรมทัศนศาสตร์และสเปกชิ้นส่วนสเปกโตรฯ ทั้งหมด
│
├── thailand_map/                         # 🗺️ โครงการแบบจำลอง 3 มิติแผนที่ภูมิประเทศและลุ่มน้ำไทย
│   ├── thailand_topographic_map_3d.stl   # โมเดลแป้นจารึก 120x200mm สลักร่องแม่น้ำ -0.42mm (Watertight 100%)
│   ├── thailand_country_standalone_3d.stl# โมเดลรูปทรงประเทศไทยลอยตัว 74x135mm (Watertight 100%)
│   ├── thailand_rivers_3d.js             # ชุดข้อมูลพิกัดโครงข่ายลุ่มแม่น้ำ 3 มิติ 46 เส้นทาง
│   ├── thailand_relief.png               # แผนที่ความสูง 16 บิต (16-bit Heightmap) สำหรับ CAD/Blender/CNC
│   ├── thailand_map.scad                 # สคริปต์ OpenSCAD สำหรับปรับสเกลและอัตราส่วนนูนต่ำ
│   ├── thailand_map_analysis.png         # แผนผังวิเคราะห์ทางภูมิศาสตร์และอุทกวิทยา 4 มุมมอง
│   ├── thailand_viewer_3d.html           # เว็บแอป Three.js สกรีนชั้นความสูง 7 ระดับและโครงข่ายลุ่มน้ำ 3D
│   └── README.md                         # คู่มือภูมิสารสนเทศและตารางสลับสีเส้นใย (Slicing Guide)
│
├── yamaha_tzr/                           # 🏍️ โครงการแบบจำลองวิศวกรรมยานยนต์เรซซิ่ง Yamaha TZR (Deltabox & YPVS)
│   ├── yamaha_tzr.scad                   # สคริปต์พารามิเตอร์ OpenSCAD โครงสร้างมอเตอร์ไซค์สมบูรณ์แบบ
│   ├── yamaha_tzr_3d.stl                 # ไฟล์ STL รถสปอร์ตอิสระ 1:10 (Watertight 100% | 656,754 Tris)
│   ├── yamaha_tzr_on_stand_3d.stl        # ไฟล์ STL รถพร้อมสแตนด์เซอร์วิสสนามแข่ง (Watertight 100% | 904,638 Tris)
│   ├── yamaha_tzr_analysis.png           # พิมพ์เขียววิศวกรรม 4 มุมมองความละเอียดสูง 3,800 x 2,300 px
│   ├── tzr_viewer_3d.html                # เว็บแอป Three.js เรนเดอร์ 3D เลือกลายแข่ง/ส่องเฟรม X-Ray/ป้ายชิ้นส่วน
│   └── README.md                         # คู่มือวิศวกรรมยานยนต์ 7 เสาหลักและคู่มือการสไลซ์พิมพ์ 3 มิติ
│
└── README.md                             # (ไฟล์นี้) ดัชนีภาพรวมและแนวทางการจัดระเบียบ 3D
```

---

## 2. รายละเอียดแต่ละกลุ่มงาน (Project Portfolios)

### 2.1 กลุ่มงานเครื่องสเปกโทรโฟโตมิเตอร์ (`spectrometer/`)
* **โฟลเดอร์ [`v4_chamber/`](spectrometer/v4_chamber/):** บรรจุโมเดลห้องวัดแสงแยกชิ้น (Modular Cuvette Chamber) ออกแบบตามกฎ 5 ข้อของทัศนศาสตร์วิศวกรรม แกนแสงตรงกึ่งกลางสูง $15.0\text{ mm}$ จากก้นหลอดคิวเวตต์ พร้อมช่องตัดแสงกระเจิง $\varnothing 3.0\text{ mm}$
* **โฟลเดอร์ [`v5_workstation/`](spectrometer/v5_workstation/):** บรรจุโมเดลสถานีตรวจวัด All-in-One รวมแท่นเสียบ Wio Terminal เอียง $22^\circ$ ตามหลักการยศาสตร์ ห้องวัดแสง ฝาปิดเขี้ยวซ้อน 2 ชั้น และช่องเก็บแบตเตอรี่ในชิ้นเดียว
* **โปรแกรมจำลอง 3 มิติ:** เปิด [`spectrometer/viewer_3d.html`](spectrometer/viewer_3d.html) หรือ [`../web/viewer_3d.html`](../web/viewer_3d.html) เพื่อหมุน ตรวจสอบแกนแสง และตัดผ่าดูโครงสร้างภายใน (Cross-Section)

### 2.2 กลุ่มงานแผนที่ภูมิประเทศและลุ่มน้ำ (`thailand_map/`)
* **แบบจำลองแป้นจารึก:** ขนาด $120 \times 200 \times 12.4\text{ mm}$ สลักร่องลุ่มน้ำลึก $-0.42\text{ mm}$ ขอบเขต 77 จังหวัด และตัวอักษรจารึกภาษาไทย-อังกฤษ
* **แบบจำลองลอยตัว (Standalone):** ขนาด $74 \times 135 \times 12.5\text{ mm}$ ตัดขอบตามรูปทรงขวานทองของประเทศไทย
* **โปรแกรมจำลอง 3 มิติ:** เปิด [`thailand_map/thailand_viewer_3d.html`](thailand_map/thailand_viewer_3d.html) หรือ [`../web/thailand_viewer_3d.html`](../web/thailand_viewer_3d.html) เพื่อใช้งานระบบสกรีนชั้นความสูง 7 ระดับสีวิทยาศาสตร์ และกรองโครงข่ายลุ่มน้ำ 3D

### 2.3 กลุ่มงานยานยนต์และเรซซิ่งโมเดลลิ่ง (`yamaha_tzr/`)
* **โครงสร้างโมเดล:** ถอดรหัสสถาปัตยกรรม 7 เสาหลักของ Yamaha TZR 150/250 (เฟรม Deltabox อะลูมิเนียม, เครื่องยนต์ 2 จังหวะ YPVS, ท่อรีดไอเสีย Hydroformed Expansion Chamber, สวิงอาร์ม Monocross, โช้คหน้า 38mm พร้อมแฮนด์จับโช้ค, ล้อแม็ก 3 ก้าน 17 นิ้ว และแฟริ่งแอโรไดนามิกส์ 90s GP)
* **โมเดล 3 มิติ:** ไฟล์ STL ทั้งสองเวอร์ชันมีความสมบูรณ์แบบระดับ Manifold 100% (Watertight, Boundary Edges = 0) พร้อมพิมพ์ 3D ทุกระบบ
* **โปรแกรมจำลอง 3 มิติ:** เปิด [`yamaha_tzr/tzr_viewer_3d.html`](yamaha_tzr/tzr_viewer_3d.html) หรือ [`../web/tzr_viewer_3d.html`](../web/tzr_viewer_3d.html) เพื่อเลือกลายแข่ง (Speedblock, Tech Blue, Stealth, Deltabox Silver, 60th GP Yellow), โหมดส่องโครงสร้างโปร่งใส X-Ray Naked Frame, และป้ายชี้ตำแหน่งชิ้นส่วนวิศวกรรม 8 จุด

---

## 3. แนวทางปฏิบัติสำหรับการพัฒนาโมเดล 3 มิติในอนาคต (Future Development Guidelines)

เมื่อมีการออกแบบชิ้นส่วนหรือแบบจำลอง 3 มิติเพิ่มเติม ให้ปฏิบัติตามมาตรฐานดังต่อไปนี้:
1. **การจัดวางโฟลเดอร์:**
   - ชิ้นส่วนอุปกรณ์วัด ให้สร้างโฟลเดอร์ย่อยใน `spectrometer/` เช่น `v6_field_portable/`, `accessories/`, `mounts/`
   - แผนที่หรือโมเดลภูมิศาสตร์ ให้จัดไว้ใน `thailand_map/` หรือสร้างกลุ่มใหม่ในระดับเดียวกัน เช่น `provinces_3d/`
2. **การรักษาคุณภาพเมช (Watertight Mesh Guarantee):**
   - ทุกไฟล์ `.stl` ที่สร้างขึ้นใหม่ต้องผ่านการตรวจสอบว่าเป็น Solid ปิดสนิท ไร้ขอบเปิด (0 Boundary Edges) และไม่มี Non-manifold geometry
3. **การจัดเตรียมไฟล์ต้นทาง (Parametric CAD):**
   - แนบไฟล์ `.scad` หรือ Python generator script ควบคู่กับไฟล์ `.stl` เสมอ เพื่อให้สามารถปรับแก้มิติและระยะเผื่อพิมพ์ (Tolerance) ได้ง่าย
4. **การอัปเดต Viewer และเอกสาร:**
   - เพิ่มรายการใน `README.md` ประจำโฟลเดอร์ย่อย และอัปเดตโมเดลเข้าสู่ Web Viewer เพื่อให้สามารถตรวจสอบผ่านเบราว์เซอร์ได้ทันที
