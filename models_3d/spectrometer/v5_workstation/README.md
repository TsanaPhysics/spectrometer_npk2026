# SpectorV5-Pro: Integrated Precision Spectrophotometer Workstation
### หน่วยวิจัยฟิสิกส์เกษตรดิจิทัลและปัญญาประดิษฐ์ (JC_AI_SciRBRU)
**สาขาวิชาฟิสิกส์ คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี**

---

## รายการไฟล์ในโฟลเดอร์

| ชื่อไฟล์ | ชนิดข้อมูล | รายละเอียด |
| :--- | :--- | :--- |
| `spector_v5_workstation.scad` | OpenSCAD | สคริปต์ 3D พารามิเตอร์ของสถานีตรวจวัด All-in-One Console |
| `spector_v5_workstation.stl` | Binary STL | โมเดลแท่นสถานีพร้อมพิมพ์ 3D (585,536 Triangles, 27.9 MB, Watertight 100%) |
| `spector_v5_lid.scad` | OpenSCAD | สคริปต์ 3D ฝาปิดเขี้ยวซ้อน 2 ชั้น พร้อมกริปกันลื่นสำหรับ SpectorV5 |
| `spector_v5_lid.stl` | Binary STL | โมเดลฝาปิดเขี้ยวซ้อนพร้อมพิมพ์ 3D (148,484 Triangles, 7.08 MB, Watertight 100%) |
| `spector_v5_analysis.png` | รูปภาพ | แผนผังวิเคราะห์วิศวกรรม 4 มุมมอง (Isometric, Top-Down, Optical Cross-Section, Dimensional Spec) |

## สเปกทางวิศวกรรม
* **ขนาดโครงสร้าง:** $96.0 \times 120.0 \times 78.0\text{ mm}$ (กว้าง x ลึก x สูง)
* **แท่นคอนโซลจอแสดงผล:** เอียง $22^\circ$ ตามหลักการยศาสตร์ (Ergonomics) สำหรับ Wio Terminal
* **เบ้าหลอดคิวเวตต์:** ขนาดมาตรฐาน $10\text{ mm}$ ($12.75 \times 12.75\text{ mm}$, ระยะเผื่อ $+0.25\text{ mm}$)
* **แกนแสง:** สูง $Z = 33.0\text{ mm}$ (สูง $15.0\text{ mm}$ จากฐานคิวเวตต์)
* **ความทึบแสงของผนัง:** ผนังหนา $\ge 3.5\text{ mm}$ พร้อมช่องเดินสายไฟในตัว
