# ชุดโมเดล 3 มิติสำหรับเครื่องสเปกโทรโฟโตมิเตอร์ (NPK Spectrometer 2026 - 3D Mechanical & Optical Models)

**หน่วยวิจัยเกษตรดิจิทัล JC_AI_SciRBRU (Digital Agriphysics & AI Research Unit)**  
**สาขาวิชาฟิสิกส์ คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี**

---

## 1. ภาพรวมสถาปัตยกรรมทางวิศวกรรมทัศนศาสตร์ (Optical Engineering Overview)

ชุดโมเดล 3 มิตินี้ได้รับการออกแบบขึ้นโดยคำนึงถึง **ทัศนศาสตร์ฟิสิกส์ (Optical Physics)** และ **กฎของเบียร์และแลมเบิร์ต (Beer-Lambert Law)** เพื่อให้การตรวจวัดธาตุอาหารในดิน (N, P, K, pH) และการวิเคราะห์สมบัติของเหลวมีเสถียรภาพและความแม่นยำสูงสุดในระดับห้องปฏิบัติการวิจัย

```
                    ┌────────────────────────────────┐
                    │     Light-Tight Baffle Lid     │ (ฝาครอบกันแสงรั่วเขี้ยวซ้อน 2 ชั้น)
                    └───────────────┬────────────────┘
                                    │
               ┌────────────────────▼───────────────────┐
               │                                        │
[Grove WS2812B]─►│  Ø3mm Aperture ──► [Cuvette 10mm] ──► Ø3mm Aperture  │──► [Adafruit TCS34725]
 (Grove Port D0)│       (แนวแกนแสงตรง Coaxial Centerline สูง 15.0 mm)     │    (Grove Port I2C)
               └────────────────────────────────────────┘
                   Cuvette Optical Measurement Chamber
```

### คุณลักษณะเด่นทางวิศวกรรม (Key Features):
1. **แนวแกนแสงโคแอกเชียลตรง 100% (Coaxial Collinear Optical Axis):**
   - ความสูงกึ่งกลางลำแสง ($Z_{\text{opt}}$) อยู่ที่ **$15.0\text{ mm}$** จากก้นหลอดคิวเวตต์ (ระดับความสูงกึ่งกลางของปริมาตรของเหลวตัวอย่าง $2.0 - 3.5\text{ mL}$)
   - แหล่งกำเนิดแสง WS2812B, ช่องจำกัดลำแสงเข้า, หลอดคิวเวตต์, ช่องจำกัดลำแสงออก, และโฟโตไดโอดเซนเซอร์ TCS34725 วางตัวตรงกันสมบูรณ์แบบ
2. **ช่องจำกัดลำแสงคู่ (Dual Collimating Apertures - $\varnothing 3.0\text{ mm}$):**
   - **ฝั่งหลอดไฟ (Input Aperture):** ปรับลำแสงที่กระจายตัวจาก LED ให้เป็นลำแสงขนาน (Collimated Parallel Beam) ส่องกระทบตั้งฉากกับผนังคิวเวตต์
   - **ฝั่งเซนเซอร์ (Output Aperture):** ตัดแสงกระเจิง (Stray Light / Scattering Cut-off) จากอนุภาคดินแขวนลอย เพื่อให้เฉพาะแสงที่ทะลุผ่านตรงเข้าสู่ตัวตรวจจับ
3. **ฝาครอบประกบกันแสงรั่วเขี้ยวซ้อน 2 ชั้น (Double-Stepped Labyrinth Seal Lid):**
   - แสงภายนอกไม่สามารถวิ่งเป็นเส้นตรงเข้าสู่ห้องวัดได้ ต้องสะท้อนหักมุม 90 องศาถึง 2 ครั้ง ทำให้ค่ากระแสมืด (Dark Current: $I_{\text{dark}}$) เสถียรแม้ใช้งานกลางแดดจัดในแปลงเกษตร
4. **เบ้าล็อกเซนเซอร์และช่องร้อยสาย (Sensor Pockets & Cable Relief):**
   - ออกแบบเบ้าขนาดพอดีสำหรับบอร์ด Adafruit TCS34725 และ Grove RGB LED พร้อมรูนำร่องสกรูยึด M2.5 และช่องร้อยสาย Grove 4-Pin ปลอดภัยไม่หักงอ

---

## 2. รายการไฟล์ในโฟลเดอร์ `models_3d/`

| ชื่อไฟล์ | ชนิดข้อมูล | บทบาทหน้าที่ |
| :--- | :--- | :--- |
| `cuvette_optical_chamber.scad` | OpenSCAD Script | โค้ด 3D แบบพารามิเตอร์ของห้องวัดแสง ปรับแก้ขนาดความหนาและระยะเผื่อได้อิสระ |
| `light_tight_lid.scad` | OpenSCAD Script | โค้ด 3D แบบพารามิเตอร์ของฝาปิดกันแสงและกริปจับ |
| `spectrometer_assembly.scad` | OpenSCAD Script | โมเดลรวมแบบ Exploded View พร้อมจำลองลำแสงเลเซอร์และหลอดคิวเวตต์ |
| `cuvette_optical_chamber.stl` | Binary STL Mesh | **ไฟล์พร้อมพิมพ์ 3D ทันที** สำหรับห้องวัดแสง (286,800 Triangles) |
| `light_tight_lid.stl` | Binary STL Mesh | **ไฟล์พร้อมพิมพ์ 3D ทันที** สำหรับฝาปิดกันแสง (209,088 Triangles) |
| `viewer_3d.html` | Three.js Web Viewer | หน้าเว็บจำลอง 3 มิติแบบโต้ตอบ หมุน ซูม ปรับระยะยกฝา และสลับสีลำแสงได้สดๆ |
| `../scripts/generate_3d_models.py` | Python Generator | สคริปต์คำนวณ Signed Distance Fields & Marching Cubes สำหรับสร้างไฟล์ `.stl` |

---

## 3. คำแนะนำการพิมพ์ 3 มิติ (3D Printing & Slicer Settings)

เพื่อให้ห้องวัดแสงมีประสิทธิภาพการกันแสงและลดการสะท้อนระดับงานวิจัย (Research Grade) กรุณาตั้งค่าโปรแกรม Slicer (Bambu Studio / PrusaSlicer / OrcaSlicer / Cura) ดังนี้:

* **ชนิดของเส้นใย (Filament):**
  * แนะนำ **PLA+ สีดำด้าน (Matte Black)** หรือ **PETG สีดำด้าน** *(ข้อห้ามเด็ดขาด: ห้ามใช้เส้นใยสีขาว สีใส หรือสีสะท้อนแสง เพราะจะทำให้เกิด Internal Reflection ทำให้ค่าการดูดกลืนแสงเพี้ยน)*
* **ความหนาแน่นเนื้อใน (Infill Density):**
  * **100% Solid Infill** (สำคัญมาก: เพื่อป้องกันไม่ให้แสงไฟภายนอกทะลุผ่านช่องว่างภายในเนื้อพลาสติกเข้าสู่เซนเซอร์)
* **ความหนาผนัง (Wall Loops / Perimeters):**
  * กำหนดอย่างน้อย **4 ถึง 5 Loops** (ความหนาผนัง $\ge 2.0\text{ mm}$)
* **ความละเอียดชั้นพิมพ์ (Layer Height):**
  * แนะนำ **$0.16\text{ mm}$** ถึง **$0.20\text{ mm}$**
* **โครงสร้างค้ำยัน (Supports):**
  * **ไม่ต้องเปิด Support (No Supports Needed)** ชิ้นงานได้รับการออกแบบมุมลาดเอียง (45° Self-supporting Chamfer) สำหรับรูทางเดินแสงและช่องใส่คิวเวตต์ ทำให้พิมพ์ได้เรียบเนียนโดยไม่ต้องใช้ตัวค้ำยัน
* **การวางตำแหน่งบนฐานพิมพ์ (Build Plate Orientation):**
  * `cuvette_optical_chamber.stl`: วางหน้าแปลนฐานราก (Flange) แนบติดกับ Heatbed
  * `light_tight_lid.stl`: วางหน้าเรียบด้านล่าง หรือวางกลับหัวโดยให้ที่จับอยู่ด้านบนตามการออกแบบ

---

## 4. รายการฮาร์ดแวร์ประกอบ (Bill of Materials - BOM)

1. **ชิ้นงานพิมพ์ 3D:**
   - 1x Optical Measurement Chamber (`cuvette_optical_chamber.stl`)
   - 1x Light-Tight Baffle Lid (`light_tight_lid.stl`)
2. **อุปกรณ์อิเล็กทรอนิกส์เชิงแสง:**
   - 1x Seeed Studio Wio Terminal
   - 1x โมดูล Adafruit TCS34725 I2C Color Sensor
   - 1x โมดูล Grove RGB LED (WS2812B NeoPixel)
   - 2x สายเชื่อมต่อ Grove 4-Pin Cable (ความยาว $20\text{ cm}$)
3. **อุปกรณ์ประกอบเชิงกล (Fasteners):**
   - 4x สกรูเกลียวปล่อย M2.5 $\times 6\text{ mm}$ (สำหรับยึดแผ่นวงจรเซนเซอร์และหลอด LED)
   - 4x น็อตและสกรู M3 $\times 10\text{ mm}$ (สำหรับยึดฐานแปลนเข้ากับแท่นทดลอง หรือกล่องรวมบอร์ด)
4. **อุปกรณ์ทัศนศาสตร์:**
   - หลอดคิวเวตต์มาตรฐานทางเดินแสง $10\text{ mm}$ (Standard $12.5 \times 12.5 \times 45\text{ mm}$ Optical Glass / Quartz / Disposable Polystyrene Cuvette)

---

## 5. วิธีเปิดดูโมเดล 3 มิติบนเว็บเบราว์เซอร์ (Interactive 3D Web Viewer)

คุณสามารถเปิดไฟล์ `models_3d/viewer_3d.html` ด้วยเว็บเบราว์เซอร์ (Google Chrome, Safari, Microsoft Edge, Firefox) เพื่อ:
- คลิกเมาส์ซ้ายลากเพื่อหมุนมุมมอง 360 องศา
- เลื่อนลูกกลิ้งเมาส์เพื่อซูมเข้า-ออก
- เลื่อนแถบเลื่อน **"ระยะยกฝาครอบ (Exploded View)"** เพื่อดูชิ้นส่วนภายใน
- กดปุ่ม **"ความยาวคลื่นลำแสง"** เพื่อดูแนวลำแสง $465\text{ nm}$ (สีน้ำเงิน N), $525\text{ nm}$ (สีเขียว P), $625\text{ nm}$ (สีแดง K), หรือ White LED
- กดปุ่ม **"ผ่าครึ่ง (Cutaway)"** เพื่อตรวจเช็คความสมบูรณ์ของแนวทางเดินแสงภายในห้องวัด
- ลากไฟล์ `.stl` จากเครื่องมาวางในหน้าจอเพื่อเรนเดอร์ทดสอบได้ทันที
