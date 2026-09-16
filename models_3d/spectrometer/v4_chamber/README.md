# SpectorV4 & Modular Optical Chamber (ชุดโมเดลห้องวัดแสงแยกชิ้น)
### หน่วยวิจัยฟิสิกส์เกษตรดิจิทัลและปัญญาประดิษฐ์ (JC_AI_SciRBRU)
**สาขาวิชาฟิสิกส์ คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี**

---

## รายการไฟล์ในโฟลเดอร์

| ชื่อไฟล์ | ชนิดข้อมูล | รายละเอียด |
| :--- | :--- | :--- |
| `SpectorV4.stl` | Binary STL | โมเดลมาสเตอร์คลาสสิก SpectorV4 โครงสร้างภายนอกดั้งเดิม (13,120 Triangles) |
| `cuvette_optical_chamber.scad` | OpenSCAD | สคริปต์ 3D พารามิเตอร์ของห้องวัดแสงแยกชิ้น (Modular Chamber) |
| `cuvette_optical_chamber.stl` | Binary STL | โมเดลห้องวัดแสงแยกชิ้นพร้อมพิมพ์ (286,800 Triangles, Watertight 100%) |
| `light_tight_lid.scad` | OpenSCAD | สคริปต์ 3D ฝาปิดกันแสงเขี้ยวซ้อน (Labyrinth Lid) สำหรับห้องวัดแยกชิ้น |
| `light_tight_lid.stl` | Binary STL | โมเดลฝาปิดกันแสงพร้อมพิมพ์ (209,088 Triangles, Watertight 100%) |
| `spectrometer_assembly.scad` | OpenSCAD | โมเดลประกอบรวมจำลองลำแสงเลเซอร์ (Exploded / Collinear Beam View) |
| `spector_v4_analysis.png` | รูปภาพ | ผลการวิเคราะห์โครงสร้างตาข่ายสามเหลี่ยมและมิติทางวิศวกรรม |
| `spector_v4_slices.png` | รูปภาพ | ภาคตัดขวางเลเยอร์การพิมพ์ 3D ของโมเดล SpectorV4 |

## กฎทางวิศวกรรมทัศนศาสตร์
1. **Coaxial Collinear Centerline:** แกนลำแสงตรงกึ่งกลางสูง $Z = 15.0\text{ mm}$ จากก้นหลอด
2. **Dual $\varnothing 3.0\text{ mm}$ Collimating Apertures:** ตัดแสงกระเจิงและควบคุมลำแสงขนาน
3. **Double-Stepped Labyrinth Seal:** ฝาครอบกันแสงรั่วเขี้ยวซ้อน ป้องกันแสงสะท้อนจากภายนอก
