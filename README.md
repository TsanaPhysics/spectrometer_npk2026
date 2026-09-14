# spectrometer_npk2026

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Seeed Wio Terminal](https://img.shields.io/badge/Platform-Seeed%20Wio%20Terminal-blue.svg)](https://www.seeedstudio.com/Wio-Terminal-p-4509.html)
[![Core: ATSAMD51](https://img.shields.io/badge/MCU-ATSAMD51%20Cortex--M4F-green.svg)](https://www.microchip.com/en-us/product/ATSAMD51P19A)
[![Sensor: TCS34725](https://img.shields.io/badge/Sensor-Adafruit%20TCS34725-red.svg)](https://www.adafruit.com/product/1334)
[![RBRU Academic Standard](https://img.shields.io/badge/Standard-RBRU%20Academic%20Textbook-gold.svg)](https://www.rbru.ac.th)

**NPK Level Meter 1.02** — เครื่องสเปกโทรโฟโตมิเตอร์ตรวจวัดปริมาณธาตุอาหารหลักในดิน (ไนโตรเจน ฟอสฟอรัส โพแทสเซียม) แบบพกพาความแม่นยำสูง  
วิจัยและพัฒนาโดย **หน่วยวิจัยฟิสิกส์เพื่อการเกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics)**  
สาขาวิชาฟิสิกส์ คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี  
*ผู้ช่วยศาสตราจารย์ ดร.ชีวะ ทัศนา และคณะ*

---

## สารบัญ (Table of Contents)
- [ภาพรวมโครงการ (Overview)](#ภาพรวมโครงการ-overview)
- [โครงสร้างระบบฮาร์ดแวร์ (Hardware Architecture)](#โครงสร้างระบบฮาร์ดแวร์-hardware-architecture)
- [การเชื่อมต่อวงจร (Wiring and Pinout)](#การเชื่อมต่อวงจร-wiring-and-pinout)
- [การควบคุมแสงสีผ่านปุ่มกด (Optical Controls)](#การควบคุมแสงสีผ่านปุ่มกด-optical-controls)
- [แบบจำลองการเทียบมาตรฐาน NPK (Calibration Models)](#แบบจำลองการเทียบมาตรฐาน-npk-calibration-models)
- [โครงสร้างโปรเจกต์ (Repository Structure)](#โครงสร้างโปรเจกต์-repository-structure)
- [คู่มือการประกอบและเอกสารทางวิชาการ (Documentation)](#คู่มือการประกอบและเอกสารทางวิชาการ-documentation)
- [ใบอนุญาตและการอ้างอิง (License and Citation)](#ใบอนุญาตและการอ้างอิง-license-and-citation)

---

## ภาพรวมโครงการ (Overview)
เครื่องสเปกโทรโฟโตมิเตอร์ตรวจวัดธาตุอาหารดิน **NPK Level Meter 1.02** เป็นอุปกรณ์ตรวจวัดในภาคสนามที่ออกแบบมาเพื่อลดระยะเวลาและต้นทุนในการวิเคราะห์ดินสำหรับการเกษตรแม่นยำ (Precision Agriculture) โดยใช้การวิเคราะห์การดูดกลืนแสงเชิงสเปกตรัม (Optical Spectroscopy) ร่วมกับหลอดกำเนิดแสง Grove RGB LED (WS2812B NeoPixel) และเซนเซอร์วัดสีความละเอียดสูง Adafruit TCS34725 ประมวลผลและแสดงผลทันทีเป็นหน่วย **mg/kg** บนหน้าจอ LCD ของ Seeed Studio Wio Terminal พร้อมบันทึกผลลงในการ์ด microSD Card

---

## โครงสร้างระบบฮาร์ดแวร์ (Hardware Architecture)
- **ประมวลผลกลาง:** Seeed Studio Wio Terminal (Microchip ATSAMD51P19A, ARM Cortex-M4F 120 MHz, 192 KB RAM, 512 KB Flash)
- **หน้าจอแสดงผล:** 2.4" TFT LCD (320x240) ขับเคลื่อนด้วย Seeed_Arduino_LCD
- **เซนเซอร์ตรวจวัดแสง:** Adafruit TCS34725 (16-bit RGB + Clear light sensor with IR filter) เชื่อมต่อผ่าน I2C บัส
- **แหล่งกำเนิดแสงสเปกตรัม:** Grove RGB LED (WS2812B NeoPixel) ความยาวคลื่น 465 nm (Blue), 525 nm (Green), 625 nm (Red) และ White
- **ช่องทางเดินแสง:** Standard Cuvette Holder ทางเดินแสง 10 mm
- **การบันทึกข้อมูล:** microSD Card SPI Interface บันทึกไฟล์ `NPK.txt`

---

## การเชื่อมต่อวงจร (Wiring and Pinout)

| อุปกรณ์ | พอร์ตบน Wio Terminal | ขาสัญญาณ | รายละเอียดหน้าที่ |
| :--- | :--- | :--- | :--- |
| **TCS34725 (SDA)** | Grove ขวา | SDA | สายสัญญาณข้อมูล I2C บัส |
| **TCS34725 (SCL)** | Grove ขวา | SCL | สายสัญญาณนาฬิกา I2C บัส |
| **TCS34725 (VCC/GND)** | Grove ขวา | 3V3 / GND | จ่ายไฟและกราวด์ให้เซนเซอร์ |
| **RGB LED (DIN)** | Grove ซ้าย | **D0** | ควบคุมเม็ดสี NeoPixel WS2812B |
| **RGB LED (VCC/GND)** | Grove ซ้าย | 5V / GND | จ่ายพลังงานให้หลอดไฟ |
| **ปุ่ม A** | ด้านบนตัวเครื่อง | WIO_KEY_A | สลับเปิด/ปิด **ไฟสีแดง (Red LED)** |
| **ปุ่ม B** | ด้านบนตัวเครื่อง | WIO_KEY_B | สลับเปิด/ปิด **ไฟสีเขียว (Green LED)** |
| **ปุ่ม C** | ด้านบนตัวเครื่อง | WIO_KEY_C | สลับเปิด/ปิด **ไฟสีน้ำเงิน (Blue LED)** |
| **จอยสติ๊กกลาง** | ด้านหน้าตัวเครื่อง | WIO_5S_PRESS | สลับเปิด/ปิด **ไฟสีขาว (White LED)** |

---

## การควบคุมแสงสีผ่านปุ่มกด (Optical Controls)
1. **ปุ่ม A (ขวาสุด):** สลับ เปิด/ปิด หลอดไฟ **สีแดง (RED)** สำหรับวิเคราะห์โพแทสเซียม (K)
2. **ปุ่ม B (ตรงกลาง):** สลับ เปิด/ปิด หลอดไฟ **สีเขียว (GREEN)** สำหรับวิเคราะห์ฟอสฟอรัส (P)
3. **ปุ่ม C (ซ้ายสุด):** สลับ เปิด/ปิด หลอดไฟ **สีน้ำเงิน (BLUE)** สำหรับวิเคราะห์ไนโตรเจน (N)
4. **จอยสติ๊กกดลงตรงกลาง:** สลับ เปิด/ปิด หลอดไฟ **สีขาว (WHITE)** เพื่อใช้ในการเทียบศูนย์ (Blank Calibration)

---

## แบบจำลองการเทียบมาตรฐาน NPK (Calibration Models)
คำนวณสัดส่วนความเข้มแสงสัมพัทธ์:
$$r_p = \frac{R}{R+G+B} \times 100, \quad g_p = \frac{G}{R+G+B} \times 100, \quad b_p = \frac{B}{R+G+B} \times 100$$

สมการพหุนามแปลงค่าความเข้มข้นธาตุอาหารดิน (mg/kg):
- **ไนโตรเจน (N):** $N = -185.42 + 8.234\,b_p - 0.0412\,b_p^2 + 0.000091\,b_p^3$
- **ฟอสฟอรัส (P):** $P = -224.18 + 12.56\,g_p - 0.0823\,g_p^2$
- **โพแทสเซียม (K):** $K = -18.92 + 1.842\,r_p + 0.0156\,r_p^2$

---

## โครงสร้างโปรเจกต์ (Repository Structure)
```
spectrometer_npk2026/
├── README.md                           # คำอธิบายโปรเจกต์และคู่มือเริ่มต้นฉบับย่อ
├── firmware/
│   ├── spectrometer_npk2026.ino        # เฟิร์มแวร์ Wio Terminal เวอร์ชันสมบูรณ์
│   ├── npk_detector_v622_SD.ino        # ไฟล์โค้ดสำรอง
│   └── build/                          # ไฟล์ไบนารี .bin, .hex, .uf2 สำหรับแฟลชทันที
├── docs/
│   ├── NPK_Spectrometer_Manual.pdf     # เอกสารคู่มือฉบับสมบูรณ์ (16 หน้า ผ่านมาตรฐาน RBRU)
│   ├── manual_assembly_operation.md    # คู่มือการประกอบและใช้งานแบบ Markdown
│   └── latex/                          # ซอร์สโค้ด XeLaTeX มาตรฐานตำรา มรภ.รำไพพรรณี
│       ├── main.tex
│       ├── styles/rbru_manual.sty
│       ├── chapters/
│       └── images/
└── data/
    └── NPK_sample_log.csv              # ตัวอย่างชุดข้อมูลผลการวัด
```

---

## คู่มือการประกอบและเอกสารทางวิชาการ (Documentation)
- อ่านคู่มือฉบับสมบูรณ์ในรูปแบบ Markdown ได้ที่ [docs/manual_assembly_operation.md](docs/manual_assembly_operation.md)
- ดาวน์โหลดคู่มือวิชาการฉบับพิมพ์ทางการ (PDF 16 หน้า จัดหน้าตามระเบียบ มรภ.รำไพพรรณี) ได้ที่ [docs/NPK_Spectrometer_Manual.pdf](docs/NPK_Spectrometer_Manual.pdf)

---

## ใบอนุญาตและการอ้างอิง (License and Citation)
ผลงานนี้เผยแพร่ภายใต้สัญญาอนุญาต **MIT License**  
หากนำผลงานหรือแบบจำลองไปใช้ในงานวิจัยทางวิชาการ กรุณาอ้างอิง:
> ชีวะ ทัศนา และคณะ. (2569). *คู่มือการประกอบ ติดตั้ง และใช้งานเครื่องสเปกโทรโฟโตมิเตอร์ตรวจวัดธาตุอาหารหลักในดิน (NPK Level Meter 1.02)*. หน่วยวิจัยฟิสิกส์เพื่อการเกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics) สาขาวิชาฟิสิกส์ คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี.
