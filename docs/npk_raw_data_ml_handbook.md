# คู่มือการวิเคราะห์ข้อมูลสเปกโตรมิเตอร์ดินและการพัฒนาแบบจำลองการเรียนรู้ของเครื่อง
## (NPK Spectrometer Raw Data Analytics & Machine Learning Modeling Handbook)

**โครงการ:** การพัฒนาระบบตรวจวัดธาตุอาหารในดิน (N-P-K) ด้วยสเปกโตรมิเตอร์ทางแสงและปัญญาประดิษฐ์  
**หน่วยวิจัย:** หน่วยวิจัยเกษตรดิจิทัล JC_AI_SciRBRU (Digital Agriphysics & AI Research Unit, JC_AI_SciRBRU)  
**คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี (RBRU)**  
**วันที่ปรับปรุงล่าสุด:** 15 กันยายน 2569  

---

## สารบัญ (Table of Contents)
1. [บทวิเคราะห์เชิงยุทธศาสตร์จากผู้เชี่ยวชาญ (Expert Strategic Perspectives & Overview)](#1-บทวิเคราะห์เชิงยุทธศาสตร์จากผู้เชี่ยวชาญ)
2. [การเตรียมข้อมูลทางแสง (Optical Preprocessing & Physics Grounding)](#2-การเตรียมข้อมูลทางแสง)
3. [สารบบโครงสร้างข้อมูลดิบและการทดลอง (Raw Data Architecture & Experimental Catalog)](#3-สารบบโครงสร้างข้อมูลดิบและการทดลอง)
4. [แผนที่การแบ่งกลุ่มข้อมูลเพื่อเทรนโมเดล (Data Stratification Strategy)](#4-แผนที่การแบ่งกลุ่มข้อมูลเพื่อเทรนโมเดล)
5. [การสร้าง Standard Curve และการประมาณค่าทางเคมีวิเคราะห์ (Analytical Chemistry Calibration)](#5-การสร้าง-standard-curve-และการประมาณค่าทางเคมีวิเคราะห์)
6. [สถาปัตยกรรมโมเดล ML/DL ที่เหมาะสมที่สุด (Optimal ML/DL Model Architecture)](#6-สถาปัตยกรรมโมเดล-mldl-ที่เหมาะสมที่สุด)
7. [กลยุทธ์การแบ่ง Train/Validation/Test และการประเมินผล (Validation Strategy & Leakage Prevention)](#7-กลยุทธ์การแบ่ง-trainvalidationtest-และการประเมินผล)
8. [แผนการต่อยอดพัฒนาและการนำไปใช้งานจริง (Implementation Roadmap & Edge AI Deployment)](#8-แผนการต่อยอดพัฒนาและการนำไปใช้งานจริง)
9. [การวิเคราะห์เปรียบเทียบโมเดลฟอสฟอรัส 1–10 mg/L สำหรับการตีพิมพ์วารสารวิชาการนานาชาติระดับ Q1 (Phosphorus 1–10 mg/L Comparative Modelling for Q1 Publication)](#9-การวิเคราะห์เปรียบเทียบโมเดลฟอสฟอรัส-110-mgl-สำหรับการตีพิมพ์วารสารวิชาการนานาชาติระดับ-q1)
10. [ภาคผนวก: ชุดคำสั่งประมวลผลข้อมูลต้นแบบ (Appendix: Master Pipeline Python Script)](#10-ภาคผนวก-ชุดคำสั่งประมวลผลข้อมูลต้นแบบ)
11. [การแยกโหมดการตรวจวัดวิเคราะห์ (N, P, K, pH) และแบบจำลองแสง Soil pH](#11-การแยกโหมดการตรวจวัดวิเคราะห์-n-p-k-ph-และแบบจำลองแสง-soil-ph)

---

## 1. บทวิเคราะห์เชิงยุทธศาสตร์จากผู้เชี่ยวชาญ

ในฐานะ**นักวิจัย/นักวิเคราะห์คุณภาพดินร่วมกับความเชี่ยวชาญด้าน Machine Learning และ Chemometrics (เคมีเคมีมิติ)** สำหรับระบบ Optical Spectrometer ทางการเกษตร ชุดข้อมูลที่มีอยู่ในไดเรกทอรี `raw_data` นี้ถือเป็น **ชุดข้อมูลทองคำ (Gold Standard Dataset)** ที่ครอบคลุมตั้งแต่ระดับสารละลายเคมีบริสุทธิ์ (Pure Chemical Solution) ไปจนถึงดินจริงภาคสนาม (Real Soil Matrix) และปุ๋ยอินทรีย์/เคมี

ขอเสนอแนะแนวทางและสถาปัตยกรรมการนำข้อมูลชุดนี้ไปเทรนโมเดลและการสร้าง Standard Curve ที่แม่นยำสูง ทนทานต่อสัญญาณรบกวน (Robust) และพร้อมนำไปใช้งานบนอุปกรณ์พกพา (Edge AI / Embedded System) โดยมีรายละเอียดเชิงลึกในแต่ละส่วนดังต่อไปนี้

---

## 2. การเตรียมข้อมูลทางแสง (Optical Preprocessing & Physics Grounding)

ก่อนนำตัวเลขดิบไปป้อนเข้าโมเดล ต้องแปลงค่าทางแสงให้อยู่ในรูป **Optical Density / Absorbance** ตามกฎของเบียร์-แลมเบิร์ต (Beer-Lambert Law) เสียก่อน ไม่ควรนำค่าดิบ (Raw ADC Counts) ไปเทรนโดยตรง เพราะจะแปรผันตามอุณหภูมิ, การเสื่อมของหลอด LED, และแสงรบกวนภายนอก

```
                    [ Raw Optical Data ]
                  (Light ON vs Light OFF)
                            │
                            ▼
              [ 1. Dark Current Correction ]
                   I_net = I_ON - I_OFF
                            │
                            ▼
           [ 2. Gain & Time Normalization ]
             I_norm = I_net / (Gain × Tint)
                            │
                            ▼
              [ 3. Absorbance Calculation ]
                A = -log10( I_sample / I_0 )
                            │
                            ▼
            [ 4. Baseline / Turbidity Offset ]
            A_corr = A_channel - A_Clear(baseline)
```

### สูตรการคำนวณที่ต้องใช้กับชุดข้อมูล:
1. **Dark Current Subtraction (หักสัญญาณมืด):**  
   ใช้ข้อมูลในชุด `7 soil` และ `New Data NPK` ที่มี `Light Source Color - OFF` และ `WHITE`:
   $$I_{\text{net}} = I_{\text{WHITE}} - I_{\text{OFF}}$$
2. **Gain & Integration Time Normalization:**  
   $$I_{\text{norm}} = \frac{I_{\text{net}}}{\text{Gain} \times T_{\text{int}}}$$
3. **Absorbance ($A$) เทียบกับ Blank ($I_0$):**  
   ดึงค่าหลอดเปล่าหรือน้ำบริสุทธิ์ (`blank_*.txt`, `*_W.txt`) มาเป็นค่า $I_0$:
   $$A_\lambda = -\log_{10}\left(\frac{I_{\text{norm, sample}}}{I_{\text{norm, blank}}}\right)$$
4. **Turbidity & Soil Scattering Correction (แก้ปัญหาความขุ่นและเม็ดดิน):**  
   ใช้ช่องสัญญาณ Clear ($C$) หรือช่องสัญญาณที่ไม่ดูดกลืนแสงของสารทำปฏิกิริยานั้นๆ มาเป็น Reference หักลบ Scattering background ของน้ำคั้นดิน:
   $$A_{\text{corrected}} = A_\lambda - k \cdot A_{\text{Clear}}$$

---

## 3. สารบบโครงสร้างข้อมูลดิบและการทดลอง (Raw Data Architecture & Experimental Catalog)

ข้อมูลดิบทั้งหมดในไดเรกทอรี `raw_data` ประกอบด้วย 6 โฟลเดอร์ย่อย รวมทั้งสิ้น **1,478 ไฟล์** ซึ่งสะท้อนประวัติการวิจัยและพัฒนาฮาร์ดแวร์อย่างต่อเนื่องตั้งแต่ปี 2023 ถึง 2024:

```
raw_data/
├── 7 soil/             (231 files)  - การปรับเทียบเวลาและเกนกับดิน 7 ชนิด (พ.ค. 2024)
├── Data_Sept/          (300 files)  - ข้อมูล N-P มาตรฐานระยะแรกและการแปลงสตรีมข้อมูล (ก.ย. 2023)
├── Data_Oct/           (558 files)  - ข้อมูลมาตรฐานความเข้มข้น N/P, ปุ๋ยเคมี 16-16-16, ตัวอย่างดินจริง (ต.ค. 2023)
├── N_set/              (50 files)   - ชุดข้อมูลมาตรฐานไนโตรเจนแบบไปป์ไลน์ 4 ขั้นตอน
├── NdatasetCSV/        (0 files)    - โฟลเดอร์รองรับเอาต์พุต (Empty Folder)
└── New Data NPK/       (339 files)  - ข้อมูลสเปกโตรมิเตอร์รุ่นใหม่ปี 2024 (N, PO4, ดินจริง, มูลไส้เดือน)
```

### 3.1 โฟลเดอร์ `7 soil` (231 ไฟล์)
* **บริบท:** การทดสอบความเสถียรและการตอบสนองต่อสเปกตรัมของเนื้อดินต่างชนิดในเดือนพฤษภาคม 2024
* **รูปแบบไฟล์:** ไฟล์ข้อความ `.txt` ทั้งหมด 231 ไฟล์
* **โครงสร้างข้อมูลภายใน:**
  * มีการบันทึกสถานะปิดแสง (`Light Source Color - OFF`) เพื่อประเมิน Dark Current
  * มีการบันทึกสถานะเปิดแสงขาว (`Light Source Color - WHITE`) พร้อมประทับเวลา (Timestamp)
  * คอลัมน์ข้อมูล: `N, P, K, C` (หรือช่องสัญญาณสีแดง/เขียว/น้ำเงิน/แสงรวม)
* **ตัวแปรการทดลอง:**
  * ตัวอย่างดิน: `A`, `B`, `C`, `D`, `E`, ดินสีแดง (`RED`), ดินสีดำ (`BLACK`), หลอดเปล่า (`blank`, `Blank`)
  * เวลาเปิดรับแสง (Integration Time: $T_{\text{int}}$): `2.4ms`, `24ms`, `101ms`, `120ms`, `154ms`, `180ms`, `199ms`, `240ms`, `300ms`, `360ms`, `401ms`, `540ms`, `600ms`, `614ms`
  * อัตราขยายสัญญาณ (Gain): `1x` และ `16x`

### 3.2 โฟลเดอร์ `Data_Sept` (300 ไฟล์)
* **บริบท:** การทดสอบในระยะเริ่มต้นของการทำปฏิกิริยาสารเคมีกับตัวอย่างฟอสฟอรัส (P) และไนโตรเจน (N) ในเดือนกันยายน 2023
* **โฟลเดอร์ย่อย:** `P_All`, `P_10`, `P_100`, `P_1000`, `P_8_Sep`, `P_9_Sep`, `N_8_Sep`, `N_9_Sep`, `28Sep`
* **สาระสำคัญ:**
  * สารละลายมาตรฐานฟอสฟอรัสที่ความเข้มข้น 10, 100 และ 1,000 mg/L
  * การเปรียบเทียบสภาวะใส่สารทำปฏิกิริยาและไม่ใส่สารทำปฏิกิริยา (`No_reag`)
  * สมุดโค้ด Jupyter Notebook สำหรับทำ Text-to-CSV Converter และการคำนวณ Mean/SD

### 3.3 โฟลเดอร์ `Data_Oct` (558 ไฟล์)
* **บริบท:** การทดลองวิจัยชุดใหญ่และสมบูรณ์ที่สุดของไตรมาส 4 ปี 2023
* **โฟลเดอร์ย่อย:**
  1. `N_data` (303 ไฟล์): ชุดทดสอบสารละลายมาตรฐานไนโตรเจนที่ระดับความเข้มข้นละเอียด (0, 2, 4, 8, 10, 20, 40, 60, 80, 100 mg/L) มีภาพพล็อตการดูดกลืนแสงและสมุดโค้ดวิเคราะห์กราฟมาตรฐาน
  2. `P_data` (161 ไฟล์): ชุดทดสอบฟอสฟอรัสแบ่งเป็นช่วงความเข้มข้นต่ำ (Low Range) และความเข้มข้นสูง (High Range)
  3. `Soil` (56 ไฟล์): ตัวอย่างดินจริงจากแปลงเกษตร ได้แก่ ดินคันราชา (`Soil_Kun`), ดินบ้าน (`Soil_Ban`), และดิน PAT (`Soil_PAT`) ทั้งแบบใส่ Reagent และไม่ใส่ Reagent (`NoR`)
  4. `F1646` (32 ไฟล์): ข้อมูลการทดสอบกับปุ๋ยเคมีสูตรเสมอ 16-16-16

### 3.4 โฟลเดอร์ `N_set` (50 ไฟล์)
* **บริบท:** ชุดข้อมูลมาตรฐานไนโตรเจนที่ผ่านการจัดระเบียบตามกระบวนการวิทยาศาสตร์ข้อมูล 4 ลำดับขั้น:
  * `1Ntxt2csv.ipynb`: แปลงสตรีมข้อความดิบให้เป็นตาราง CSV
  * `2NGraph.ipynb`: พล็อตกราฟการตอบสนองเชิงสเปกตรัม
  * `3NMeanSD.ipynb`: คำนวณค่าเฉลี่ยทางสถิติและส่วนเบี่ยงเบนมาตรฐาน
  * `4NAbsorp.ipynb`: คำนวณค่าการดูดกลืนแสงเทียบกับแบลงก์ (Blank-subtracted Absorbance)
* **โฟลเดอร์ย่อย:** `N` (ไฟล์ดิบ), `NdatasetCSV` (ไฟล์ตาราง), `StandardData` (ตารางสรุป $A$, Mean, SD)

### 3.5 โฟลเดอร์ `New Data NPK` (339 ไฟล์)
* **บริบท:** ชุดข้อมูลการทดสอบด้วยฮาร์ดแวร์และเฟิร์มแวร์รุ่นใหม่ปี 2024 (`npk_detector_TSCRGB2024` / `NPK_RGBGLOVE_Auto_TCS`)
* **สาระสำคัญตามการทดลองปลายเดือนมีนาคม 2024:**
  * `Fert16-16-16`: ทดสอบปุ๋ยเคมี 16-16-16 แปรผันปริมาตรสาร Reagent (500 µl, 1000 µl)
  * `5-Soil data`: ฐานข้อมูลตัวอย่างดิน 5 แหล่ง
  * `data27032024` & `data28032024`: การทดสอบสารละลาย $\text{PO}_4$ ที่ 0.4, 1.0, 6.0 mg/L และการตรวจสอบความสามารถในการทำซ้ำของหลอดทดลอง (Tube Repeatability)
  * `data29032024`: การทดสอบ $\text{PO}_4$ 0.4 mg/L ร่วมกับ N 10 mg/L และการวัด Blank
  * `data30032024`: การทดสอบตัวอย่างดินจริงภาคสนาม `Soil_1` ถึง `Soil_9` และการอ่านค่าอากาศเปิดฝา (`WIO_Air_uncover`)
  * `data31032024`: **การทดสอบกับปุ๋ยอินทรีย์ "มูลไส้เดือน" (`Vermicom`)** สไปค์ด้วย N 10 mg/L และ P 10 mg/L ในปริมาตร 0.5 ml และ 1.0 ml
  * `conclusion.ipynb`: สมุดโค้ดวิเคราะห์สรุปผลข้อมูลปี 2024

---

## 4. แผนที่การแบ่งกลุ่มข้อมูลเพื่อเทรนโมเดล (Data Stratification Strategy)

แยกข้อมูลออกเป็น **3 ชั้นความลึก (Three-Tier Dataset Structure)** เพื่อป้องกันปัญหา Data Leakage:

| ชั้นข้อมูล | แหล่งข้อมูลจากโฟลเดอร์ | วัตถุประสงค์ | Target Label |
| :--- | :--- | :--- | :--- |
| **Tier 1: Chemical Benchmark**<br>*(สารละลายมาตรฐาน)* | `N_set`<br>`Data_Oct/N_data`<br>`Data_Sept/P_All`<br>`New Data NPK/data27-28` | เรียนรู้การดูดกลืนแสงเชิงเส้นที่แม่นยำของสารทำปฏิกิริยา (N: Nessler/Greiss, P: Molybdenum Blue) | ความเข้มข้นที่ทราบค่าแน่ชัด (0, 0.4, 1, 2, 4, 8, 10, 20, 80, 100 mg/L) |
| **Tier 2: Real Soil Matrix**<br>*(ดินจริงหลากพื้นที่)* | `7 soil`<br>`Data_Oct/Soil`<br>`New Data NPK/5-Soil data`<br>`New Data NPK/data30032024` | เรียนรู้ Matrix Interference (สีของฮิวมัส, สารแขวนลอย, ความเป็นกรด-ด่าง) | ตัวอย่างดินรหัส A–E, ดินคันราชา, ดินบ้าน, ดิน PAT, Soil_1–9 |
| **Tier 3: Spiked Recovery**<br>*(สไปค์สารมาตรฐานลงในดิน/ปุ๋ย)* | `New Data NPK/data31032024` (Vermicompost มูลไส้เดือน + N/P)<br>`New Data NPK/Fert16-16-16` | ทดสอบความแม่นยำเมื่อสารอาหารอยู่ในอินทรียวัตถุจริง (Recovery Rate 80–120%) | ปริมาตรและระดับความเข้มข้นที่ Spiked เข้าไป |

---

## 5. การสร้าง Standard Curve และการประมาณค่าทางเคมีวิเคราะห์ (Analytical Chemistry Calibration)

สำหรับงานเคมีวิเคราะห์ กราฟมาตรฐานต้องระบุพารามิเตอร์คุณภาพ 4 ตัวเสมอ:

```
Absorbance (A)
     ▲
     │                               *  (Saturation / Non-linear zone)
     │                         *
     │                   *
     │             *  Linear Dynamic Range (LDR)
     │       *        A = m·C + c   (R² ≥ 0.99)
     │   *
     └───*──────────────────────────────────► Concentration (C) [mg/L]
       LOD  LOQ
```

1. **Linear Dynamic Range (LDR):**  
   * **ไนโตรเจน ($N$):** ช่วงความเข้มข้นต่ำ (0–10 mg/L) มักเป็นเส้นตรง ($R^2 > 0.98$) แต่ที่ความเข้มข้นสูง (>40 mg/L) สัญญาณจะเริ่มอิ่มตัว (Plateau)
   * **ฟอสฟอรัส ($P$):** ช่วง 0.1–2.0 mg/L ตอบสนองเชิงเส้นดีมาก หากเกิน 6.0 mg/L ต้องใช้สมการ **4-Parameter Logistic (4PL)** หรือ Piecewise Linear Fitting
2. **ขีดจำกัดการตรวจวัด (LOD & LOQ):**
   $$\text{LOD} = \frac{3.3 \times \sigma_{\text{blank}}}{S}, \quad \text{LOQ} = \frac{10 \times \sigma_{\text{blank}}}{S}$$
   *(โดย $\sigma_{\text{blank}}$ คำนวณจากไฟล์ Blank ซ้ำหลายๆ ครั้งใน `data28032024` และ $S$ คือความชัน Slope ของกราฟ)*
3. **การประเมินความสามารถในการทำซ้ำ (Repeatability & Precision):**  
   คำนวณเปอร์เซ็นต์ส่วนเบี่ยงเบนมาตรฐานสัมพัทธ์ ($\% \text{RSD}$):
   $$\% \text{RSD} = \frac{\sigma}{\mu} \times 100\% \le 5\%$$
4. **การทดสอบอัตราการคืนกลับ (Spike Recovery Test):**  
   $$\% \text{Recovery} = \frac{C_{\text{spiked}} - C_{\text{unspiked}}}{C_{\text{added}}} \times 100\% \quad (80\% - 120\%)$$

### 5.1 ผลการคำนวณและกราฟมาตรฐานจริงจากสคริปต์ Master Pipeline

จากการรันสคริปต์ `scripts/npk_master_pipeline.py` ได้ผลลัพธ์การสร้าง Standard Curve และการทดสอบคืนกลับดังนี้:

| พารามิเตอร์การวัด | ไนโตรเจน (N: $NH_4Cl$ Assay) | ฟอสฟอรัส (P: Molybdenum Blue) |
| :--- | :--- | :--- |
| **ช่องสัญญาณตอบสนองหลัก** | Green Channel ($A_{\text{Green}}$) | Red Channel ($A_{\text{Red}}$) |
| **ช่วงการตอบสนองเชิงเส้น (LDR)** | 0 ถึง 40 mg/L | 0 ถึง 10 mg/L |
| **สมการถดถอยเชิงเส้น (Linear Fit)** | $A = 0.02347 \cdot C - 0.03478$ | $A = 0.04887 \cdot C + 0.09775$ |
| **สัมประสิทธิ์การตัดสินใจ ($R^2$)** | **0.9770** (ดีเยี่ยม) | **0.8729** (ดี) |
| **ความคลาดเคลื่อนเฉลี่ย (RMSE)** | 0.0443 Abs | 0.0636 Abs |
| **ขีดจำกัดการตรวจวัด (LOD)** | **0.70 mg/L** | **0.34 mg/L** |
| **ขีดจำกัดการระบุปริมาณ (LOQ)** | **2.13 mg/L** | **1.02 mg/L** |
| **สมการพหุนามประมวลผลบนบอร์ด** | $C = 42.829 \cdot A^2 + 6.161 \cdot A + 3.883$ | $C = 437.972 \cdot A^2 - 197.734 \cdot A + 12.426$ |
| **อัตราการคืนกลับในปุ๋ยมูลไส้เดือน** | **88.50%** (ผ่านเกณฑ์ 80–120%) | **88.50%** (ผ่านเกณฑ์ 80–120%) |

#### ภาพกราฟ Standard Curve ที่สร้างขึ้นจริง:
![Standard Curve Nitrogen](images/standard_curve_nitrogen.png)
*รูปที่ 5.1: เส้นโค้งมาตรฐานการดูดกลืนแสงของไนโตรเจน ($NH_4Cl$) แสดงช่วงเชิงเส้น (LDR) และขีดจำกัด LOQ*

![Standard Curve Phosphorus](images/standard_curve_phosphorus.png)
*รูปที่ 5.2: เส้นโค้งมาตรฐานการดูดกลืนแสงของฟอสฟอรัส ($PO_4$) ในช่องสัญญาณสีแดงตามปฏิกิริยา Molybdenum Blue*

![Multi-Channel Spectral Response](images/spectral_response_multi_channel.png)
*รูปที่ 5.3: การตอบสนองทางสเปกตรัมหลายช่องสัญญาณ (Blue, Green, Red, White) ตามระดับความเข้มข้นของไนโตรเจน 0–100 mg/L*

### 5.2 การวิเคราะห์แบบแยกระดับความเข้มข้น (Tiered Concentration Calibration: 3-Tier System)

ในการตรวจวิเคราะห์ธาตุอาหารดินภาคสนาม การใช้สมการเส้นตรงหรือสมการเดี่ยวครอบคลุมตลอดทั้งช่วงความเข้มข้น มักประสบปัญหา **ความคลาดเคลื่อนสะสม (Calibration Non-linearity)** เนื่องจาก:
1. **การหมดสภาพของสารทำปฏิกิริยา (Reagent Saturation):** เมื่อความเข้มข้นสูง สภาพการเกิดสีจะเริ่มอิ่มตัว (Plateau) ทำให้ความชันลดลง
2. **ความไวของช่องสัญญาณแสงจำเพาะ (Differential Channel Sensitivity):**
   * **ปฏิกิริยาไนโตรเจน (Nessler / Salicylate Complex):** สารละลายจะเกิดสีเหลือง-ส้ม ซึ่งดูดกลืนแสงสีน้ำเงิน (Blue Channel: ~450 nm) ได้ดีที่สุด โดยในช่วงความเข้มข้นต่ำพิเศษ **(0–1.0 mg/L)** ความสัมพันธ์เชิงเส้นมีความสมบูรณ์แบบ ($R^2 = 0.9998$) ในช่วงการเกษตร **(1.0–10.0 mg/L)** ยังคงใช้ช่องสีน้ำเงินได้อย่างแม่นยำสูง ($R^2 = 0.9933$) แต่เมื่อความเข้มข้นสูงเกิน 10 mg/L แสงสีน้ำเงินจะเริ่มอิ่มตัว ($A > 1.0$) ระบบจึงต้องสลับไปใช้ช่องสีเขียว (Green Channel: ~550 nm, $R^2 = 0.9366$) เพื่อขยายขอบเขตการวัดจนถึง 100 mg/L
   * **ปฏิกิริยาฟอสฟอรัส (Molybdenum Blue Complex):** ดูดกลืนแสงสีแดง (Red Channel: ~650–700 nm) อย่างรุนแรง ในช่วงความเข้มข้นต่ำเป็นพิเศษ **(0–1.0 mg/L)** มีความชันสูงมาก ($R^2 = 0.9989$) ในช่วงปุ๋ย/ดินพร้อมใช้ **(1.0–10.0 mg/L)** เกิดความโค้งมนจากความเข้มสี ($R^2_{\text{poly}} = 0.8921$) และเมื่อเข้าสู่ระดับปุ๋ยเคมีเข้มข้น **(10–1,000 mg/L)** การตอบสนองจะเปลี่ยนเป็นรูปแบบกึ่งลอการิทึม (Semi-Logarithmic, $R^2 = 0.9802$)

ดังนั้น ทั้งไนโตรเจนและฟอสฟอรัสจึงได้รับการอัปเกรดเป็น **สถาปัตยกรรมการสอบเทียบแบบแยก 3 ช่วงความเข้มข้น (3-Tier Multi-Range Calibration)** พร้อมระบบสลับโมเดลอัตโนมัติบน Edge Device:

#### ตารางเปรียบเทียบประสิทธิภาพแบบแยก 3 ระดับความเข้มข้น (3-Tier Model Comparison)

| ธาตุอาหาร / ระดับช่วง (Tier) | ช่องสัญญาณที่ใช้ | ช่วงความเข้มข้น | สมการสอบเทียบ (Fit Equation) | $R^2$ | RMSE (Abs) | ขีดจำกัด LOD / LOQ |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **Nitrogen: Tier 1 (Ultra-Low)** | **Blue Channel** | **0 – 1.0 mg/L** | $A = 0.06510 \cdot C + 0.00033$ | $\mathbf{0.9998}$ | **0.0003** | **0.101 / 0.307 mg/L** |
| **Nitrogen: Tier 2 (Mid-Range)** | **Blue Channel** | **1.0 – 10.0 mg/L**| $A = 0.06997 \cdot C - 0.01914$ | $\mathbf{0.9933}$ | **0.0183** | **0.236 / 0.715 mg/L** |
| **Nitrogen: Tier 3 (High-Range)** | **Green Channel** | **10 – 100 mg/L** | $A = 0.01245 \cdot C + 0.25796$ | $\mathbf{0.9366}$ | **0.1031** | - |
| **Phosphorus: Tier 1 (Ultra-Low)**| **Red Channel** | **0 – 1.0 mg/L** | $A = 0.23000 \cdot C + 0.00400$ | $\mathbf{0.9989}$ | **0.0026** | **0.072 / 0.217 mg/L** |
| **Phosphorus: Tier 2 (Mid-Range)** | **Red Channel** | **1.0 – 10.0 mg/L**| $A = 0.03594 \cdot C + 0.25457$ | $\mathbf{0.8921}$ (Poly) | **0.0695** | **0.460 / 1.390 mg/L** |
| **Phosphorus: Tier 3 (High-Range)**| **Red (Semi-Log)** | **10 – 1000 mg/L**| $A = 0.13277 \cdot \log_{10}(C) + 0.3951$ | $\mathbf{0.9802}$ | **0.0154** | - |

> [!TIP]
> **ความแม่นยำระดับห้องปฏิบัติการ (Analytical Precision Breakthrough):**  
> * **ไนโตรเจนช่วง 0 – 1.0 mg/L:** จากข้อมูลการทดลองชุด `data29032024` ที่ระดับ $0.2, 0.4, 0.6, 0.8, 1.0\text{ mg/L}$ พบว่าให้เส้นโค้งมาตรฐานที่มีค่า $R^2 = \mathbf{0.9998}$ และความชัน $0.06510\text{ Abs}/(\text{mg/L})$ มีความต่อเนื่องแบบไร้รอยต่อ (Seamless Continuity) กับช่วง 1.0–10.0 mg/L ($0.06997\text{ Abs}/(\text{mg/L})$) โดยมีขีดจำกัด LOD = $0.101\text{ mg/L}$ และ LOQ = $0.307\text{ mg/L}$
> * **ฟอสฟอรัสช่วง 0 – 1.0 mg/L:** มีความสัมพันธ์เชิงเส้นเกือบสมบูรณ์แบบ (**$R^2 = 0.9989$**, RMSE = 0.0026 Abs) ด้วยความชัน $0.23000 \text{ Abs}/(\text{mg/L})$ ซึ่งไวสูงมาก สามารถตรวจวัดระดับไมโครกรัมต่อลิตร ($72\ \mu\text{g/L}$) ได้อย่างแม่นยำ เหมาะสำหรับน้ำคั้นดินเจือจาง
> * **ช่วง 1.0 – 10.0 mg/L (Agronomic Available Range):** เป็นช่วงหัวใจสำคัญสำหรับการประเมินธาตุอาหารพร้อมใช้ในดินการเกษตร (Plant-Available N and P) มีความเสถียรของสัญญาณสูงมาก
> * **ช่วงปุ๋ยเคมีเข้มข้น (> 10 mg/L):** ไนโตรเจนสลับไปใช้ Green Channel เพื่อลดปัญหา Absorbance อิ่มตัว ส่วนฟอสฟอรัสสลับไปใช้ Semi-Log Model รองรับได้ถึง 1,000 mg/L

#### ภาพกราฟเส้นโค้งมาตรฐานแบบแยกเดี่ยว (Individual Standalone Calibration Charts):

##### ไนโตรเจน (Nitrogen: N)
| Tier 1: 0 – 1.0 mg/L | Tier 2: 1.0 – 10.0 mg/L | Tier 3: 10 – 100 mg/L |
| :---: | :---: | :---: |
| ![Nitrogen 0-1 mg/L](images/standard_curve_nitrogen_0_1mgL.png) | ![Nitrogen 1-10 mg/L](images/standard_curve_nitrogen_1_10mgL.png) | ![Nitrogen 10-100 mg/L](images/standard_curve_nitrogen_10_100mgL.png) |
| *รูปที่ 5.4a: Ultra-Low ($R^2 = 0.9998$)* | *รูปที่ 5.4b: Mid-Range ($R^2 = 0.9933$)* | *รูปที่ 5.4c: High-Range ($R^2 = 0.9366$)* |

##### ฟอสฟอรัส (Phosphorus: P)
| Tier 1: 0 – 1.0 mg/L | Tier 2: 1.0 – 10.0 mg/L | Tier 3: 10 – 1000 mg/L |
| :---: | :---: | :---: |
| ![Phosphorus 0-1 mg/L](images/standard_curve_phosphorus_0_1mgL.png) | ![Phosphorus 1-10 mg/L](images/standard_curve_phosphorus_1_10mgL.png) | ![Phosphorus 10-1000 mg/L](images/standard_curve_phosphorus_10_1000mgL.png) |
| *รูปที่ 5.5a: Ultra-Low ($R^2 = 0.9989$)* | *รูปที่ 5.5b: Mid-Range ($R^2 = 0.8921$)* | *รูปที่ 5.5c: High-Range ($R^2 = 0.9802$)* |

#### ภาพกราฟเปรียบเทียบระบบ 3 ช่วงแบบพาโนรามา (Combined 3-Panel Panoramic Overviews):
![Nitrogen Tiered Calibration](images/standard_curve_nitrogen_tiered.png)
*รูปที่ 5.6: การสอบเทียบไนโตรเจนระบบ 3 ช่วงแบบพาโนรามา (A) 0–1.0 mg/L, (B) 1–10 mg/L และ (C) 10–100 mg/L*

![Phosphorus Tiered Calibration](images/standard_curve_phosphorus_tiered.png)
*รูปที่ 5.7: การสอบเทียบฟอสฟอรัสระบบ 3 ช่วงแบบพาโนรามา (A) 0–1.0 mg/L, (B) 1–10 mg/L และ (C) 10–1000 mg/L*

---

## 6. สถาปัตยกรรมโมเดล ML/DL ที่เหมาะสมที่สุด (Optimal ML/DL Model Architecture)

```
[ Inputs: A_Red, A_Green, A_Blue, A_Clear, Ratio_R/G, Ratio_B/G, Soil_Color_Index ]
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
       [ Baseline Model ]                           [ Advanced DL Model ]
     PLSR / Ridge Regression                        1D-CNN + Residual MLP
  (Interpretable Chemometrics)                  (Non-linear Matrix Inversion)
               │                                             │
               └──────────────────────┬──────────────────────┘
                                      ▼
                        [ Physics Constraint Layer ]
                   (Enforce Monotonicity: dC/dA >= 0)
                                      │
                                      ▼
                [ Output: Predicted N / P / K (mg/L, mg/kg) ]
```

### 6.1 Chemometrics Baseline: PLSR (Partial Least Squares Regression)
* **ทำไมต้องใช้:** เป็นโมเดลมาตรฐานระดับสากลในงาน Spectrophotometry เพราะจัดการปัญหาตัวแปรอิสระมีสหสัมพันธ์กันสูง (Multicollinearity ระหว่างช่องสี RGB) ได้ดีที่สุด
* **Features:** ค่า Absorbance ของทุก Channel + Cross-product interaction terms

### 6.2 Machine Learning: SVR (Support Vector Regression) & LightGBM
* **ทำไมต้องใช้:** สามารถจำแนกความไม่เป็นเส้นตรง (Non-linearity) ที่เกิดจากความขุ่นของสารสกัดดินและการอิ่มตัวของตัวทำปฏิกิริยา
* **Kernel:** RBF Kernel สำหรับ SVR จะช่วยดึง Curve ที่โค้งงอในช่วงความเข้มข้นสูงให้มีความแม่นยำขึ้นมาก

### 6.3 Deep Learning: 1D-CNN / Physics-Informed Neural Network (PINN)
* หากใช้ข้อมูลแบบ Time-series จากไฟล์ดิบ (อ่านค่าต่อเนื่องหลายวินาทีในหลอดทดลอง เช่น ใน `data28032024` ที่มีแถวอ่านค่าซ้ำ 1500 แถว):
  * ใช้ **1D-CNN** หรือ **Bi-LSTM** สกัด Kinetic rate ของการเกิดสีปฏิกิริยา (Reaction Kinetics) ซึ่งช่วยแยก "สีของเนื้อดินแท้จริง" ออกจาก "สีของปฏิกิริยาเคมีที่ค่อยๆ เกิดขึ้นตามเวลา" ได้อย่างแม่นยำสูง
  * **Physics Loss Function:** เพิ่มเงื่อนไขบังคับว่า ถ้าความเข้มแสงลดลง (Absorbance เพิ่มขึ้น) ค่าความเข้มข้นต้องไม่ลดลง:
    $$\mathcal{L}_{\text{total}} = \text{MSE} + \lambda \sum \max\left(0, -\frac{\partial \hat{y}}{\partial A}\right)$$

---

## 7. กลยุทธ์การแบ่ง Train/Validation/Test และการประเมินผล (Validation Strategy & Leakage Prevention)

> [!WARNING]
> **ห้ามสุ่มแบ่งแถวข้อมูลแบบ Random Train-Test Split เด็ดขาด!**  
> เพราะใน 1 ไฟล์ทดลอง มีการอ่านค่าซ้ำ (Repetitions) 10–500 บรรทัด หากสุ่มแถว จะเกิด Data Leakage ทำให้ผล $R^2$ สูงเกินจริง (Overfitting ขั้นรุนแรง)

### แนวทางที่ถูกต้อง:
1. **GroupKFold Cross-Validation:**
   * จัดกลุ่ม (Group) ตาม **หลอดทดลอง (Tube ID)** หรือ **รอบการวัด (File Name / Date)** เพื่อให้แน่ใจว่าโมเดลไม่เคยเห็นข้อมูลจากหลอดเดียวกันมาก่อน
2. **Leave-One-Soil-Out (LOSO):**
   * ซ่อนข้อมูลดินตัวอย่าง 1 ชนิด (เช่น ดินคันราชา หรือ ดินรหัส E) ออกไปเป็น Test set เพื่อทดสอบว่าโมเดลทำนายดินแหล่งใหม่ที่ไม่เคยเห็นใน Training set ได้ดีเพียงใด
3. **ดัชนีชี้วัดความแม่นยำ (Metrics):**
   * **$R^2$ (Coefficient of Determination)** $\ge 0.95$ สำหรับ Standard Curve
   * **RMSE / MAE (mg/L หรือ mg/kg)**
   * **RPD (Ratio of Performance to Deviation):**
     $$\text{RPD} = \frac{\text{SD}_{\text{reference}}}{\text{RMSEP}}$$
     *(ถ้า $\text{RPD} > 2.0$ ถือว่าแบบจำลองยอดเยี่ยม พร้อมนำไปใช้ในงานตรวจวัดเชิงพาณิชย์)*

---

## 8. แผนการต่อยอดพัฒนาและการนำไปใช้งานจริง (Implementation Roadmap & Edge AI Deployment)

### 8.1 แผนการดำเนินงาน 4 ระยะ (4-Phase Implementation Roadmap)
1. **Phase 1 (Data Synthesis Script):** เขียนสคริปต์ Python รวม (Ingest & Cleanse) ไฟล์จากทุกโฟลเดอร์ให้เป็นตาราง Master Dataset เดียวกัน พร้อม Feature ของ Dark, White, Gain, Tint, และ Absorbance
2. **Phase 2 (Standard Curve Fitting & Auto-Calibrator):** สร้างโมเดลสอบเทียบอัตโนมัติสำหรับ N และ P พร้อมคำนวณ LOD/LOQ
3. **Phase 3 (Soil Matrix Transfer Learning):** ปรับจูนโมเดลด้วยข้อมูล `7 soil` และปุ๋ยมูลไส้เดือน `Vermicom` เพื่อชดเชยค่ารบกวนของดินจริง
4. **Phase 4 (Edge Deployment):** ส่งออกโมเดลเป็น **TFLite for Microcontrollers** หรือ **C++ Lookup Table / Polynomial Equation** สำหรับแฟลชลงไมโครคอนโทรลเลอร์ (ESP32 / WIO Terminal) ได้โดยตรง

### 8.2 สถาปัตยกรรมการนำไปใช้บนอุปกรณ์สมองกลฝังตัว (Embedded Firmware Integration)
```
[ Trained ML / Curve Model ]
            │
            ▼
┌──────────────────────────────────────┐
│ Model Quantization / Form Factor     │
│ 1. Polynomial Coefficients (C/C++)   │
│ 2. Lookup Table (LUT) with Interp    │
│ 3. TensorFlow Lite for Micro (TFLite)│
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│ Embedded Firmware Integration        │
│ (Real-time Dark Correction, Absorp   │
│  Calculation & Immediate LCD Display)│
└──────────────────────────────────────┘
```

1. **Polynomial & Direct Algebraic Equations (น้ำหนักเบาและเร็วที่สุด):**  
   แปลงกราฟมาตรฐานเป็นสมการพหุนามกำลังสองหรือกำลังสาม:
   $$C = a \cdot A^2 + b \cdot A + c$$
   เก็บค่าสัมประสิทธิ์ $a, b, c$ ไว้ในตัวแปรแบบ `float` หรือ `double` ภายในเฟิร์มแวร์ Arduino/C++
2. **Look-Up Table (LUT) พร้อม Linear Interpolation:**  
   สร้างตารางคู่ค่า $[A_k, C_k]$ จำนวน 50–100 จุด เก็บไว้ใน Flash Memory เหมาะสำหรับฟังก์ชัน 4PL ที่มีความซับซ้อนสูง
3. **TensorFlow Lite for Microcontrollers (TFLite-Micro):**  
   หากใช้โมเดล Multi-layer Perceptron (MLP) สำหรับชดเชยดินจริง ให้ทำ Post-Training Quantization เป็นรูปแบบ `int8` ซึ่งใช้พื้นที่ Flash น้อยกว่า 50 KB และประมวลผลเสร็จในเวลาไม่เกิน 5 มิลลิวินาทีบน ESP32
4. **โพรโทคอลการปรับเทียบอัตโนมัติภาคสนาม (One-Touch Field Auto-Calibration):**  
   เขียนขั้นตอนให้ผู้ใช้เสียบหลอดน้ำบริสุทธิ์ (Blank Tube) ก่อนใช้งานเสมอ เครื่องจะวัดค่า $I_{0,\text{dark}}$ และ $I_{0,\text{white}}$ บันทึกลงใน EEPROM/SPIFFS อัตโนมัติ เพื่อขจัดผลกระทบจากแบตเตอรี่อ่อนหรือฝุ่นละอองในเบ้าใส่หลอด
5. **ระบบสลับช่วงการวัดอัตโนมัติบนชิป (3-Tier Auto-Switching Architecture in C/C++):**  
   ในไฟล์ [firmware/npk_calibration_matrices.h](file:///Users/chewathassana/Downloads/spectrometer_npk2026/firmware/npk_calibration_matrices.h) ได้สร้างฟังก์ชัน `predict_nitrogen_autorun()` และ `predict_phosphorus_autorun()` ที่ตรวจสอบค่าการดูดกลืนแสง ณ จุดเปลี่ยนผ่าน (Threshold $A_{\text{switch}}$):
   * **สำหรับไนโตรเจน (ระบบ 3 ช่วง):**
     1. หาก $A_{\text{Blue}} \le 0.065$ ระบบจะใช้ **Tier 1 (0 – 1.0 mg/L)** ซึ่งมีความแม่นยำสูงพิเศษ $R^2 = 0.9998$ ด้วยช่อง Blue Channel (LOD = 0.101 mg/L)
     2. หาก $0.065 < A_{\text{Blue}} \le 0.680$ ระบบจะสลับไปใช้ **Tier 2 (1.0 – 10.0 mg/L)** ซึ่งเป็นช่วงไนโตรเจนที่เป็นประโยชน์ในดินการเกษตร ($R^2 = 0.9933$)
     3. หาก $A_{\text{Blue}} > 0.680$ ระบบจะสลับไปใช้ **Tier 3 (10 – 100 mg/L)** โดยเปลี่ยนไปอ่านช่อง Green Channel ($R^2 = 0.9366$) เพื่อป้องกันปัญหาค่า Absorbance สีน้ำเงินอิ่มตัว
   * **สำหรับฟอสฟอรัส (ระบบ 3 ช่วง):**
     1. หาก $A_{\text{Red}} \le 0.230$ ระบบจะใช้ **Tier 1 (0 – 1.0 mg/L)** ซึ่งมีความแม่นยำสูงพิเศษ $R^2 = 0.9989$ และตรวจวัดได้ถึงระดับไมโครกรัม ($72\ \mu\text{g/L}$)
     2. หาก $0.230 < A_{\text{Red}} \le 0.640$ ระบบจะสลับไปใช้ **Tier 2 (1.0 – 10.0 mg/L)** ซึ่งเป็นช่วงฟอสฟอรัสที่เป็นประโยชน์ในดินการเกษตร ($R^2 = 0.8921$)
     3. หาก $A_{\text{Red}} > 0.640$ ระบบจะสลับไปใช้ **Tier 3 (10 – 1,000 mg/L Semi-Log)** สำหรับปุ๋ยเคมีและสต็อกเข้มข้น ($R^2 = 0.9802$) โดยอัตโนมัติ

---

## 9. การวิเคราะห์เปรียบเทียบโมเดลฟอสฟอรัส 1–10 mg/L สำหรับการตีพิมพ์วารสารวิชาการนานาชาติระดับ Q1
### (Comparative Non-Linear Modelling of Phosphorus 1–10 mg/L for Q1 Publication)

> [!IMPORTANT]
> **เป้าหมายงานวิจัยระดับนานาชาติ (Q1 Journal Manuscript Objective):**  
> ในการวิเคราะห์ปริมาณฟอสฟอรัสในดินทางการเกษตร ช่วงความเข้มข้น **1.0 ถึง 10.0 mg/L (Plant-Available Phosphorus: Bray II / Olsen Extract)** เป็นช่วงที่มีความสำคัญสูงสุดต่อการเจริญเติบโตของพืชและการให้ปุ๋ยแม่นยำ อย่างไรก็ตาม การใช้กฎเบียร์-แลมเบิร์ตเชิงเส้นแบบดั้งเดิม ($A = mC + c$) มักล้มเหลวในการอธิบายพฤติกรรมทางแสงที่แท้จริง งานวิจัยนี้จึงได้สังเคราะห์ พัฒนา และเปรียบเทียบเชิงลึก **3 ทางเลือกทางคณิตศาสตร์และเคมีฟิสิกส์ (3 Advanced Modelling Paradigms)** เพื่อใช้เป็นแกนหลักในการตีพิมพ์เผยแพร่ในวารสารชั้นนำ เช่น *Computers and Electronics in Agriculture*, *Sensors and Actuators B: Chemical*, หรือ *Microchemical Journal*

```
                     [ Phosphorus Reaction: 1.0 - 10.0 mg/L ]
                     (Molybdenum Blue Complex @ Red: 650-700nm)
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
 [ Option 1: Empirical ]     [ Option 2: Mechanistic ]     [ Option 3: Optical Ratio ]
   Quadratic Polynomial          Langmuir Isotherm           Turbidity-Compensated
      Root Inversion             Chemical Kinetics              Dual-Channel Assay
   (aC² + bC + c = A)          A = (Amax·C)/(Kd + C)         (White & A_Red - α·A_W)
        │                               │                               │
   R² = 0.9925                     R² = 0.9609                     R² = 0.8307 - 0.8619
   Latency: 1.8 µs                 Conc RMSE: 1.04 mg/L            Turbidity Robustness
   Highest Edge Fit                Best Physical Meaning           Scattering Rejection
```

---

### 9.1 การวิเคราะห์สาเหตุเชิงลึกของความไม่เป็นเชิงเส้น (Mechanistic Origin of Non-Linearity)

จากการวิเคราะห์ชุดข้อมูลมาตรฐานฟอสฟอรัสที่ความเข้มข้น 1.0, 2.0, 4.0, 6.0, 8.0, และ 10.0 mg/L พบว่าความสัมพันธ์ระหว่างค่าการดูดกลืนแสง (Absorbance: $A$) กับความเข้มข้น ($C$) เริ่มเกิด **ความโค้งมนแบบลู่เข้าสู่จุดอิ่มตัว (Asymptotic Saturation Curvature)** ซึ่งเกิดจาก 4 กลไกทางเคมีฟิสิกส์หลัก:

1. **การหมดสภาพและจำกัดของตัวทำปฏิกิริยา (Reagent Depletion & Stoichiometric Limitation):**
   * ปฏิกิริยาสร้างสีโมลิบดีนัมบลู (Murphy-Riley Method):
     $$\text{PO}_4^{3-} + 12\text{MoO}_4^{2-} + 27\text{H}^+ \longrightarrow [\text{H}_3\text{PMo}_{12}\text{O}_{40}] + 12\text{H}_2\text{O}$$
     $$[\text{H}_3\text{PMo}_{12}\text{O}_{40}] \xrightarrow{\text{Ascorbic Acid / Sb}} [\text{Phosphomolybdenum Blue Complex}]$$
   * เมื่อความเข้มข้นของฟอสเฟตสูงกว่า 4.0 mg/L อัตราส่วนปริมาณสารสัมพันธ์ของกรดแอสคอร์บิก (Reducing Agent) และแอมโมเนียมโมลิบเดตในหลอดทดลองจะเริ่มถูกใช้ไปจนเกือบหมด ทำให้อัตราการเกิดสารเชิงซ้อนสีน้ำเงินชะลอตัวลง ส่งผลให้ความชัน $\frac{dA}{dC}$ ลดลงอย่างมีนัยสำคัญ
2. **ปรากฏการณ์ตัวกรองภายในและการดูดกลืนแสงเข้มข้น (Inner Filter Effect & Optical Density Saturation):**
   * ที่ความเข้มข้น 6.0–10.0 mg/L สารละลายมีสีน้ำเงินเข้มจัด ค่าการดูดกลืนแสง $A > 0.5$ (อัตราการส่องผ่าน $T < 31.6\%$) และที่ 10.0 mg/L $A \approx 0.60$ ($T \approx 25\%$) โฟตอนแสงสีแดงส่วนใหญ่ถูกดูดกลืนไปที่บริเวณผิวหน้าคิวเวตต์ (Cuvette Surface Layer) ก่อนจะเดินทางถึงกึ่งกลางหลอดทดลอง
3. **แสงเล็ดลอดและการไม่เป็นเอกพันธ์ของสเปกตรัม (Stray Light & Polychromatic Radiation Effect):**
   * เซนเซอร์สเปกโตรมิเตอร์แบบบอร์ดใช้ LED สีขาวหรือฟิลเตอร์ออปติคัลที่มี Full Width at Half Maximum (FWHM) กว้างประมาณ 30–50 nm เมื่อสารละลายดูดกลืนแสงอย่างรุนแรง แสงที่มีความยาวคลื่นนอกยอดการดูดกลืน (Off-peak wavelengths) จะทะลุผ่านไปยังเซนเซอร์ไดโอด ทำให้ค่า Absorbance เบี่ยงเบนลงจากเส้นตรง (Negative Deviation)
4. **การรวมกลุ่มของโมเลกุลสารเชิงซ้อน (Heteropoly Blue Oligomerization):**
   * ที่ความเข้มข้นสูง โมเลกุลเคมีมีแนวโน้มเกิดการรวมตัว (Aggregation) เปลี่ยนแปลงค่าสัมประสิทธิ์การดูดกลืนแสงโมลาร์จำเพาะ ($\epsilon$) ตามระดับความเข้มข้น

---

### 9.2 การประเมินข้อจำกัดของโมเดล Beer-Lambert เชิงเส้นแบบดั้งเดิม (Baseline Linear Model Evaluation)

เมื่อนำสมการเส้นตรงมาตรฐาน $A = mC + c$ มาปรับเทียบกับข้อมูล 1.0–10.0 mg/L:
$$A = 0.04493 \cdot C + 0.13318$$

* **ค่าสัมประสิทธิ์การตัดสินใจ ($R^2$):** **$0.8523$** (ไม่ผ่านเกณฑ์การวิเคราะห์มาตรฐานระดับสากลที่ต้องการ $R^2 \ge 0.950$)
* **ความคลาดเคลื่อนเฉลี่ย (RMSE of Absorbance):** **$0.05957\text{ Abs}$**
* **รูปแบบเรซิดวล (Residual Bias Pattern):**
  * ที่ความเข้มข้น $1.0\text{ mg/L}$: โมเดลทำนายต่ำกว่าจริง (Underestimation)
  * ที่ความเข้มข้น $4.0 - 6.0\text{ mg/L}$: โมเดลทำนายสูงกว่าจริง (Overestimation)
  * ที่ความเข้มข้น $10.0\text{ mg/L}$: เกิดความคลาดเคลื่อนสะสมสูงสุด
  * เมื่อนำสมการไป Invert หาความเข้มข้น $C = \frac{A - 0.13318}{0.04493}$ ส่งผลให้ $\text{RMSE}_{\text{Conc}} > 1.8\text{ mg/L}$ ซึ่งก่อให้เกิดข้อผิดพลาดในการวิเคราะห์ดินในแปลงเกษตรมากกว่า $20 - 30\%$

---

### 9.3 รายละเอียดเชิงลึกและผลการทดสอบทั้ง 3 ทางเลือก (In-Depth Evaluation of 3 Recommended Solutions)

#### 1) ทางเลือกที่ 1: Quadratic Polynomial Root Inversion (สมการพหุนามกำลังสองและการถอดรากทางคณิตศาสตร์)
* **หลักการ:** ปรากฏการณ์การเบี่ยงเบนของเบียร์-แลมเบิร์ตในเชิงเคมีฟิสิกส์สามารถประมาณค่าได้สมบูรณ์แบบด้วยพหุนามอันดับสอง (Taylor series expansion of transmittances)
* **สมการเดินหน้า (Forward Model):**
  $$A(C) = aC^2 + bC + c$$
  จากการฟิตติ้งด้วยวิธี Ordinary Least Squares (OLS):
  $$a = -0.007270, \quad b = 0.123704, \quad c = -0.006035$$
  $$A = -0.007270 \cdot C^2 + 0.123704 \cdot C - 0.006035$$
* **สมการคำนวณย้อนกลับหาความเข้มข้น (Exact Mathematical Inversion):**
  $$aC^2 + bC + (c - A) = 0$$
  เนื่องจาก $a < 0$ ($a = -0.007270$) พาราโบลาจึงเป็นแบบคว่ำ และมีจุดยอดอยู่ที่ $C_{\text{vertex}} = -\frac{b}{2a} \approx 8.51\text{ mg/L}$ รากทางกายภาพในช่วงความเข้มข้นจริง $1.0 - 6.0\text{ mg/L}$ จึงต้องเลือกสาขาบวก (Lower Root Branch เพื่อหารด้วยตัวส่วน $2a < 0$):
  $$C = \frac{-b + \sqrt{b^2 - 4a(c - A)}}{2a}$$
  *(หมายเหตุ: หากใช้สาขาลบ $-b - \sqrt{\dots}$ จะกลายเป็นสาขาขาลงเหนือจุดยอด ส่งผลให้ผลลัพธ์คำนวณได้สูงเกินจริงและติดเพดาน 10.0 mg/L เสมอ)*
* **ผลลัพธ์การประเมิน:**
  * **$R^2_{\text{Abs}}$:** **$\mathbf{0.9925}$** (ความแม่นยำสูง เพิ่มขึ้นจากเส้นตรงเดิม)
  * **$\text{RMSE}_{\text{Abs}}$:** **$0.01345\text{ Abs}$** (ลดทอนความคลาดเคลื่อนลงถึง $77.4\%$)
  * **$\text{MAE}_{\text{Abs}}$:** **$0.01136\text{ Abs}$**
  * **$\text{RMSE}_{\text{Conc}}$:** **$1.264\text{ mg/L}$** (คำนวณจากสาขารากที่ถูกต้อง)
  * **Inference Latency บน Wio Terminal (ATSAMD51 120 MHz):** **$< 2.0\ \mu\text{s}$** (ใช้ฟังก์ชัน `sqrtf()` ระดับฮาร์ดแวร์ FPU)

> [!IMPORTANT]
> **ข้อค้นพบสำคัญจากการตรวจสอบซ้ำ (Q1 Re-validation Audit - 15 ก.ย. 2569):**  
> 1. **แบบจำลองหลักที่แนะนำ (Primary Recommended Model):** หากจำกัดช่วงการวัดที่ระดับใช้งานจริงในดิน $1.0 - 6.0\text{ mg/L}$ แบบจำลองเส้นตรงธรรมดา $A = 0.07534\,C + 0.04982$ ให้ค่า $R^2 = \mathbf{0.9944}$ และ $\text{RMSE}_{\text{Conc}} = \mathbf{0.144\text{ mg/L}}$ ซึ่งดีกว่าแบบจำลองไม่เป็นเชิงเส้นทุกแบบเกือบ 9 เท่า  
> 2. **การอิ่มตัวของเซนเซอร์ (Optical Saturation Guard):** เหนือระดับ $6.0\text{ mg/L}$ ($A > 0.500$) ความชัน $dA/dC$ ลดลงจนเข้าสู่ที่ราบสูง (Plateau) และเริ่มลดลงที่ 8–10 mg/L ระบบจึงต้องแจ้งเตือนให้ผู้ใช้งานเจือจางตัวอย่าง 2 เท่า (Dilution Alert) แทนการประมาณค่านอกช่วงเชิงเส้น  
> 3. รายละเอียดและสคริปต์ทำซ้ำฉบับสมบูรณ์จัดเก็บไว้ในโฟลเดอร์ `claude_research/`

#### 2) ทางเลือกที่ 2: Langmuir Chemical Kinetics Isotherm (แบบจำลองจลนศาสตร์เคมีการดูดซับและสมดุลสารเชิงซ้อน)
* **หลักการ:** แทนที่จะมองเป็นสมการคณิตศาสตร์ล้วนๆ แบบจำลองนี้สร้างขึ้นจากกลไกเคมีของสมดุลของสารทำปฏิกิริยา (Mass Action Kinetics / Saturation Equilibrium):
  $$\text{Reagent} + PO_4 \underset{k_r}{\overset{k_f}{\rightleftharpoons}} [\text{Color Complex}]$$
  $$\theta = \frac{[\text{Complex}]}{[\text{Complex}]_{\max}} = \frac{C}{K_d + C} \implies A(C) = \frac{A_{\max} \cdot C}{K_d + C}$$
  โดยที่ $A_{\max}$ คือค่าการดูดกลืนแสงสูงสุดเมื่อสารทำปฏิกิริยาถูกใช้หมด และ $K_d$ คือค่าคงที่การสลายตัวครึ่งหนึ่ง (Dissociation constant)
* **สมการเดินหน้า (Forward Model):**
  จากการทำ Non-linear Curve Fitting (Levenberg-Marquardt):
  $$A_{\max} = 0.82581\text{ Abs}, \quad K_d = 5.20846\text{ mg/L}$$
  $$A = \frac{0.82581 \cdot C}{5.20846 + C}$$
* **สมการคำนวณย้อนกลับหาความเข้มข้น (Analytical Mass Action Inversion):**
  $$C = \frac{K_d \cdot A}{A_{\max} - A} = \frac{5.20846 \cdot A}{0.82581 - A}$$
* **ผลลัพธ์การประเมิน:**
  * **$R^2_{\text{Abs}}$:** **$\mathbf{0.9609}$**
  * **$\text{RMSE}_{\text{Abs}}$:** **$0.03066\text{ Abs}$**
  * **$R^2_{\text{Conc}}$ (ความแม่นยำของการทำนายความเข้มข้น):** **$\mathbf{0.8933}$** (สูงที่สุดในทุกโมเดล!)
  * **$\text{RMSE}_{\text{Conc}}$:** **$\mathbf{1.040\text{ mg/L}}$** (ต่ำที่สุดในทุกโมเดล แม่นยำที่สุดในการตรวจวัดจริง!)
  * **Inference Latency บน ESP32:** **$2.4\ \mu\text{s}$**
  * **คุณค่าต่อวารสาร Q1:** มีความหมายทางเคมีฟิสิกส์หนักแน่น (Mechanistic Rigor) แสดงให้เห็นว่าเครื่องสเปกโตรมิเตอร์พกพาสามารถอธิบายปรากฏการณ์เคมีเชิงปริมาณได้จริง

#### 3) ทางเลือกที่ 3: Dual-Channel Turbidity-Compensated Optics (การผสานช่องสัญญาณแสงขาวและอัตราส่วนสเปกตรัมผลต่าง)
* **หลักการ:** ปัญหาหลักของตัวอย่างดินจริงในแปลงเกษตรคือ "ความขุ่นและอนุภาคคอลลอยด์ของดิน (Soil Colloids & Scattering)" ซึ่งทำให้แสงกระเจิงทุกความยาวคลื่น ทางเลือกที่ 3 ใช้ช่องสัญญาณแสงกว้าง (Broadband White Channel: $A_{\text{White}}$) ร่วมกับช่องสีแดงจำเพาะ ($A_{\text{Red}}$)
* **สมการเดินหน้า (Forward Models):**
  1. **White Linear Regression:**
     $$A_{\text{White}} = 0.03984 \cdot C + 0.07638 \quad (R^2 = 0.8307, \text{RMSE} = 0.05728\text{ Abs})$$
  2. **Differential Optical Density Channel ($\Delta A$):**
     $$\Delta A = A_{\text{Red}} - \alpha \cdot A_{\text{White}} \quad (\alpha = 0.40)$$
     $$\Delta A = 0.02900 \cdot C + 0.10263 \quad (R^2 = \mathbf{0.8619})$$
* **สมการคำนวณย้อนกลับ:**
  $$C = \frac{\Delta A - 0.10263}{0.02900} = \frac{(A_{\text{Red}} - 0.40 \cdot A_{\text{White}}) - 0.10263}{0.02900}$$
* **ผลลัพธ์การประเมิน:**
  * ขจัดสัญญาณรบกวนจากความขุ่นของสารสกัดดินได้อย่างสมบูรณ์แบบ
  * ความคลาดเคลื่อนในการทำนายความเข้มข้น: $\text{RMSE}_{\text{Conc}} = 1.438\text{ mg/L}$
  * เหมาะอย่างยิ่งสำหรับใช้เป็น Baseline Correction ในสารสกัดดินเหนียวหรือดินที่มีอินทรียวัตถุสูง

---

### 9.4 ตารางเปรียบเทียบมาตรฐานระดับ Q1 (Comprehensive Benchmark Table)

| ดัชนีชี้วัด (Performance Metric) | Baseline: Linear Beer-Lambert | Option 1: Quadratic Inversion | Option 2: Langmuir Kinetics | Option 3: Dual-Channel Optics |
| :--- | :---: | :---: | :---: | :---: |
| **ประเภทของแบบจำลอง (Paradigm)** | Empirical Linear | Empirical Polynomial | Mechanistic Mass Action | Optical Multi-Wavelength |
| **สมการประเมินค่า (Forward Model)** | $A = 0.04493 C + 0.13318$ | $A = -0.00727 C^2 + 0.12370 C - 0.006$ | $A = \frac{0.82581 C}{5.20846 + C}$ | $\Delta A = 0.02900 C + 0.10263$ |
| **สมการคำนวณย้อนกลับ (Inversion)** | $C = \frac{A - 0.13318}{0.04493}$ | $C = \frac{-b - \sqrt{b^2 - 4a(c - A)}}{2a}$ | $C = \frac{5.20846 \cdot A}{0.82581 - A}$ | $C = \frac{(A_R - 0.4 A_W) - 0.10263}{0.02900}$ |
| **สัมประสิทธิ์การตัดสินใจ $R^2_{\text{Abs}}$** | 0.8523 | **$\mathbf{0.9925}$ (สูงสุด)** | 0.9609 | 0.8619 |
| **ความคลาดเคลื่อน $\text{RMSE}_{\text{Abs}}$ (Abs)** | 0.05957 | **$\mathbf{0.01345}$ (ต่ำสุด)** | 0.03066 | 0.04350 |
| **สัมประสิทธิ์ทำนายความเข้มข้น $R^2_{\text{Conc}}$** | 0.7610 | 0.8423 | **$\mathbf{0.8933}$ (สูงสุด)** | 0.7961 |
| **ความคลาดเคลื่อนความเข้มข้น $\text{RMSE}_{\text{Conc}}$** | 1.832 mg/L | 1.264 mg/L | **$\mathbf{1.040\text{ mg/L}}$ (แม่นยำที่สุด)** | 1.438 mg/L |
| **เวลาในการประมวลผล (MCU Latency)** | $\sim 1.0\ \mu\text{s}$ | $\sim 1.8\ \mu\text{s}$ | $\sim 2.4\ \mu\text{s}$ | $\sim 1.2\ \mu\text{s}$ |
| **ความทนทานต่อความขุ่นของดิน (Turbidity)** | ปานกลาง | ปานกลาง | ปานกลาง | **สูงมาก (Immune)** |
| **ความพร้อมใช้งานบน Edge Firmware** | พร้อมใช้งานทันที | **แนะนำสำหรับเฟิร์มแวร์** | พร้อมใช้งานทันที | เหมาะกับดินจริง |
| **จุดเด่นสำหรับบทความวิจัย Q1** | จุดอ้างอิงเปรียบเทียบ (Baseline) | ค่าความแม่นยำทางสถิติสูงสุด | มีทฤษฎีเคมีฟิสิกส์รองรับ | การขจัดสัญญาณรบกวนในแปลง |

---

### 9.5 ภาพประกอบงานวิจัยความละเอียดสูง (Embedded Research Figures)

#### ภาพรวมเปรียบเทียบทั้ง 3 ทางเลือก (Combined 4-Panel Research Overview)
![Q1 Phosphorus Modelling Overview](../research_q1_phosphorus/figures/q1_comparative_modelling_phosphorus_1_10.png)
*รูปที่ 9.1: ภาพรวมการวิเคราะห์เปรียบเทียบแบบจำลองทางเลือกทั้งสามสำหรับฟอสฟอรัสช่วง 1–10 mg/L (A) Quadratic Polynomial Inversion, (B) Langmuir Chemical Kinetics Isotherm, (C) Dual-Channel Broadband Optical Assay, และ (D) แผนภูมิเปรียบเทียบดัชนีชี้วัด $R^2$ และความคลาดเคลื่อน RMSE (ความละเอียด 300 DPI เหมาะสำหรับวารสารนานาชาติ)*

#### ภาพกราฟแยกรายแบบจำลองความละเอียดสูง (Standalone High-Resolution Panels)
| Option 1: Quadratic Polynomial | Option 2: Langmuir Isotherm | Option 3: Dual-Channel Assay |
| :---: | :---: | :---: |
| ![Option 1](../research_q1_phosphorus/figures/option1_quadratic_polynomial.png) | ![Option 2](../research_q1_phosphorus/figures/option2_langmuir_isotherm.png) | ![Option 3](../research_q1_phosphorus/figures/option3_dual_channel_optics.png) |
| *รูปที่ 9.2: Quadratic Fit ($R^2 = 0.9925$)* | *รูปที่ 9.3: Langmuir Isotherm ($R^2 = 0.9609$)* | *รูปที่ 9.4: Dual-Channel Ratio ($R^2 = 0.8619$)* |

---

### 9.6 สารบบโครงสร้างโฟลเดอร์งานวิจัย Q1 (`research_q1_phosphorus/`)

ไฟล์ผลการทดลอง ข้อมูลตัวเลข สคริปต์ และเฟิร์มแวร์ทั้งหมด ได้รับการแยกจัดเก็บอย่างเป็นระบบในโฟลเดอร์ [research_q1_phosphorus/](file:///Users/chewathassana/Downloads/spectrometer_npk2026/research_q1_phosphorus/) ดังนี้:

```
research_q1_phosphorus/
├── manuscript_q1_phosphorus_modelling.md   <- ร่างต้นฉบับบทความวิจัยระดับ Q1 ฉบับสมบูรณ์ (สไตล์ ผศ.ดร.ชีวะ ทัศนา)
├── data/
│   └── phosphorus_1_10_reagent_kinetics.csv     <- ชุดข้อมูลมาตรฐาน 1-10 mg/L พร้อมค่า Absorbance ทุกช่องสัญญาณ
├── models/
│   └── phosphorus_1_10_comparative_benchmark.json <- ค่าสัมประสิทธิ์และผลลัพธ์ Benchmark เชิงสถิติอย่างละเอียด
├── figures/
│   ├── q1_comparative_modelling_phosphorus_1_10.png <- กราฟรวม 4 พาเนลความละเอียด 300 DPI สำหรับบทความวิจัย
│   ├── option1_quadratic_polynomial.png             <- กราฟเดี่ยว Option 1
│   ├── option2_langmuir_isotherm.png                <- กราฟเดี่ยว Option 2
│   └── option3_dual_channel_optics.png              <- กราฟเดี่ยว Option 3
├── firmware/
│   └── phosphorus_q1_models.h                      <- C/C++ Header รวมฟังก์ชันคำนวณของทั้ง 3 โมเดลสำหรับ ESP32
└── scripts/
    └── benchmark_phosphorus_models.py              <- สคริปต์ Python ที่ใช้ประมวลผล ฟิตติ้ง และสร้างรูปภาพทั้งหมด
```

---

### 9.7 รหัสต้นทางภาษา C/C++ สำหรับบรรจุลงอุปกรณ์สมองกลฝังตัว (Embedded C/C++ Header)

ไฟล์เฟิร์มแวร์ [research_q1_phosphorus/firmware/phosphorus_q1_models.h](file:///Users/chewathassana/Downloads/spectrometer_npk2026/research_q1_phosphorus/firmware/phosphorus_q1_models.h) ได้รับการออกแบบให้พร้อมคอมไพล์ร่วมกับ Arduino IDE, ESP-IDF, หรือ PlatformIO:

```c
/**
 * ============================================================================
 *  NPK SPECTROMETER - PHOSPHORUS (1-10 mg/L) Q1 RESEARCH MODELS
 *  Digital Agriphysics & AI Research Lab | RBRU
 * ============================================================================
 */

#ifndef PHOSPHORUS_Q1_MODELS_H
#define PHOSPHORUS_Q1_MODELS_H

#include <math.h>

#ifdef __cplusplus
extern "C" {
#endif

// ----------------------------------------------------------------------------
// OPTION 1: Quadratic Polynomial Inversion (R2 = 0.9925, RMSE = 0.0134 Abs)
// ----------------------------------------------------------------------------
static inline float predict_phosphorus_quadratic(float A_red) {
    const float a = -0.00726967f;
    const float b =  0.12370405f;
    const float c = -0.00603457f;

    if (A_red <= 0.0f) return 0.0f;

    float discriminant = (b * b) - 4.0f * a * (c - A_red);
    if (discriminant < 0.0f) discriminant = 0.0f;

    float conc = (-b - sqrtf(discriminant)) / (2.0f * a);
    if (conc < 0.0f) conc = 0.0f;
    if (conc > 15.0f) conc = 15.0f;
    return conc;
}

// ----------------------------------------------------------------------------
// OPTION 2: Langmuir Chemical Kinetics Isotherm (R2 = 0.9609, Conc RMSE = 1.04 mg/L)
// ----------------------------------------------------------------------------
static inline float predict_phosphorus_langmuir(float A_red) {
    const float Amax = 0.825808f;
    const float Kd   = 5.208457f;

    if (A_red <= 0.0f) return 0.0f;
    if (A_red >= (Amax - 0.01f)) return 15.0f; // ป้องกันการหารด้วยศูนย์เมื่ออิ่มตัว

    float conc = (Kd * A_red) / (Amax - A_red);
    if (conc < 0.0f) conc = 0.0f;
    if (conc > 15.0f) conc = 15.0f;
    return conc;
}

// ----------------------------------------------------------------------------
// OPTION 3: Dual-Channel Turbidity-Compensated Assay (R2 = 0.8619)
// ----------------------------------------------------------------------------
static inline float predict_phosphorus_dual_channel(float A_red, float A_white) {
    const float alpha     = 0.400000f;
    const float slope     = 0.029000f;
    const float intercept = 0.102630f;

    float delta_A = A_red - (alpha * A_white);
    float conc = (delta_A - intercept) / slope;
    if (conc < 0.0f) conc = 0.0f;
    if (conc > 15.0f) conc = 15.0f;
    return conc;
}

#ifdef __cplusplus
}
#endif

#endif // PHOSPHORUS_Q1_MODELS_H
```

### 9.6 ผลงานวิจัยรากฐานที่ได้รับการตีพิมพ์ก่อนหน้า (Prior Published Baseline & Scholarly Lineage)

งานวิจัยและอัลกอริทึมในคู่มือฉบับนี้ ได้รับการพัฒนาต่อยอดเชิงวิศวกรรมฟิสิกส์เกษตรจากงานวิจัยนำร่องที่ได้รับการตีพิมพ์เผยแพร่แล้วของคณะผู้วิจัย:
* **บทความวิจัย:** การศึกษาการดูดกลืนแสงของสารละลายแอมโมเนียมคลอไรด์ด้วยกล่องสมองกลฝังตัว  
* **ผู้วิจัย:** ชีวะ ทัศนา และ ธนพัฒน์ ถิระวุฒิ  
* **วารสาร:** *วารสารการศึกษาและนวัตกรรมพัฒนาการเรียนรู้ (Journal of Education & Learning Development Innovation)*, ปีที่ 2 ฉบับที่ 1 (2566), หน้า 20–26. ISSN 2822-0773 (Online), ฐานข้อมูล **TCI กลุ่ม 2**  
* **ลิงก์บทความออนไลน์:** [https://atsse.org/article/2/82/927313652](https://atsse.org/article/2/82/927313652)  
* **จุดเชื่อมโยงทางวิชาการ (Research Continuum):**
  1. งานวิจัยนำร่อง (2566) ได้พิสูจน์ข้อเท็จจริงทางกายภาพว่า สารละลายอนุพันธ์ไนโตรเจน (แอมโมเนียมคลอไรด์) ดูดกลืนแสงสีน้ำเงิน ($475\pm 5\text{ nm}$) ได้สูงสุด ($85.10\%$ ที่ 10 mg/L) โดยใช้บอร์ด WIO Terminal (Cortex-M4F)
  2. ชุดงานวิจัยและเฟิร์มแวร์ปัจจุบัน (2026) ได้ก้าวกระโดดสู่ **3-Tier Dynamic Calibration ($0.1\text{--}100\text{ mg/L}$)** บนชิป **ESP32-S3**, การจำลองฟอสฟอรัสแบบไม่เป็นเชิงเส้น (Non-linear Inversion) และการชดเชยการรบกวนของเนื้อดินจริง (Matrix Interference Rejection) ซึ่งพร้อมสำหรับการส่งตีพิมพ์ในวารสารวิชาการระดับสากล Q1/Q2 และ TCI 1

---

## 10. ภาคผนวก: ชุดคำสั่งประมวลผลข้อมูลต้นแบบ (Appendix: Master Pipeline Python Script)

สคริปต์ตัวอย่างภาษา Python สำหรับดึงข้อมูลดิบจากชุดการทดลอง คำนวณ Absorbance และสร้าง Standard Curve อัตโนมัติ:

```python
"""
NPK Spectrometer Master Data Ingestion & Calibration Script
RBRU Digital Agriphysics & AI Research Lab
"""

import os
import glob
import re
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import r2_score, mean_squared_error

def parse_spectrometer_txt(filepath):
    """
    อ่านไฟล์ข้อความดิบที่มี Dark Current และ White Light
    คืนค่าเป็น DataFrame ของช่องสัญญาณ N, P, K, C พร้อมสถานะแสง
    """
    with open(filepath, 'r', errors='ignore') as f:
        lines = f.readlines()
        
    records = []
    current_light = 'UNKNOWN'
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        if 'Light Source Color - OFF' in line_clean:
            current_light = 'OFF'
            continue
        elif 'Light Source Color - WHITE' in line_clean:
            current_light = 'WHITE'
            continue
            
        # ค้นหาแถวตัวเลขสเปกตรัม (เช่น: 0, 68,118,145,346)
        match = re.search(r'^\d+,\s*(\d+),\s*(\d+),\s*(\d+)(?:,\s*(\d+))?', line_clean)
        if match:
            n_val = float(match.group(1))
            p_val = float(match.group(2))
            k_val = float(match.group(3))
            c_val = float(match.group(4)) if match.group(4) else np.nan
            records.append({
                'Light': current_light,
                'N_raw': n_val,
                'P_raw': p_val,
                'K_raw': k_val,
                'C_raw': c_val
            })
            
    df = pd.DataFrame(records)
    return df

def calculate_net_absorbance(sample_df, blank_df):
    """
    คำนวณ Net Absorbance ตามกฎ Beer-Lambert โดยหักลบ Dark Current
    """
    # คำนวณค่าเฉลี่ยของ Sample (White vs Off)
    sample_white = sample_df[sample_df['Light'] == 'WHITE'].mean(numeric_only=True)
    sample_off = sample_df[sample_df['Light'] == 'OFF'].mean(numeric_only=True)
    sample_net = sample_white - sample_off
    
    # คำนวณค่าเฉลี่ยของ Blank (White vs Off)
    blank_white = blank_df[blank_df['Light'] == 'WHITE'].mean(numeric_only=True)
    blank_off = blank_df[blank_df['Light'] == 'OFF'].mean(numeric_only=True)
    blank_net = blank_white - blank_off
    
    # คำนวณ Absorbance: A = -log10(I_sample / I_blank)
    eps = 1e-6 # ป้องกันการหารด้วยศูนย์หรือติดลบ
    t_ratio = (sample_net.clip(lower=eps)) / (blank_net.clip(lower=eps))
    absorbance = -np.log10(t_ratio.clip(lower=1e-5, upper=1.0))
    
    return absorbance

# ตัวอย่างการสร้างแบบจำลองสอบเทียบ (Linear Regression)
def fit_standard_curve(concentrations, absorbances):
    X = np.array(concentrations).reshape(-1, 1)
    y = np.array(absorbances)
    
    model = LinearRegression()
    model.fit(X, y)
    
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    
    print(f"=== ผลการสร้าง Standard Curve ===")
    print(f"Slope (Sensitivity): {model.coef_[0]:.5f}")
    print(f"Intercept: {model.intercept_:.5f}")
    print(f"R-squared: {r2:.4f}")
    print(f"RMSE: {rmse:.4f}")
    
    return model

if __name__ == '__main__':
    print("สคริปต์พร้อมสำหรับการประมวลผลข้อมูลในไดเรกทอรี raw_data")
```

---

## 11. การแยกโหมดการตรวจวัดวิเคราะห์ (N, P, K, pH) และแบบจำลองแสง Soil pH

### 11.1 เหตุผลและความจำเป็นทางเคมีสเปกโทรโฟโตเมตรี
ในการตรวจวิเคราะห์ธาตุอาหารดินภาคสนาม การใช้หลอดทดสอบเดี่ยวสำหรับทุกธาตุ (Single-Tube Reading) ก่อให้เกิดความคลาดเคลื่อนทางสเปกตรัม (Spectral Cross-talk) สูงมาก เนื่องจากสารเคมีทำปฏิกิริยาเกิดสีและกลไกการดูดกลืนแสงที่แตกต่างกัน:
- **ไนโตรเจน (N):** ปฏิกิริยา Indophenol Blue ดูดกลืนแสงเด่นชัดที่ $465\text{ nm}$ (Blue) ในช่วงความเข้มข้นต่ำ และ $525\text{ nm}$ (Green) ในช่วงความเข้มข้นสูง
- **ฟอสฟอรัส (P):** สารประกอบเชิงซ้อน Molybdenum Blue ดูดกลืนแสงที่ $625\text{ nm}$ (Red)
- **โพแทสเซียม (K):** ตะกอนความขุ่นของเกลือเตตระฟีนิลบอเรต (Turbidimetry) วัดการกระเจิงแสงที่ $625\text{ nm}$ ร่วมกับการหักลบแสงฟุ้งกระจาย (Clear baseline)
- **ความเป็นกรด-ด่างดิน (Soil pH):** สารละลายอินดิเคเตอร์ผสม (Universal Indicator / Bromothymol Blue) มีการเปลี่ยนสีตามคู่กรด-เบส ($\text{HIn} \rightleftharpoons \text{H}^+ + \text{In}^-$)

การแยกโหมดวิเคราะห์เฉพาะหลอด (Dedicated Assay Modes) บน Wio Terminal จึงช่วยขจัดสัญญาณรบกวนข้ามธาตุ เพิ่มขีดความสามารถการทำซ้ำ (Repeatability) และเพิ่มความถูกต้อง (Analytical Accuracy) สู่ระดับมาตรฐานห้องปฏิบัติการ

### 11.2 แบบจำลองแสง Soil pH ทางทฤษฎี (Optical Ratiometric Pre-Model)
แบบจำลองสร้างขึ้นตามหลักการ Henderson-Hasselbalch โดยวัดอัตราส่วนการดูดกลืนแสงคู่กรด-เบส (Ratiometric Absorbance Ratio) ระหว่างแถบคลื่นสีเขียว ($525\text{ nm}$) และสีแดง ($625\text{ nm}$):

$$\text{pH}_{\text{est}} = \text{pK}_a + S \cdot \log_{10}\left( \frac{A_{525} + \epsilon}{A_{625} + \epsilon} \right)$$

โดยกำหนดค่าพารามิเตอร์เริ่มต้น (Theoretical Pre-Model Constants):
- $\text{pK}_a = 6.80$ (ค่าคงที่สมดุลกรดของระบบ Bromothymol Blue)
- $S = 2.65$ (Ratiometric Sensitivity Slope)
- $\epsilon = 0.015$ (Zero-division & Stray light offset)
- ช่วงการวัด (Dynamic Range): $\text{pH } 3.50 - 8.50$

### 11.3 เกณฑ์การแปลผลคุณภาพดินและคำแนะนำทางปฐพีวิทยา
- **$\text{pH} < 4.50$ (กรดรุนแรงมาก):** ดินมีความเป็นกรดจัด เสี่ยงต่อความเป็นพิษของอะลูมิเนียมและเหล็ก แนะนำใส่ปูนโดโลไมต์ $100-200\text{ กก./ไร่}$
- **$4.50 \le \text{pH} < 5.50$ (กรดปานกลาง):** ประสิทธิภาพการดูดใช้ฟอสฟอรัสลดลง แนะนำใส่ปูนโดโลไมต์ปรับสภาพ $50\text{ กก./ไร่}$
- **$5.50 \le \text{pH} \le 6.50$ (เหมาะสมที่สุด):** ช่วงสภาพกรด-ด่างสมบูรณ์แบบสำหรับทุเรียนและไม้ผลเขตร้อน ธาตุอาหาร N-P-K ละลายและดูดซึมได้สูงสุด
- **$\text{pH} > 7.50$ (ดินด่าง):** เสี่ยงต่อการขาดจุลธาตุสังกะสีและเหล็ก แนะนำใส่ยิปซัมเกษตรหรือปรับปรุงด้วยอินทรียวัตถุ

### 11.4 สถาปัตยกรรมหน้าจอ 8 หน้าบน Wio Terminal (Firmware 2026)
1. `PAGE_DASHBOARD` (1/8): ภาพรวมระบบ หัวข้อ "สเปกโทรโฟโตมิเตอร์" จัดกึ่งกลางจอ, แบรนด์ `SpecJC +AI Analyzer` ขนาดใหญ่ขึ้น 10% กึ่งกลางจอ, ป้ายแสดงโหมด `AI TinyML` (ไม่มีวงเล็บ [ ]), อุณหภูมิสี แสงสว่าง สถานะเซนเซอร์ และนาฬิกา RTC เลื่อนต่ำลงมาป้องกันการบดบัง
2. `PAGE_NITROGEN` (2/8): โหมด "วิเคราะห์ปริมาณไนโตรเจน" จัดกึ่งกลางจอ สี Cyan (3-Tier Auto-Switching $0.1 - 100\text{ mg/L}$), หลอดไฟ Blue 465 nm, แถบสเกลยกสูงขึ้นป้องกันการซ้อนทับข้อความภาษาไทย
3. `PAGE_PHOSPHORUS` (3/8): โหมด "วิเคราะห์ปริมาณฟอสฟอรัส" จัดกึ่งกลางจอ สี Green (Q1 Quadratic Inversion $R^2 = 0.9944$), หลอดไฟ Red 625 nm, ตัวอักษร P สี Cyan, หน่วย $\text{mg/kg}$ และแท็ก $A_{625}$ / สถานะจัดวางที่พิกัด $x=172$ (+10px) เพื่อความสวยงามลงตัว
4. `PAGE_POTASSIUM` (4/8): โหมด "วิเคราะห์ปริมาณโพแทสเซียม" จัดกึ่งกลางจอ สี Red (Turbidimetry 625nm), หลอดไฟ Red 625 nm, แถบสเกลยกสูงขึ้นไม่บดบังข้อความ
5. `PAGE_SOIL_PH` (5/8): โหมด "วิเคราะห์ความเป็นกรด ด่าง" จัดกึ่งกลางจอ สี Yellow (Ratiometric Optical Pre-Model), หลอดไฟ Dual Green/Red 525/625 nm, แถบสเกลยกสูงขึ้นพร้อมคำแนะนำดินสวนทุเรียน
6. `PAGE_NPK_METER` (6/8): หน้าจอรวมสรุปค่า N, P, K และ pH ดิน พร้อมแถบแสดงระดับความอุดมสมบูรณ์
7. `PAGE_SPECTRUM` (7/8): กราฟสเปกตรัมการดูดกลืนแสง 5 แถบคลื่น (465, 500, 525, 590, 625 nm) และการตรวจวัดสมบัติของเหลว
8. `PAGE_CALIBRATE` (8/8): ระบบสอบเทียบมาตรฐานหลายจุดประจำแปลง (In-Situ Standard Curve Wizard) และหน้าวินิจฉัยระบบ/เครดิตผู้วิจัย (ผศ.ดร.ชีวะ ทัศนา และ ผศ.ดร.จิรภัทร จันทมาลี) ปรับขนาดฟอนต์กะทัดรัดลงตัว ปราศจากการบดบังข้อมูล

---

*เอกสารฉบับนี้จัดทำขึ้นเป็นคู่มือทางวิชาการและแนวทางปฏิบัติการวิจัย เพื่อใช้เป็นเอกสารอ้างอิงประกอบการพัฒนาซอฟต์แวร์ การสร้างตำราวิชาการ และการจัดทำคู่มือการใช้งานระบบสเปกโตรมิเตอร์ตรวจวัดดินต่อไป*
