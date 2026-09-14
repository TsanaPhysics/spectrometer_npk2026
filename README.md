# spectrometer_npk2026
**เครื่องสเปกโทรโฟโตมิเตอร์ตรวจวัดธาตุอาหารหลักในดิน (NPK Level Meter 1.02) พร้อมระบบประมวลผล TinyML / Edge AI, สแกนความยาวคลื่นอัตโนมัติ และระบบเทียบมาตรฐานเชิงวิเคราะห์ (In-Situ Standard Curve Wizard: R², LOD, LOQ)**

โครงการพัฒนาระบบตรวจวัดธาตุอาหารหลักในดิน (Nitrogen - N, Phosphorus - P, Potassium - K) ระดับห้องปฏิบัติการภาคสนามโดยอาศัยหลักการสเปกโทรโฟโตเมตรี (Spectrophotometry) ประมวลผลบนไมโครคอนโทรลเลอร์ Seeed Studio Wio Terminal พร้อมระบบเมนูหลายหน้าจอ (Multi-Screen Carousel UI), ระบบสแกนกวาดแสงอัตโนมัติ (Automated Wavelength Sweep), ระบบคาลิเบรตมาตรฐานหลายจุดคำนวณสถิติมาตรวิทยาเคมีวิเคราะห์ ($R^2$, LOD, LOQ) บนชิปโดยตรง และโมเดลการเรียนรู้เชิงลึกแบบ TinyML Edge AI

---

## จุดเด่นของระบบ (Key Features)
1. **ระบบควบคุม 4 หน้าจอ (4-Screen Carousel UI):**
   - **Page 1: System Dashboard:** ตรวจสอบความพร้อมของระบบ สเปกชิป ATSAMD51 120 MHz, FPU, แฟลช, แรม, เซนเซอร์ TCS34725 และสถานะ microSD Card
   - **Page 2: NPK Level Meter 1.02:** หน้าจอหลักแสดงความเข้มข้น N, P, K แบบเรียลไทม์ พร้อมป้ายสถานะโหมด `[AI]`, `[PL]`, หรือ `[SC]`
   - **Page 3: Absorbance Spectrum Plot:** กราฟิก 2D แสดงเส้นโค้งการดูดกลืนแสง $A(\lambda)$ ช่วง 400 - 700 nm พร้อมตรวจจับพีคการดูดกลืนแสง ($\lambda_{\max}, A_{\max}$) และระบบเตือนความเข้มข้นสูงเกินย่านเชิงเส้น ($A > 1.50$)
   - **Page 4: Calibration & Standard Curve Wizard:** ระบบเทียบมาตรฐานสารละลายมาตรฐาน 5 จุด ($0, 20, 40, 80, 160\text{ mg/kg}$) พร้อมพล็อตกราฟเส้นตรงการถดถอยและคำนวณค่า $R^2$, Slope $m$, Intercept $c$, LOD, LOQ บนหน้าจอ LCD
2. **ระบบการคำนวณ 3 โหมด (Triple Analytical Engine):**
   - **`[AI]` (ป้ายเขียว):** พยากรณ์ด้วยโครงข่ายประสาทเทียม TinyML Deep Learning ($6 \to 12 \to 8 \to 3$) พร้อมระบบชดเชยความขุ่น
   - **`[PL]` (ป้ายเหลือง):** คำนวณด้วยสมการพหุนามสากล (Classical Polynomial)
   - **`[SC]` (ป้ายฟ้า):** คำนวณด้วยสมการเส้นตรงมาตรฐานที่ผู้ใช้วัดเทียบสดจากห้องปฏิบัติการ (In-Situ Standard Curve: $C = \frac{A - c}{m}$)
3. **ระบบสแกนความยาวคลื่นอัตโนมัติและการหักลบกระแสมืด:** ดับไฟ 50 ms วัด Dark Current ($I_{\text{dark}}$) แล้วกวาดแสง 5 ช่วงคลื่น (465, 500, 525, 590, 625 nm)
4. **Triple Data Logging on microSD:**
   - `NPK.csv`: บันทึกค่าความเข้มข้นธาตุอาหาร NPK ต่อเนื่อง
   - `SPECTRUM.csv`: บันทึกค่า Absorbance ของสเปกตรัมทุกช่วงความยาวคลื่นเมื่อกด Auto-Scan
   - `CALIB_LOG.csv`: บันทึกประวัติสมการคาลิเบรต $R^2$, LOD, LOQ และพารามิเตอร์การวัด

---

## การควบคุมและสลับหน้าจอ (User Controls & Navigation)

| ปุ่มกด / จอยสติ๊ก | ตำแหน่ง | หน้าที่การทำงาน |
| :--- | :--- | :--- |
| **จอยสติ๊กโยกซ้าย (`WIO_5S_LEFT`)** | ด้านหน้า | สลับไปยัง **หน้าจอก่อนหน้า** (วนลูป 4 หน้าจอ) |
| **จอยสติ๊กโยกขวา (`WIO_5S_RIGHT`)** | ด้านหน้า | สลับไปยัง **หน้าจอถัดไป** (Dashboard -> NPK -> Spectrum -> Calib) |
| **จอยสติ๊กโยกลง (`WIO_5S_DOWN`)** | ด้านหน้า | ในหน้า Spectrum: สั่ง **Auto-Scan**<br>ในหน้า Calibrate: สั่ง **บันทึกจุดสารมาตรฐาน (Step Calib)** |
| **จอยสติ๊กโยกขึ้น (`WIO_5S_UP`)** | ด้านหน้า | ในหน้า NPK: สลับโหมดคำนวณ **`[AI]` $\to$ `[PL]` $\to$ `[SC]`** |
| **จอยสติ๊กกดตรงกลาง (`WIO_5S_PRESS`)** | ด้านหน้า | ในหน้า Calibrate: สั่ง **Zero Blank ($I_0$)** บนทุกช่องสัญญาณ<br>ในหน้าอื่น: เปิด/ปิด **ไฟสีขาว (White LED)** |
| **ปุ่ม C (ซ้ายสุดด้านบน)** | ด้านบน | ในหน้า Calibrate: เลือกคาลิเบรต **ไนโตรเจน (N - 465 nm)**<br>ในหน้า NPK: เปิด/ปิด **ไฟสีน้ำเงิน (Blue LED)** |
| **ปุ่ม B (กลางด้านบน)** | ด้านบน | ในหน้า Calibrate: เลือกคาลิเบรต **ฟอสฟอรัส (P - 525 nm)**<br>ในหน้า NPK: เปิด/ปิด **ไฟสีเขียว (Green LED)** |
| **ปุ่ม A (ขวาสุดด้านบน)** | ด้านบน | ในหน้า Calibrate: เลือกคาลิเบรต **โพแทสเซียม (K - 625 nm)**<br>ในหน้า NPK: เปิด/ปิด **ไฟสีแดง (Red LED)** |

---

## ทฤษฎีมาตรวิทยาเคมีวิเคราะห์ (Analytical Metrology & Calibration)

### 1. การถดถอยเชิงเส้นตรง (OLS Linear Regression):
$$A = m \cdot C + c \implies C = \frac{A - c}{m}$$

### 2. สัมประสิทธิ์การตัดสินใจ (Coefficient of Determination $R^2$):
$$R^2 = \frac{\left[\sum (C_i - \bar{C})(A_i - \bar{A})\right]^2}{\sum (C_i - \bar{C})^2 \sum (A_i - \bar{A})^2}$$

### 3. ขีดจำกัดการตรวจวัดและการหาปริมาณ (LOD / LOQ ตามเกณฑ์ IUPAC):
$$\text{LOD} = \frac{3.3 \cdot s_{y/x}}{m}, \quad \text{LOQ} = \frac{10 \cdot s_{y/x}}{m}$$

---

## โครงสร้างโปรเจกต์ (Repository Structure)
```
spectrometer_npk2026/
├── README.md                           # คู่มือฉบับสมบูรณ์
├── firmware/
│   ├── spectrometer_npk2026/
│   │   ├── spectrometer_npk2026.ino    # สเก็ตช์หลักระบบ Triple-Engine & 4-Screen UI
│   │   ├── Calibration_Engine.h        # เอนจิน Standard Curve Regression (R2, LOD, LOQ) & Chart
│   │   ├── Spectrum_Engine.h           # เอนจิน Auto-Scan Wavelength Sweep & Absorbance Chart
│   │   └── TinyML_Model.h              # โมเดล TinyML C++ Zero-Allocation
│   └── train_tinyml_model.py           # สคริปต์ฝึกสอนและส่งออกโมเดล AI
├── docs/
│   ├── NPK_Spectrometer_Manual.pdf     # เอกสารคู่มือวิชาการฉบับสมบูรณ์ (มาตรฐาน มรภ.รำไพพรรณี)
│   ├── manual_assembly_operation.md    # คู่มือปฏิบัติการแบบ Markdown
│   └── latex/                          # ซอร์สโค้ด XeLaTeX
└── data/
    ├── NPK.csv                         # ตัวอย่างไฟล์บันทึกค่าความเข้มข้น NPK
    ├── SPECTRUM.csv                    # ตัวอย่างไฟล์บันทึกสเปกตรัมการดูดกลืนแสง
    └── CALIB_LOG.csv                   # ประวัติสมการคาลิเบรต R2, LOD, LOQ
```

---

## ใบอนุญาตและการอ้างอิง (License and Citation)
ผลงานนี้เผยแพร่ภายใต้สัญญาอนุญาต **MIT License**  
หากนำผลงานหรือแบบจำลองไปใช้ในงานวิจัยทางวิชาการ กรุณาอ้างอิง:
> ชีวะ ทัศนา และคณะ. (2569). *คู่มือการประกอบ ติดตั้ง และใช้งานเครื่องสเปกโทรโฟโตมิเตอร์ตรวจวัดธาตุอาหารหลักในดิน (NPK Level Meter 1.02)*. หน่วยวิจัยฟิสิกส์เพื่อการเกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics) สาขาวิชาฟิสิกส์ คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี.
