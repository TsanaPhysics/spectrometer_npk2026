# spectrometer_npk2026
**เครื่องสเปกโทรโฟโตมิเตอร์ตรวจวัดธาตุอาหารหลักในดิน (NPK Level Meter 1.02) พร้อมระบบประมวลผล TinyML / Edge AI, ระบบสแกนความยาวคลื่นอัตโนมัติ และการพล็อตกราฟสเปกตรัมการดูดกลืนแสงบนจอ LCD**

โครงการพัฒนาระบบตรวจวัดธาตุอาหารหลักในดิน (Nitrogen - N, Phosphorus - P, Potassium - K) ระดับห้องปฏิบัติการภาคสนามโดยอาศัยหลักการสเปกโทรโฟโตเมตรี (Spectrophotometry) ร่วมกับเซนเซอร์วัดค่าสีแบบดิจิทัลความละเอียดสูง TCS34725 และโมดูลกำเนิดแสงหลายความยาวคลื่น ประมวลผลบนไมโครคอนโทรลเลอร์ Seeed Studio Wio Terminal ขับเคลื่อนด้วยโครงสร้างหลายหน้าจอ (Multi-Screen Carousel UI), ระบบสแกนความยาวคลื่นอัตโนมัติ (Automated Wavelength Sweep), การหักลบกระแสมืด (Dark Current Compensation) และโครงข่ายประสาทเทียม TinyML Edge AI

---

## จุดเด่นของระบบ (Key Features)
1. **ระบบควบคุม 4 หน้าจอ (4-Screen Carousel State Machine):**
   - **Page 0: System Dashboard:** ตรวจสอบความสมบูรณ์ของระบบ ชิป ATSAMD51 120 MHz, หน่วยความจำ Flash/RAM, การเชื่อมต่อเซนเซอร์แสง และ microSD Card
   - **Page 1: NPK Level Meter 1.02:** หน้าจอหลักแสดงความเข้มข้น N, P, K แบบเรียลไทม์ พร้อมป้ายสถานะโหมด `[AI]` หรือ `[PL]`
   - **Page 2: Absorption Spectrum Plot:** กราฟิก 2D แสดงเส้นโค้งการดูดกลืนแสง $A(\lambda)$ ช่วง 400 - 700 nm แบบเรียลไทม์ พร้อมตรวจจับจุดยอดการดูดกลืนแสง ($\lambda_{\max}, A_{\max}$) และระบบเตือนความเข้มข้นสูงเกินย่านเชิงเส้น ($A > 1.5$)
   - **Page 3: Calibration & Blank Wizard:** ระบบเทียบมาตรฐานสารละลายอ้างอิง ($I_0$) และตรวจวัดกระแสมืด ($I_{\text{dark}}$) บันทึกลงหน่วยความจำและ microSD Card
2. **ระบบสแกนความยาวคลื่นอัตโนมัติ (Automated Wavelength Sweep):**
   - ดับไฟ 50 ms เพื่อเก็บค่ากระแสมืดและแสงรบกวนแวดล้อม ($I_{\text{dark}}$)
   - กวาดแสงกระตุ้น 5 ช่วงคลื่น: Blue (465 nm), Cyan (500 nm), Green (525 nm), Yellow (590 nm), Red (625 nm)
   - คำนวณค่า Transmittance และ Absorbance ตามกฎของเบียร์-แลมเบิร์ต (Beer-Lambert Law)
3. **TinyML / Edge AI Deep Neural Network:** โครงข่ายประสาทเทียม Multi-Layer Perceptron ($6 \to 12 \to 8 \to 3$) ประมวลผลบนฮาร์ดแวร์ FPU ความเร็ว $12.4\ \mu\text{s}$ ต่อตัวอย่าง
4. **Dual Data Logging on microSD:**
   - `NPK.csv`: บันทึกค่าความเข้มข้นธาตุอาหาร NPK ต่อเนื่อง
   - `SPECTRUM.csv`: บันทึกค่า Absorbance ของสเปกตรัมทุกช่วงความยาวคลื่นสำหรับการวิเคราะห์เชิงลึก

---

## การควบคุมและสลับหน้าจอ (User Controls & Navigation)

| ปุ่มกด / จอยสติ๊ก | ตำแหน่ง | หน้าที่การทำงาน |
| :--- | :--- | :--- |
| **จอยสติ๊กโยกซ้าย (`WIO_5S_LEFT`)** | ด้านหน้า | สลับไปยัง **หน้าจอก่อนหน้า** (วนลูป 4 หน้าจอ) |
| **จอยสติ๊กโยกขวา (`WIO_5S_RIGHT`)** | ด้านหน้า | สลับไปยัง **หน้าจอถัดไป** (Dashboard -> NPK -> Spectrum -> Calib) |
| **จอยสติ๊กโยกลง (`WIO_5S_DOWN`)** | ด้านหน้า | สั่ง **Auto-Scan** กวาดแสงในหน้า Spectrum หรือสั่ง **Zero Blank** ในหน้า Calibrate |
| **จอยสติ๊กโยกขึ้น (`WIO_5S_UP`)** | ด้านหน้า | สลับโหมดวิเคราะห์ **`[AI]` TinyML $\leftrightarrow$ `[PL]` Polynomial** (ในหน้า NPK) |
| **จอยสติ๊กกดตรงกลาง (`WIO_5S_PRESS`)** | ด้านหน้า | เปิด/ปิด **ไฟสีขาว (White LED)** สำหรับการเทียบศูนย์ |
| **ปุ่ม A (ขวาสุดด้านบน)** | ด้านบน | เปิด/ปิด **ไฟสีแดง (Red LED)** |
| **ปุ่ม B (กลางด้านบน)** | ด้านบน | เปิด/ปิด **ไฟสีเขียว (Green LED)** |
| **ปุ่ม C (ซ้ายสุดด้านบน)** | ด้านบน | เปิด/ปิด **ไฟสีน้ำเงิน (Blue LED)** |

---

## การคำนวณทางฟิสิกส์สเปกโทรสโกปี (Spectroscopic Equations)

1. **การหักลบกระแสมืด (Dark Current Correction):**
   $$I_{\text{sample, corr}}(\lambda) = \max(1.0, \, I_{\text{sample}}(\lambda) - I_{\text{dark}}(\lambda))$$
   $$I_{\text{blank, corr}}(\lambda) = \max(1.0, \, I_{\text{blank}}(\lambda) - I_{\text{dark}}(\lambda))$$

2. **การดูดกลืนแสงตามกฎของเบียร์-แลมเบิร์ต (Beer-Lambert Law):**
   $$T(\lambda) = \frac{I_{\text{sample, corr}}(\lambda)}{I_{\text{blank, corr}}(\lambda)}$$
   $$A(\lambda) = -\log_{10}(T(\lambda))$$

3. **ขีดจำกัดย่านความเป็นเส้นตรง (Linear Dynamic Range Alert):**
   หากค่า $A_{\max} > 1.50$ หน้าจอจะแสดงป้ายเตือน:
   `! WARN: HIGH ABS - DILUTE 1:5 !` เพื่อแนะนำให้ทำการเจือจางสารละลายตัวอย่างก่อนวัดซ้ำ

---

## โครงสร้างโปรเจกต์ (Repository Structure)
```
spectrometer_npk2026/
├── README.md                           # คู่มือฉบับสมบูรณ์
├── firmware/
│   ├── spectrometer_npk2026/
│   │   ├── spectrometer_npk2026.ino    # สเก็ตช์หลักระบบ Multi-Screen & State Machine
│   │   ├── Spectrum_Engine.h           # เอนจิน Auto-Scan & วาดกราฟสเปกตรัม A(lambda)
│   │   ├── Calibration_Engine.h        # ระบบเทียบมาตรฐาน Blank Reference & Dark Current
│   │   └── TinyML_Model.h              # โมเดล TinyML C++ Zero-Allocation
│   └── train_tinyml_model.py           # สคริปต์ฝึกสอนและส่งออกโมเดล AI
├── docs/
│   ├── NPK_Spectrometer_Manual.pdf     # เอกสารคู่มือวิชาการฉบับสมบูรณ์ (มาตรฐาน มรภ.รำไพพรรณี)
│   ├── manual_assembly_operation.md    # คู่มือปฏิบัติการแบบ Markdown
│   └── latex/                          # ซอร์สโค้ด XeLaTeX
└── data/
    ├── NPK.csv                         # ตัวอย่างไฟล์บันทึกค่าความเข้มข้น NPK
    └── SPECTRUM.csv                    # ตัวอย่างไฟล์บันทึกสเปกตรัมการดูดกลืนแสง
```

---

## ใบอนุญาตและการอ้างอิง (License and Citation)
ผลงานนี้เผยแพร่ภายใต้สัญญาอนุญาต **MIT License**  
หากนำผลงานหรือแบบจำลองไปใช้ในงานวิจัยทางวิชาการ กรุณาอ้างอิง:
> ชีวะ ทัศนา และคณะ. (2569). *คู่มือการประกอบ ติดตั้ง และใช้งานเครื่องสเปกโทรโฟโตมิเตอร์ตรวจวัดธาตุอาหารหลักในดิน (NPK Level Meter 1.02)*. หน่วยวิจัยฟิสิกส์เพื่อการเกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics) สาขาวิชาฟิสิกส์ คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี.
