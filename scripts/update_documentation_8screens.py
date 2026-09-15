#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update Documentation for 8-Screen Carousel UI & JC_AI_SciRBRU Branding
----------------------------------------------------------------------
Updates README.md and docs/manual_assembly_operation.md to reflect:
1. Research Unit: หน่วยวิจัยเกษตรดิจิทัล JC_AI_SciRBRU
2. 8-Screen Architecture [1/8] to [8/8]
3. Auto-Wavelength Switching System (Blue 465nm, Red 625nm, Dual Green/Red 525/625nm)
4. UI Enhancements:
   - Dashboard: "สเปกโทรโฟโตมิเตอร์", Double-Size Bold JC_AI_SciRBRU (Red-Orange-Yellow-Green) + "เกษตรดิจิทัล"
   - N, P, K: TextSize 4 Bold in Pink (Magenta), Blue (Cyan), Red
   - Soil pH: TextSize 3 Bold & Colorful "pH Level" (Cyan & Yellow)
   - Auto RTC Clock Compilation Sync
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def update_readme():
    readme_path = BASE_DIR / "README.md"
    content = readme_path.read_text(encoding="utf-8")

    # 1. Subtitle & Research Unit
    old_sub = (
        "<b>ระบบสเปกโทรโฟโตมิเตอร์แบบพกพา 5 หน้าจอ (5-Screen Carousel UI) ผสาน Edge AI TinyML ในตัว, "
        "การสร้างกราฟมาตรฐานสด (In-Situ Standard Curve: R², LOD, LOQ), การกวาดสเปกตรัมหลายช่วงคลื่น "
        "และการวิเคราะห์ดัชนีหักเห-ความหนาแน่นของของเหลว</b><br>\n"
        "  <i>หน่วยวิจัยฟิสิกส์เพื่อการเกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics) สาขาวิชาฟิสิกส์ "
        "คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี</i>"
    )
    new_sub = (
        "<b>ระบบสเปกโทรโฟโตมิเตอร์แบบพกพา 8 หน้าจอ (8-Screen Carousel UI) ผสาน Edge AI TinyML ในตัว, "
        "การสร้างกราฟมาตรฐานสด (In-Situ Standard Curve: R², LOD, LOQ), ระบบสลับความยาวคลื่นแสงอัตโนมัติ (Auto-Wavelength Switching), "
        "และการวิเคราะห์ pH ดินและสมบัติเชิงแสงของของเหลว</b><br>\n"
        "  <i>หน่วยวิจัยเกษตรดิจิทัล JC_AI_SciRBRU (Digital Agriphysics & AI Research Unit, JC_AI_SciRBRU) "
        "สาขาวิชาฟิสิกส์ คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี</i>"
    )
    if old_sub in content:
        content = content.replace(old_sub, new_sub)

    # 2. Table of Contents
    old_toc = "- [สถาปัตยกรรม 5 หน้าจอ (5-Screen Carousel UI)](#สถาปัตยกรรม-5-หน้าจอ-5-screen-carousel-ui)"
    new_toc = (
        "- [สถาปัตยกรรม 8 หน้าจอ (8-Screen Carousel UI)](#สถาปัตยกรรม-8-หน้าจอ-8-screen-carousel-ui)\n"
        "- [ระบบเปลี่ยนความยาวคลื่นแสงอัตโนมัติ (Auto-Wavelength Switching)](#ระบบเปลี่ยนความยาวคลื่นแสงอัตโนมัติ-auto-wavelength-switching)"
    )
    if old_toc in content:
        content = content.replace(old_toc, new_toc)

    # 3. Overview Highlights
    old_overview_section = re.search(r"## ภาพรวมโครงการ \(Project Overview\).*?## สถาปัตยกรรม 5 หน้าจอ", content, re.DOTALL)
    if old_overview_section:
        new_overview = """## ภาพรวมโครงการ (Project Overview)

เครื่อง **สเปกโทรโฟโตมิเตอร์ตรวจวัดธาตุอาหารหลักในดินและสมบัติเชิงแสงของของเหลว (NPK Level Meter 1.02 & Liquid Optics Metrology Analyzer)** พัฒนาโดย **หน่วยวิจัยเกษตรดิจิทัล JC_AI_SciRBRU** เป็นระบบตรวจวัดทางเคมีฟิสิกส์เชิงสเปกตรัมแบบพกพาที่พัฒนาขึ้นสำหรับเกษตรกรแปลงใหญ่ (เช่น สวนทุเรียนจันทบุรี) นักวิจัย และห้องปฏิบัติการวิทยาศาสตร์ โดยมีจุดเด่นคือ:
1. **ประมวลผลบนชิปสมบูรณ์ 100% (Edge-Only Processing):** ใช้ไมโครคอนโทรลเลอร์ Microchip ATSAMD51P19A (ARM Cortex-M4F 120 MHz พร้อม Hardware FPU) ไม่พึ่งพาคลาวด์หรือสมาร์ตโฟน
2. **ระบบการวิเคราะห์ 3 โหมด (Triple Analytical Engine):** สลับโหมดวิเคราะห์ธาตุอาหารดินระหว่าง TinyML Neural Network, Classical Polynomial และ In-Situ Standard Curve ได้ทันที
3. **ระบบสลับความยาวคลื่นแสงอัตโนมัติ (Auto-Wavelength Switching):** ปรับสีและความยาวคลื่นของแสง LED อัตโนมัติตามหน้าจอการวิเคราะห์ (Blue 465 nm สำหรับ N, Red 625 nm สำหรับ P และ K, Green/Red สำหรับ pH)
4. **ระบบสร้างเส้นโค้งมาตรฐานในตัวเครื่อง (In-Situ Calibration Wizard):** คำนวณความชัน $m$, จุดตัด $c$, ค่า $R^2$, LOD, LOQ ตามมาตรฐาน IUPAC/ISO 17025
5. **ระบบวิเคราะห์ความเป็นกรดด่างและสมบัติของเหลว (Soil pH & Liquid Optics):** ตรวจวัดค่า pH ดิน พร้อมคำแนะนำสำหรับสวนทุเรียน และตรวจวัดค่าดัชนีหักเห ($n$), ความหนาแน่น ($\\rho$ ใน $\\text{g/cm}^3$), ความเข้มข้นสารละลาย ($^\\circ\\text{Bx}$)
6. **ระบบการแสดงผลแบบ High-Contrast Zero-Tofu UI:** ปราศจากปัญหากล่องสี่เหลี่ยมเต้าหู้ (`[][][]`) และไร้ปัญหาข้อความซ้อนทับกัน พร้อมระบบนาฬิกา RTC ปรับเทียบเวลาจริงอัตโนมัติ (`__TIME__`, `__DATE__`)
7. **เอกลักษณ์แบรนดิ้งวิจัยเฉพาะ `JC_AI_SciRBRU`:** ออกแบบตราสัญลักษณ์หลากสีระดับพรีเมียม (JC แดง, AI ส้ม, Sci เหลือง, RBRU เขียว)

---

## สถาปัตยกรรม 8 หน้าจอ"""
        content = content.replace(old_overview_section.group(0), new_overview)

    # 4. 8-Screen Section & Auto-Wavelength
    old_screens_section = re.search(r"## สถาปัตยกรรม (?:5|8) หน้าจอ \(.*?## ทฤษฎีทางฟิสิกส์", content, re.DOTALL)
    if old_screens_section:
        new_screens = """## สถาปัตยกรรม 8 หน้าจอ (8-Screen Carousel UI)

ผู้ใช้สามารถสลับหน้าจอได้อย่างราบรื่นผ่านจอยสติ๊ก 5 ทิศทาง (`WIO_5S_LEFT / RIGHT`):

```
 [1/8] Dashboard ──> [2/8] Nitrogen (N) ──> [3/8] Phosphorus (P) ──> [4/8] Potassium (K)
        │
        └───> [5/8] Soil pH ──> [6/8] NPK Matrix ──> [7/8] Calib Wizard ──> [8/8] System Info
```

### รายละเอียดหน้าจอทั้ง 8 หน้า:
1. **Page 1: System Dashboard (`[1/8]`):**
   - หัวข้อ **"สเปกโทรโฟโตมิเตอร์"** (ตัดคำว่า NPK ออก เพื่อความเป็นเครื่องมือวิทยาศาสตร์สากล)
   - แบรนด์ **`JC_AI_SciRBRU`** ขนาดใหญ่พิเศษ (TextSize 2, 4-Point Bold) ด้วยคู่สีเฉพาะ: **`JC` สีแดง (`TFT_RED`)**, **`AI` สีส้ม (`TFT_ORANGE`)**, **`Sci` สีเหลือง (`TFT_YELLOW`)**, และ **`RBRU` สีเขียว (`TFT_GREEN`)** จัดวางคู่กับข้อความภาษาไทย **"เกษตรดิจิทัล"**
   - ตราสัญลักษณ์เวกเตอร์ออปติคัลปริซึมและสเปกตรัมแสง 5 สี
   - ตรวจสอบความพร้อมของระบบ: SAMD51 120 MHz, FPU, หน่วยความจำ Flash/SRAM, เซนเซอร์ TCS34725, microSD Card, และนาฬิกา RTC ตรงตามเวลาจริง
2. **Page 2: Dedicated Nitrogen Assay (`[2/8]`):**
   - หลอดไฟ LED ปรับเข้าสู่แสงสีน้ำเงินความยาวคลื่นแม่นยำ **465 nm Blue LED** โดยอัตโนมัติ
   - แสดงค่าความเข้มข้นไนโตรเจนแบบเรียลไทม์ ตัวเลขขนาดใหญ่ 4 เท่า พร้อมตัวอักษร **`N` ขนาดใหญ่พิเศษ (TextSize 4) ตัวหนา สีชมพูอมม่วง (Magenta)** ต่อท้ายหน่วย $\\text{mg/kg}$
   - ป้ายกำกับโหมด `[AI TinyML]`, `[PL Poly]`, หรือ `[SC StdCurv]`
3. **Page 3: Dedicated Phosphorus Assay (`[3/8]`):**
   - หลอดไฟ LED ปรับเข้าสู่แสงสีแดงความยาวคลื่น **625 nm Red LED** โดยอัตโนมัติ
   - แสดงค่าความเข้มข้นฟอสฟอรัสแบบเรียลไทม์ พร้อมตัวอักษร **`P` ขนาดใหญ่พิเศษ (TextSize 4) ตัวหนา สีน้ำเงินสด (Cyan/Blue)**
4. **Page 4: Dedicated Potassium Assay (`[4/8]`):**
   - หลอดไฟ LED ปรับเข้าสู่แสงสีแดงความยาวคลื่น **625 nm Red LED** โดยอัตโนมัติ
   - แสดงค่าความเข้มข้นโพแทสเซียมแบบเรียลไทม์ พร้อมตัวอักษร **`K` ขนาดใหญ่พิเศษ (TextSize 4) ตัวหนา สีแดงสด (Red)**
5. **Page 5: Soil pH Assay (`[5/8]`):**
   - หลอดไฟ LED ปรับเป็นโหมดตรวจวัดสีย้อมอินดิเคเตอร์คู่ความยาวคลื่น **525/625 nm**
   - แสดงข้อความ **`pH Level` ขนาดใหญ่ (TextSize 3) ตัวหนา Multi-Pass Rendering พร้อมคู่สีสันสดใส (`pH` สีฟ้าสดใส Neon Cyan `0x07FF` และ `Level` สีเหลืองนีออน Bright Yellow `TFT_YELLOW`)**
   - กราฟิกแท่งสเกลวัดความเป็นกรดด่างเชิงแสง ($3.5 - 8.5\\text{ pH}$) พร้อมระบบวินิจฉัยและคำแนะนำการปรับปรุงดินเฉพาะทางสำหรับสวนทุเรียน
6. **Page 6: Full NPK Nutrient Matrix (`[6/8]`):**
   - หน้าจอรวมตารางธาตุอาหารหลักทั้ง 3 ชนิด (N, P, K) ในหน้าเดียว พร้อมแถบกราฟิกแสดงระดับธาตุอาหาร (ต่ำ-เหมาะสม-สูง)
7. **Page 7: Calibration & Standard Curve Wizard (`[7/8]`):**
   - ฝั่งซ้าย: กราฟิกแสดงเส้นตรงการถดถอยและจุดข้อมูลจริง 5 จุดความเข้มข้น ($0, 20, 40, 80, 160\\text{ mg/kg}$)
   - ฝั่งขวา: แผงสถิติมาตรวิทยาเคมีวิเคราะห์ ($R^2$, ความชัน $m$, จุดตัด $c$, LOD, LOQ ตามมาตรฐาน IUPAC/ISO 17025)
   - ปุ่มเลือกธาตุ: ปุ่ม C (ไนโตรเจน 465 nm), ปุ่ม B (ฟอสฟอรัส 525 nm), ปุ่ม A (โพแทสเซียม 625 nm)
8. **Page 8: System Diagnostics & Core Info (`[8/8]`):**
   - ตรวจสอบรายละเอียดสถานะฮาร์ดแวร์ การจัดการพลังงาน สวิตช์สลับโมเดลคำนวณ ข้อมูลผู้พัฒนา ผศ.ดร.ชีวะ ทัศนา และแบรนดิ้ง **`JC_AI_SciRBRU`**

---

## ระบบเปลี่ยนความยาวคลื่นแสงอัตโนมัติ (Auto-Wavelength Switching)

ระบบเฟิร์มแวร์ได้รับการออกแบบให้มีฟังก์ชัน **Auto-Optics Wavelength Switching Engine** เพื่อลดความผิดพลาดของผู้ใช้งาน (Zero Human Error) โดยฮาร์ดแวร์จะเปลี่ยนสีและความยาวคลื่นของแหล่งกำเนิดแสง LED ทันทีที่ผู้ใช้เปลี่ยนหน้าจอ:

| หน้าจอที่กำลังแสดงผล | แหล่งกำเนิดแสง LED ที่เปิดอัตโนมัติ | ความยาวคลื่นแสง ($\\lambda$) | เหตุผลทางเคมีฟิสิกส์เชิงแสง |
| :--- | :--- | :--- | :--- |
| **Page 2: Nitrogen (N)** | **Blue LED** | $\\approx 465\\text{ nm}$ | ดูดกลืนแสงสูงสุดในสารละลายสกัดไนเตรต/แอมโมเนีย (สีส้มอมน้ำตาล) |
| **Page 3: Phosphorus (P)** | **Red LED** | $\\approx 625\\text{ nm}$ | ดูดกลืนแสงสูงสุดในสารเชิงซ้อนฟอสโฟโมลิบดีนัมบลู (Molybdenum Blue) |
| **Page 4: Potassium (K)** | **Red LED** | $\\approx 625\\text{ nm}$ | วัดการกระเจิงแสงและการลดทอนความเข้มของตะกอนเตตระฟีนิลบอเรต |
| **Page 5: Soil pH** | **Dual Green/Red** | $\\approx 525\\text{ / }625\\text{ nm}$ | วัดอัตราส่วนการดูดกลืนแสงของสีย้อม Universal / Bromothymol Blue |
| **Page 7: Calibration** | **ตามธาตุที่เลือก (C/B/A)** | $465\\text{ / }525\\text{ / }625\\text{ nm}$ | ปรับตามธาตุอาหารมาตรฐานที่กำลังเทียบเส้นกราฟ |
| **Page 1, 6, 8 (Dashboard/Info)** | **Standby (Off/White)** | Full Spectrum / Off | พักแหล่งกำเนิดแสงเพื่อประหยัดพลังงานและยืดอายุการใช้งาน |

---

## ทฤษฎีทางฟิสิกส์"""
        content = content.replace(old_screens_section.group(0), new_screens)

    # 5. Footer Branding
    old_foot = "<b>พัฒนาโดย หน่วยวิจัยฟิสิกส์เพื่อการเกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics)</b>"
    new_foot = "<b>พัฒนาโดย หน่วยวิจัยเกษตรดิจิทัล JC_AI_SciRBRU (Digital Agriphysics & AI Research Unit)</b>"
    if old_foot in content:
        content = content.replace(old_foot, new_foot)

    readme_path.write_text(content, encoding="utf-8")
    print("Updated README.md successfully.")

def update_manual():
    manual_path = BASE_DIR / "docs" / "manual_assembly_operation.md"
    content = manual_path.read_text(encoding="utf-8")

    # 1. Header
    old_header = (
        "**หน่วยวิจัยฟิสิกส์เพื่อการเกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics)**  \n"
        "**สาขาวิชาฟิสิกส์ คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี**"
    )
    new_header = (
        "**หน่วยวิจัยเกษตรดิจิทัล JC_AI_SciRBRU (Digital Agriphysics & AI Research Unit)**  \n"
        "**สาขาวิชาฟิสิกส์ คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี**"
    )
    if old_header in content:
        content = content.replace(old_header, new_header)

    # 2. Table of Contents
    content = content.replace("4. สถาปัตยกรรม 5 หน้าจอและการควบคุมการทำงาน", "4. สถาปัตยกรรม 8 หน้าจอและการควบคุมการทำงาน (8-Screen Carousel UI)")

    # 3. Section 4 update
    old_sec4 = re.search(r"## 4\. สถาปัตยกรรม .*?## 5\. ทฤษฎีและแบบจำลอง", content, re.DOTALL)
    if old_sec4:
        new_sec4 = """## 4. สถาปัตยกรรม 8 หน้าจอและการควบคุมการทำงาน (8-Screen Carousel UI)

ระบบแสดงผลบนจอ LCD ขนาด 2.4 นิ้ว (320x240 พิกเซล) แบ่งออกเป็น 8 หน้าจอแบบ Carousel หมุนวนอย่างราบรื่น:

| หน้าจอ | รหัสหน้า | วัตถุประสงค์หลักและการแสดงผลเด่น |
| :---: | :--- | :--- |
| **Page 1** | `[1/8]` System Dashboard | แดชบอร์ดระบบ: แสดงหัวข้อ "สเปกโทรโฟโตมิเตอร์", ตราสัญลักษณ์เวกเตอร์ปริซึมออปติก, แบรนด์ **`JC_AI_SciRBRU`** ขนาดใหญ่ 2 เท่า (TextSize 2 ตัวหนา สี แดง-ส้ม-เหลือง-เขียว), "เกษตรดิจิทัล", นาฬิกา RTC ปรับเทียบเวลาจริงอัตโนมัติ และสถานะชิป/เซนเซอร์ |
| **Page 2** | `[2/8]` Dedicated Nitrogen Assay | ตรวจวัดไนโตรเจน (N): สลับไฟ **Blue LED (465 nm)** อัตโนมัติ, แสดงผลตัวเลขขนาดใหญ่ 4 เท่า พร้อมตัวอักษร **`N` ขนาดใหญ่พิเศษ (TextSize 4) ตัวหนา สีชมพูอมม่วง (Magenta)** ต่อท้าย $\\text{mg/kg}$ |
| **Page 3** | `[3/8]` Dedicated Phosphorus Assay | ตรวจวัดฟอสฟอรัส (P): สลับไฟ **Red LED (625 nm)** อัตโนมัติ, แสดงผลตัวเลขขนาดใหญ่ พร้อมตัวอักษร **`P` ขนาดใหญ่พิเศษ (TextSize 4) ตัวหนา สีน้ำเงินสด (Cyan/Blue)** |
| **Page 4** | `[4/8]` Dedicated Potassium Assay | ตรวจวัดโพแทสเซียม (K): สลับไฟ **Red LED (625 nm)** อัตโนมัติ, แสดงผลตัวเลขขนาดใหญ่ พร้อมตัวอักษร **`K` ขนาดใหญ่พิเศษ (TextSize 4) ตัวหนา สีแดงสด (Red)** |
| **Page 5** | `[5/8]` Soil pH Assay | ตรวจวัดค่าความเป็นกรดด่างดิน: สลับไฟ **Dual Green/Red LED (525/625 nm)** อัตโนมัติ, แสดงข้อความ **`pH Level` ขนาดใหญ่ (TextSize 3) ตัวหนา Multi-Pass สีฟ้าสดและเหลืองนีออน**, แถบสเกล $3.5 - 8.5\\text{ pH}$ และคำแนะนำปรับปรุงดินสำหรับสวนทุเรียน |
| **Page 6** | `[6/8]` Full NPK Nutrient Matrix | ตารางสรุปภาพรวมธาตุอาหารดิน 3 ชนิด (N, P, K) พร้อมแถบวัดระดับความอุดมสมบูรณ์ (ต่ำ-เหมาะสม-สูง) |
| **Page 7** | `[7/8]` In-Situ Calibration Wizard | ระบบเทียบมาตรฐานและสร้างเส้นโค้ง OLS ($R^2$, ความชัน $m$, จุดตัด $c$, LOD, LOQ ตามมาตรฐาน IUPAC/ISO 17025) |
| **Page 8** | `[8/8]` System Diagnostics & Core Info | การวินิจฉัยระบบ: สวิตช์สลับโหมดโมเดล AI TinyML / Polynomial / Standard Curve, อุณหภูมิ, หน่วยความจำ และเครดิต ผศ.ดร.ชีวะ ทัศนา พร้อมแบรนด์ `JC_AI_SciRBRU` |

### ระบบเปลี่ยนความยาวคลื่นแสงอัตโนมัติ (Auto-Wavelength Switching Engine)
เพื่อป้องกันข้อผิดพลาดในการเปิดแสงผิดสีของผู้ปฏิบัติงาน เฟิร์มแวร์จะเปลี่ยนแหล่งกำเนิดแสง LED ตามฟังก์ชันการตรวจวัดทันทีที่เปลี่ยนหน้าจอ:
- **หน้า 2 (Nitrogen):** เปิดไฟสีน้ำเงิน (465 nm) ดูดกลืนสูงสุดกับสารสกัดไนเตรต/แอมโมเนีย
- **หน้า 3 (Phosphorus):** เปิดไฟสีแดง (625 nm) ดูดกลืนสูงสุดกับสารเชิงซ้อนฟอสโฟโมลิบดีนัมบลู
- **หน้า 4 (Potassium):** เปิดไฟสีแดง (625 nm) วัดการลดทอนความเข้มแสงและการกระเจิงจากตะกอนเตตระฟีนิลบอเรต
- **หน้า 5 (Soil pH):** เปิดไฟคู่เขียว/แดง (525/625 nm) วิเคราะห์อัตราส่วนสีสีย้อมอินดิเคเตอร์

### การสั่งงานด้วยปุ่มกดและจอยสติ๊ก
- **จอยสติ๊กโยกซ้าย / ขวา (`WIO_5S_LEFT / RIGHT`):** เลื่อนสลับหน้าจอวนลูป 8 หน้าจอ
- **จอยสติ๊กโยกขึ้น (`WIO_5S_UP`):** หน้า Dashboard / NPK / System Info: สลับโหมดคำนวณ `[AI TinyML]` $\\to$ `[PL Poly]` $\\to$ `[SC StdCurv]`
- **จอยสติ๊กโยกลง (`WIO_5S_DOWN`):**
  - หน้า Calibrate: สั่งบันทึกจุดสารมาตรฐาน (Step Calib)
  - หน้า NPK / pH: สั่งอ่านค่าและบันทึกข้อมูลด่วน
- **จอยสติ๊กกดตรงกลาง (`WIO_5S_PRESS`):**
  - หน้า Calibrate: บันทึกค่าศูนย์เทียบน้ำกลั่น (Zero Blank Reference)
  - หน้าอื่น: สลับเปิด/ปิด ไฟแสงสีขาว (White LED) ตรวจสอบตัวอย่าง
- **ปุ่ม A, B, C (ด้านบนตัวเครื่อง):**
  - หน้า Calibrate: เลือกธาตุที่ต้องการเทียบมาตรฐาน (C=ไนโตรเจน 465nm, B=ฟอสฟอรัส 525nm, A=โพแทสเซียม 625nm)
  - หน้า NPK: สลับเปิด/ปิด หลอดไฟแมนนวล (C=น้ำเงิน, B=เขียว, A=แดง)

---

## 5. ทฤษฎีและแบบจำลอง"""
        content = content.replace(old_sec4.group(0), new_sec4)

    # 4. Footer
    content = content.replace("จัดทำโดย หน่วยวิจัยฟิสิกส์เพื่อการเกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics)", "จัดทำโดย หน่วยวิจัยเกษตรดิจิทัล JC_AI_SciRBRU (Digital Agriphysics & AI Research Unit)")

    manual_path.write_text(content, encoding="utf-8")
    print("Updated manual_assembly_operation.md successfully.")

if __name__ == "__main__":
    update_readme()
    update_manual()
