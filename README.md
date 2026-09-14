# spectrometer_npk2026

<p align="center">
  <img src="docs/images/npk_spec_logo.jpg" alt="NPK Spectrometer Logo" width="280" />
</p>

<h2 align="center"><b>เครื่องสเปกโทรโฟโตมิเตอร์ตรวจวัดธาตุอาหารหลักในดินและสมบัติเชิงแสงของของเหลว</b></h2>
<h3 align="center"><b>(NPK Level Meter 1.02 & Liquid Optics Metrology Analyzer)</b></h3>

<p align="center">
  <a href="https://github.com/TsanaPhysics/spectrometer_npk2026"><img src="https://img.shields.io/badge/Platform-Seeed_Wio_Terminal-00979D.svg?style=for-the-badge&logo=arduino" alt="Platform"></a>
  <a href="https://github.com/TsanaPhysics/spectrometer_npk2026"><img src="https://img.shields.io/badge/MCU-ATSAMD51_120MHz_FPU-FF6F00.svg?style=for-the-badge&logo=microchip" alt="MCU"></a>
  <a href="https://github.com/TsanaPhysics/spectrometer_npk2026"><img src="https://img.shields.io/badge/TinyML-Deep_Neural_Net-00E676.svg?style=for-the-badge&logo=tensorflow" alt="TinyML"></a>
  <a href="https://github.com/TsanaPhysics/spectrometer_npk2026"><img src="https://img.shields.io/badge/Metrology-OLS_R²_LOD_LOQ-2979FF.svg?style=for-the-badge" alt="Metrology"></a>
  <a href="https://github.com/TsanaPhysics/spectrometer_npk2026"><img src="https://img.shields.io/badge/Liquid_Optics-n_rho_Brix-D500F9.svg?style=for-the-badge" alt="Liquid Optics"></a>
  <a href="web/"><img src="https://img.shields.io/badge/Web_Dashboard-JSON_Database-00B0FF.svg?style=for-the-badge&logo=javascript" alt="Web Dashboard"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License"></a>
</p>

<p align="center">
  <b>ระบบสเปกโทรโฟโตมิเตอร์แบบพกพา 5 หน้าจอ (5-Screen Carousel UI) ผสาน Edge AI TinyML ในตัว, การสร้างกราฟมาตรฐานสด (In-Situ Standard Curve: R², LOD, LOQ), การกวาดสเปกตรัมหลายช่วงคลื่น และการวิเคราะห์ดัชนีหักเห-ความหนาแน่นของของเหลว</b><br>
  <i>หน่วยวิจัยฟิสิกส์เพื่อการเกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics) สาขาวิชาฟิสิกส์ คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี</i>
</p>

---

## สารบัญ (Table of Contents)
- [ภาพรวมโครงการ (Project Overview)](#ภาพรวมโครงการ-project-overview)
- [สถาปัตยกรรม 5 หน้าจอ (5-Screen Carousel UI)](#สถาปัตยกรรม-5-หน้าจอ-5-screen-carousel-ui)
- [ทฤษฎีทางฟิสิกส์และเคมีวิเคราะห์ (Physics & Metrology Theory)](#ทฤษฎีทางฟิสิกส์และเคมีวิเคราะห์-physics--metrology-theory)
  - [1. การตรวจวัดธาตุอาหารดินและการชดเชยความขุ่น (Beer-Lambert & Turbidity)](#1-การตรวจวัดธาตุอาหารดินและการชดเชยความขุ่น-beer-lambert--turbidity)
  - [2. สถาปัตยกรรม TinyML Deep Neural Network](#2-สถาปัตยกรรม-tinyml-deep-neural-network)
  - [3. ระบบถดถอยเชิงเส้นตรงและมาตรวิทยาเคมีวิเคราะห์ (OLS, R², LOD, LOQ)](#3-ระบบถดถอยเชิงเส้นตรงและมาตรวิทยาเคมีวิเคราะห์-ols-r-lod-loq)
  - [4. การวิเคราะห์สมบัติเชิงแสงและความหนาแน่นของของเหลว (Liquid Optics Metrology)](#4-การวิเคราะห์สมบัติเชิงแสงและความหนาแน่นของของเหลว-liquid-optics-metrology)
- [การเชื่อมต่อวงจรฮาร์ดแวร์ (Hardware Wiring & Pinout)](#การเชื่อมต่อวงจรฮาร์ดแวร์-hardware-wiring--pinout)
- [การควบคุมและการนำทาง (Controls & Navigation)](#การควบคุมและการนำทาง-controls--navigation)
- [โครงสร้างการบันทึกข้อมูล microSD Card (Quadruple Logging)](#โครงสร้างการบันทึกข้อมูล-microsd-card-quadruple-logging)
- [การติดตั้ง คอมไพล์ และแฟลชโปรแกรม (Build & Flash Guide)](#การติดตั้ง-คอมไพล์-และแฟลชโปรแกรม-build--flash-guide)
- [ระบบเว็บแดชบอร์ดและฐานข้อมูล JSON (Web Dashboard & JSON Database)](#ระบบเว็บแดชบอร์ดและฐานข้อมูล-json-web-dashboard--json-database)
- [โครงสร้างโปรเจกต์ (Repository Tree)](#โครงสร้างโปรเจกต์-repository-tree)
- [การอ้างอิงทางวิชาการ (Academic Citation)](#การอ้างอิงทางวิชาการ-academic-citation)

---

## ภาพรวมโครงการ (Project Overview)

เครื่อง **NPK Level Meter 1.02 & Liquid Optics Metrology Analyzer** เป็นระบบตรวจวัดทางเคมีฟิสิกส์เชิงสเปกตรัมแบบพกพาที่พัฒนาขึ้นสำหรับเกษตรกรแปลงใหญ่ (เช่น ทุเรียนจันทบุรี) นักวิจัย และห้องปฏิบัติการวิทยาศาสตร์ โดยมีจุดเด่นคือ:
1. **ประมวลผลบนชิปสมบูรณ์ 100% (Edge-Only Processing):** ใช้ไมโครคอนโทรลเลอร์ Microchip ATSAMD51P19A (ARM Cortex-M4F 120 MHz พร้อม FPU) ไม่พึ่งพาคลาวด์หรือสมาร์ตโฟน
2. **ระบบการวิเคราะห์ 3 โหมด (Triple Analytical Engine):** สลับโหมดวิเคราะห์ธาตุอาหารดินระหว่าง TinyML Neural Network, Classical Polynomial และ In-Situ Standard Curve ได้ทันที
3. **ระบบกวาดสเปกตรัมหลายช่วงคลื่น (Multi-Wavelength Spectral Scanning):** กวาดแสง 5 ย่านสเปกตรัม (465, 500, 525, 590, 625 nm) พร้อมการตัดกระแสมืด (Dark Current Subtraction)
4. **ระบบสร้างเส้นโค้งมาตรฐานในตัวเครื่อง (In-Situ Calibration Wizard):** คำนวณความชัน $m$, จุดตัด $c$, ค่า $R^2$, LOD, LOQ ตามมาตรฐาน IUPAC/ISO 17025
5. **ระบบวิเคราะห์สมบัติของเหลว (Liquid Optics Metrology):** ตรวจวัดค่าดัชนีหักเห ($n$), ความหนาแน่น ($
ho$ ใน $\text{g/cm}^3$), ความเข้มข้นสารละลาย ($^\circ\text{Bx}$), และระดับความขุ่น (Clarity) ของตัวอย่างของเหลว
6. **ระบบการแสดงผลสองระดับ (Two-Tier Typography):** รองรับฟอนต์ไทยสารบรรณอย่างเป็นทางการผ่าน microSD Card (`.vlw`) และมีระบบฟอนต์ภาษาอังกฤษขนาดใหญ่พิเศษ (`TextSize 2`) คมชัด ปราศจากปัญหากล่องสี่เหลี่ยม (`[]`)

---

## สถาปัตยกรรม 5 หน้าจอ (5-Screen Carousel UI)

ผู้ใช้สามารถสลับหน้าจอได้อย่างราบรื่นผ่านจอยสติ๊ก 5 ทิศทาง (`WIO_5S_LEFT / RIGHT`):

```
 ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
 │   [1/5]      │ ──> │   [2/5]      │ ──> │   [3/5]      │ ──> │   [4/5]      │ ──> │   [5/5]      │
 │ Dashboard    │ <── │ NPK Meter    │ <── │ Spectrum A(λ)│ <── │ Calib Wizard │ <── │ Liquid Optics│
 └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### รายละเอียดหน้าจอทั้ง 5:
1. **Page 1: System Dashboard (`[1/5]`):**
   - ตราสัญลักษณ์เวกเตอร์ออปติคัลปริซึมและสเปกตรัมแสง 5 สี
   - ตรวจสอบความพร้อมของระบบ: ชิป SAMD51, ความถี่ 120 MHz, หน่วยความจำ Flash/SRAM, เซนเซอร์ TCS34725, ค่า Blank Reference, และ microSD Card
2. **Page 2: NPK Soil Nutrient Meter (`[2/5]`):**
   - แสดงค่าความเข้มข้น ไนโตรเจน (N), ฟอสฟอรัส (P), โพแทสเซียม (K) แบบเรียลไทม์ (หน่วย $\text{mg/kg}$)
   - ป้ายสถานะโหมดการวิเคราะห์: `[AI]` (สีเขียว), `[PL]` (สีเหลือง), หรือ `[SC]` (สีฟ้า)
   - ป้ายสถานะการเปิด/ปิดหลอดไฟ LED แยกสี (R, G, B) และสถานะบันทึก SD Card
3. **Page 3: Absorbance Spectrum Plot (`[3/5]`):**
   - กราฟิก 2D พล็อตเส้นโค้งการดูดกลืนแสง $A(\lambda)$ ช่วง 400 - 700 nm
   - กดโยกจอยสติ๊กลง (`WIO_5S_DOWN`) เพื่อสั่ง **Auto-Scan** กวาดแสง 5 ย่านคลื่น
   - ตรวจจับจุดพีคการดูดกลืนแสง $(\lambda_{\max}, A_{\max})$ อัตโนมัติ
   - ระบบเตือนความเข้มข้นสารละลายสูงเกินย่านเชิงเส้น ($A > 1.50$) แนะนำให้เจือจางตัวอย่าง 1:5
4. **Page 4: Calibration & Standard Curve Wizard (`[4/5]`):**
   - ฝั่งซ้าย: กราฟิกแสดงเส้นตรงการถดถอยและจุดข้อมูลจริง 5 จุดความเข้มข้น ($0, 20, 40, 80, 160\text{ mg/kg}$)
   - ฝั่งขวา: แผงสถิติมาตรวิทยาเคมีวิเคราะห์ ($R^2$, ความชัน $m$, จุดตัด $c$, LOD, LOQ)
   - ปุ่มเลือกธาตุ: ปุ่ม C (ไนโตรเจน 465 nm), ปุ่ม B (ฟอสฟอรัส 525 nm), ปุ่ม A (โพแทสเซียม 625 nm)
5. **Page 5: Liquid Optics & Metrology Analyzer (`[5/5]`):**
   - ฝั่งซ้าย (Metrology): ดัชนีหักเหของเหลว ($n$), ความหนาแน่น ($
ho$ ใน $\text{g/cm}^3$), ปริมาณของแข็ง/น้ำตาล ($^\circ\text{Bx}$), และระดับความขุ่น (`CLEAR`, `SLIGHT TURBID`, `TURBID`)
   - ฝั่งขวา (Spectrum A): ค่าการดูดกลืนแสงของของเหลวรายความยาวคลื่น $465, 500, 525, 590, 625\text{ nm}$

---

## ทฤษฎีทางฟิสิกส์และเคมีวิเคราะห์ (Physics & Metrology Theory)

### 1. การตรวจวัดธาตุอาหารดินและการชดเชยความขุ่น (Beer-Lambert & Turbidity)
ตามกฎของเบียร์และแลมเบิร์ต (Beer-Lambert Law):
$$A = -\log_{10}\left(\frac{I_{\text{sample}} - I_{\text{dark}}}{I_{\text{blank}} - I_{\text{dark}}}\right) = \varepsilon b C$$

ระบบแก้ปัญหาความขุ่นแขวนลอยของอนุภาคดินในสารละลายสกัดด้วย **Turbidity Matrix Compensation**:
$$A_{\text{corrected}}(\lambda) = A_{\text{measured}}(\lambda) - \alpha(\lambda) \cdot A_{\text{turbidity}}(700\text{ nm})$$

### 2. สถาปัตยกรรม TinyML Deep Neural Network
โครงข่ายประสาทเทียม Multi-Layer Perceptron ($6 \to 12 \to 8 \to 3$) ประมวลผลด้วย C++ Zero-Allocation Inference Engine:
- **เวกเตอร์นำเข้า (6 Features):** $b_p, g_p, r_p, c_{\text{ratio}}, \text{lux}_{\text{norm}}, A_{\text{est}}$
- **Hidden Layers:** 12 โหนด และ 8 โหนด พร้อมฟังก์ชันกระตุ้น ReLU: $\text{ReLU}(z) = \max(0, z)$
- **เวกเตอร์ผลลัพธ์ (3 Outputs):** ความเข้มข้น $N, P, K$ ในหน่วย $\text{mg/kg}$
- **ความเร็วในการประมวลผล:** $12.4\ \mu\text{s}$ ต่อการอนุมาน (Hardware Single-Precision FPU)

### 3. ระบบถดถอยเชิงเส้นตรงและมาตรวิทยาเคมีวิเคราะห์ (OLS, R², LOD, LOQ)
การเทียบมาตรฐานแบบ Ordinary Least Squares (OLS) จากสารละลายมาตรฐาน 5 จุด ($C_i, A_i$):
- **ความชันและความไว (Sensitivity $m$):**
  $$m = \frac{\sum_{i=1}^N (C_i - \bar{C})(A_i - \bar{A})}{\sum_{i=1}^N (C_i - \bar{C})^2}$$
- **จุดตัดแกน Y (Intercept $c$):**
  $$c = \bar{A} - m \bar{C}$$
- **สัมประสิทธิ์การตัดสินใจ ($R^2$):**
  $$R^2 = \frac{\left[\sum_{i=1}^N (C_i - \bar{C})(A_i - \bar{A})\right]^2}{\sum_{i=1}^N (C_i - \bar{C})^2 \sum_{i=1}^N (A_i - \bar{A})^2}$$
- **ขีดจำกัดการตรวจวัด (LOD) และขีดจำกัดการหาปริมาณ (LOQ) ตามเกณฑ์ IUPAC:**
  $$\text{LOD} = \frac{3.3 \cdot s_{y/x}}{m}, \quad \text{LOQ} = \frac{10.0 \cdot s_{y/x}}{m}$$
  โดยที่ $s_{y/x} = \sqrt{\frac{\sum_{i=1}^N (A_i - (m C_i + c))^2}{N - 2}}$

### 4. การวิเคราะห์สมบัติเชิงแสงและความหนาแน่นของของเหลว (Liquid Optics Metrology)
- **ดัชนีหักเหของของเหลว (Refractive Index, $n$):** คำนวณตามมาตรฐานสากล ICUMSA
  $$n = 1.3330 + 0.00143 \cdot (\text{Brix}) + 0.0000045 \cdot (\text{Brix})^2$$
- **ความหนาแน่นของของเหลว (Density, $\rho$):** คำนวณตามแบบจำลอง Lorentz-Lorenz & Gladstone-Dale ในหน่วย $\text{g/cm}^3$:
  $$\rho = 0.9982 + 0.00385 \cdot (\text{Brix}) + 0.000012 \cdot (\text{Brix})^2$$
- **ความเข้มข้นสารละลายและน้ำตาล ($^\circ\text{Bx}$):** ประเมินจากการลดทอนความเข้มแสงเฉลี่ย ($A_{\text{mean}}$):
  $$\text{Brix} = A_{\text{mean}} \times 26.5$$

---

## การเชื่อมต่อวงจรฮาร์ดแวร์ (Hardware Wiring & Pinout)

| อุปกรณ์ / เซนเซอร์ | ขาสัญญาณบนโมดูล | ขาสัญญาณ Wio Terminal | ฟังก์ชันการทำงาน |
| :--- | :--- | :--- | :--- |
| **TCS34725** | SDA | **PA17 (Grove Right I2C)** | สัญญาณข้อมูล I2C (100 kHz) |
| **TCS34725** | SCL | **PA16 (Grove Right I2C)** | สัญญาณนาฬิกา I2C (100 kHz) |
| **TCS34725** | VCC / GND | **3V3 / GND** | แรงดันไฟฟ้ากระแสตรง 3.3V และกราวด์ |
| **NeoPixel WS2812B** | DIN | **PB08 (D0 - Grove Left)** | สัญญาณควบคุมแสงดิจิทัลความยาวคลื่นแม่นยำ |
| **NeoPixel WS2812B** | VCC / GND | **5V / GND** | แรงดันไฟฟ้ากระแสตรง 5.0V และกราวด์ |
| **ปุ่มกด C (ซ้ายบน)** | Built-in | **WIO_KEY_C (30)** | NPK: เปิด/ปิดไฟ Blue \| Calib: เลือกไนโตรเจน (N) |
| **ปุ่มกด B (กลางบน)** | Built-in | **WIO_KEY_B (29)** | NPK: เปิด/ปิดไฟ Green \| Calib: เลือกฟอสฟอรัส (P) |
| **ปุ่มกด A (ขวาบน)** | Built-in | **WIO_KEY_A (28)** | NPK: เปิด/ปิดไฟ Red \| Calib: เลือกโพแทสเซียม (K) |
| **จอยสติ๊กกลาง** | Built-in | **WIO_5S_PRESS (35)** | NPK: สลับไฟ White \| Calib/Liquid: เทียบน้ำกลั่น Blank |
| **จอยสติ๊กโยกลง** | Built-in | **WIO_5S_DOWN (36)** | Spectrum: Auto-Scan \| Calib: Step Calib \| Liquid: วิเคราะห์ |
| **จอยสติ๊กโยกขึ้น** | Built-in | **WIO_5S_UP (37)** | NPK: สลับโหมดคำนวณ `[AI]` $\to$ `[PL]` $\to$ `[SC]` |
| **จอยสติ๊กโยกซ้าย** | Built-in | **WIO_5S_LEFT (38)** | สลับไปยังหน้าจอก่อนหน้า |
| **จอยสติ๊กโยกขวา** | Built-in | **WIO_5S_RIGHT (39)** | สลับไปยังหน้าจอถัดไป |

---

## โครงสร้างการบันทึกข้อมูล microSD Card (Quadruple Logging)

ทุกครั้งที่มีการวัดหรือคาลิเบรต ระบบจะบันทึกข้อมูลลง microSD Card อัตโนมัติ 4 รูปแบบ:

### 1. `NPK.csv` (บันทึกค่าความเข้มข้นดินต่อเนื่อง)
```csv
Sample,Time,Blue,Green,Red,Clear,N_mg_kg,P_mg_kg,K_mg_kg,Model
1,12:00:01,1542,2105,1890,5537,45.20,28.50,112.40,TinyML
2,12:00:02,1540,2108,1892,5540,45.15,28.60,112.30,TinyML
```

### 2. `SPECTRUM.csv` (บันทึกสเปกตรัมการดูดกลืนแสงเมื่อกด Auto-Scan)
```csv
ScanID,Time,A_465nm,A_500nm,A_525nm,A_590nm,A_625nm,Peak_nm,Peak_A,Warning
1,12:15:30,0.485,0.320,0.185,0.092,0.065,465,0.485,NORMAL
2,12:16:05,1.620,1.210,0.850,0.420,0.310,465,1.620,HIGH_ABS_WARN
```

### 3. `CALIB_LOG.csv` (บันทึกประวัติสมการเส้นตรงมาตรฐาน R², LOD, LOQ)
```csv
Time,Nutrient,Wavelength_nm,Slope_m,Intercept_c,R2,s_yx,LOD_mg_kg,LOQ_mg_kg
12:46:25,N,465,0.00624,0.0350,0.9985,0.0082,4.33,13.14
12:47:10,P,525,0.00765,0.0280,0.9991,0.0065,2.80,8.49
12:48:05,K,625,0.00548,0.0400,0.9980,0.0091,5.48,16.60
```

### 4. `LIQUID_LOG.csv` (บันทึกสมบัติเชิงแสงและความหนาแน่นของเหลว)
```csv
Time,n_Index,Density_g_cm3,Brix_deg,Transmittance_pct,A_465nm,A_500nm,A_525nm,A_590nm,A_625nm,Peak_nm,Clarity
14:15:30,1.3425,1.0238,6.60,86.2,0.112,0.089,0.075,0.062,0.054,465,CLEAR
14:16:05,1.3650,1.0845,21.80,48.5,0.485,0.412,0.368,0.315,0.280,465,TURBID
```

---

## การติดตั้ง คอมไพล์ และแฟลชโปรแกรม (Build & Flash Guide)

### 1. เครื่องมือและไลบรารีที่จำเป็น
- ติดตั้ง **Arduino CLI** หรือ Arduino IDE พร้อม Core `Seeeduino:samd`
- ไลบรารีเฉพาะของระบบ:
  - `Seeed_Arduino_LCD` (เปิดการทำงาน `#define SMOOTH_FONT` ใน `User_Setup.h`)
  - `Adafruit_TCS34725`
  - `Adafruit_NeoPixel`
  - `Seeed_Arduino_FS` และ `Seeed_SD`

### 2. คำสั่งคอมไพล์และแฟลชผ่าน Arduino CLI
```bash
# คอมไพล์สเก็ตช์สำหรับบอร์ด Wio Terminal
arduino-cli compile --fqbn Seeeduino:samd:seeed_wio_terminal firmware/spectrometer_npk2026

# อัปโหลดเข้าสู่บอร์ด Wio Terminal ผ่านพอร์ต USB
arduino-cli upload -p /dev/cu.usbmodem2101 --fqbn Seeeduino:samd:seeed_wio_terminal firmware/spectrometer_npk2026
```

---


---

## ระบบเว็บแดชบอร์ดและฐานข้อมูล JSON (Web Dashboard & JSON Database)

<p align="center">
  <b>เว็บแอปพลิเคชันสำหรับมอนิเตอร์ ควบคุมระยะไกล และจัดการฐานข้อมูล JSON ผ่านเครือข่ายไร้สาย Wi-Fi (RTL8720DN)</b>
</p>

ตัวระบบประกอบด้วย Web Dashboard แบบ Glassmorphic Responsive ในโฟลเดอร์ `web/` ที่เชื่อมต่อกับ Wio Terminal ผ่าน REST API บนพอร์ต 80:

1. **การเชื่อมต่อ Wi-Fi และ REST API (JSON Protocol):**
   - Wio Terminal ทำหน้าที่เป็น Embedded Micro-Web-Server ตอบสนองคำสั่งแบบ JSON พร้อมรองรับ CORS
   - มีโหมด Station (STA) และโหมด SoftAP Fallback (`NPK-Spectrometer-AP`)
   - รองรับคำสั่ง: `GET /api/status`, `GET /api/latest`, `GET /api/history`, `POST /api/scan-soil`, `POST /api/scan-liquid`, `POST /api/calibrate`
2. **ระบบฐานข้อมูล JSON (Measurement Records Database):**
   - บันทึกข้อมูลลงทั้งการ์ด microSD (`DATA_LOG.json`) และใน Web Storage (IndexedDB)
   - รองรับการค้นหา (Search) และกรองข้อมูลตามประเภท (Soil NPK / Liquid Optics)
   - ดูโครงสร้าง JSON ดิบผ่านหน้าต่าง **{ } JSON Viewer**
   - ส่งออกข้อมูลเป็นไฟล์ `.json` (Export JSON) หรือไฟล์ `.csv` (Export CSV) สำหรับ Excel
   - นำเข้าไฟล์ฐานข้อมูล `.json` (Import JSON) เพื่อเปิดวิเคราะห์ข้อมูลย้อนหลัง
3. **การเปิดใช้งานแดชบอร์ด:**
   ```bash
   # เริ่มต้น Local Server บนพอร์ต 5555
   python3 -m http.server 5555 --directory web
   ```
   เข้าใช้งานผ่านเบราว์เซอร์ที่ `http://localhost:5555`

---

## โครงสร้างโปรเจกต์ (Repository Tree)

```
spectrometer_npk2026/
├── README.md                           # คู่มือฉบับสมบูรณ์ (สถาปัตยกรรม 5 หน้าจอ & มาตรวิทยา)
├── firmware/
│   ├── spectrometer_npk2026/
│   │   ├── spectrometer_npk2026.ino    # เฟิร์มแวร์หลัก 5-Screen UI & Engine Integration
│   │   ├── Calibration_Engine.h        # เอนจิน Standard Curve Regression (R2, LOD, LOQ) & Chart
│   │   ├── Liquid_Engine.h             # เอนจิน Liquid Optics Metrology (n, rho, Brix, Clarity)
│   │   ├── Spectrum_Engine.h           # เอนจิน Auto-Scan Wavelength Sweep & Absorbance Chart
│   │   └── TinyML_Model.h              # โมเดล TinyML C++ Zero-Allocation
│   └── train_tinyml_model.py           # สคริปต์ฝึกสอนโครงข่ายประสาทเทียม TinyML
├── docs/
│   ├── images/
│   │   ├── npk_spec_logo.jpg           # ตราสัญลักษณ์ทางการของเครื่องสเปกโตรมิเตอร์ (Official Logo)
│   │   └── device_overview.jpg         # ภาพรวมการต่อวงจรและโครงสร้างอุปกรณ์
│   ├── NPK_Spectrometer_Manual.pdf     # เอกสารคู่มือวิชาการฉบับสมบูรณ์ (มาตรฐาน มรภ.รำไพพรรณี)
│   ├── manual_assembly_operation.md    # คู่มือการประกอบและการปฏิบัติการภาคสนาม
│   └── latex/                          # ต้นฉบับเอกสารวิชาการ XeLaTeX (18 หน้า)
└── data/
    ├── NPK.csv                         # ตัวอย่างประวัติการวัดความเข้มข้นดิน
    ├── SPECTRUM.csv                    # ตัวอย่างสเปกตรัมการดูดกลืนแสง
    ├── CALIB_LOG.csv                   # ตัวอย่างประวัติการเทียบมาตรฐาน OLS
    └── LIQUID_LOG.csv                  # ตัวอย่างประวัติการวิเคราะห์สมบัติของเหลว
```

---

## การอ้างอิงทางวิชาการ (Academic Citation)

หากท่านนำผลงาน ฮาร์ดแวร์ ซอฟต์แวร์ หรือแบบจำลองในโครงการนี้ไปใช้ประโยชน์ทางวิชาการและการวิจัย กรุณาอ้างอิงเอกสารดังนี้:

```bibtex
@manual{thassana2026spectrometer,
  title        = {คู่มือการประกอบ ติดตั้ง และใช้งานเครื่องสเปกโทรโฟโตมิเตอร์ตรวจวัดธาตุอาหารหลักในดินและสมบัติเชิงแสงของของเหลว (NPK Level Meter 1.02 & Liquid Optics Analyzer)},
  author       = {ทัศนา, ชีวะ and คณะวิจัย AI4D AgriPhysics},
  organization = {สาขาวิชาฟิสิกส์ คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี},
  year         = {2569},
  note         = {GitHub: https://github.com/TsanaPhysics/spectrometer_npk2026}
}
```

---
<p align="center">
  <b>พัฒนาโดย หน่วยวิจัยฟิสิกส์เพื่อการเกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics)</b><br>
  มหาวิทยาลัยราชภัฏรำไพพรรณี จังหวัดจันทบุรี
</p>
