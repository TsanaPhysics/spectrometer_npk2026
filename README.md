# spectrometer_npk2026
**เครื่องสเปกโทรโฟโตมิเตอร์ตรวจวัดธาตุอาหารหลักในดิน (NPK Level Meter 1.02) พร้อมระบบประมวลผล TinyML / Edge AI ในตัว**

โครงการพัฒนาระบบตรวจวัดธาตุอาหารหลักในดิน (Nitrogen - N, Phosphorus - P, Potassium - K) ระดับห้องปฏิบัติการภาคสนามโดยอาศัยหลักการสเปกโทรโฟโตเมตรี (Spectrophotometry) ผ่านโมดูลไดโอดเปล่งแสงหลายสี (RGB LED) ร่วมกับเซนเซอร์วัดค่าสีแบบดิจิทัลความละเอียดสูง TCS34725 และประมวลผลบนไมโครคอนโทรลเลอร์ Seeed Studio Wio Terminal พร้อมระบบการเรียนรู้เชิงลึกแบบ TinyML Multi-Layer Perceptron (MLP) บูรณาการในเฟิร์มแวร์โดยตรง

---

## จุดเด่นของระบบ (Key Highlights)
1. **TinyML / Edge AI Direct Firmware Inference:** โครงข่ายประสาทเทียม Multi-Layer Perceptron ($6 \to 12 \to 8 \to 3$) ประมวลผลแบบ Real-time บนชิป Cortex-M4F 120 MHz ใช้เวลาคำนวณเพียง $12.4\ \mu\text{s}$ ต่อตัวอย่าง
2. **Dual-Mode Analytical Engine:** สลับโหมดการคำนวณได้ทันทีระหว่างแบบจำลองปัญญาประดิษฐ์ `[AI]` และแบบจำลองพหุนามดั้งเดิม `[PL]` ด้วยการโยกจอยสติ๊กขึ้นด้านบน
3. **Matrix Turbidity Compensation:** ระบบชดเชยการกระเจิงของแสงจากสารแขวนลอยและความขุ่นในสารละลายสกัดดินด้วยช่องสัญญาณ Clear และการแปลงค่า Absorbance สัมพัทธ์
4. **Intuitive Physical Controls:** ปุ่ม A (แดง), ปุ่ม B (เขียว), ปุ่ม C (น้ำเงิน) และจอยสติ๊กกดตรงกลาง (ขาว) สั่งเปิด/ปิดแสงสเปกตรัมที่ต้องการได้อย่างอิสระ
5. **Auto Data Logging:** บันทึกข้อมูลและเวลาลงในการ์ด microSD Card แบบอัตโนมัติ

---

## โครงสร้างระบบฮาร์ดแวร์ (Hardware Architecture)
- **ประมวลผลกลาง:** Seeed Studio Wio Terminal (Microchip ATSAMD51P19A, ARM Cortex-M4F 120 MHz, 192 KB RAM, 512 KB Flash, Hardware FPU)
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
| **จอยสติ๊กโยกขึ้น** | ด้านหน้าตัวเครื่อง | WIO_5S_UP | สลับโหมดการคำนวณ **[AI] TinyML $\leftrightarrow$ [PL] Polynomial** |

---

## สถาปัตยกรรม TinyML Edge AI บน Wio Terminal

### เวกเตอร์คุณลักษณะนำเข้า (Input Features $\in \mathbb{R}^6$)
$$\mathbf{x} = \begin{bmatrix} b_p & g_p & r_p & c_{\text{ratio}} & \text{lux}_{\text{norm}} & A_{\text{est}} \end{bmatrix}^T$$
- $b_p, g_p, r_p$: สัดส่วนร้อยละของสัญญาณแสงสีน้ำเงิน เขียว และแดง
- $c_{\text{ratio}} = C / (R+G+B+\epsilon)$: สัดส่วนช่องสัญญาณ Clear ชดเชยความขุ่น
- $\text{lux}_{\text{norm}} = \text{Lux} / 1000.0$: ความสว่างสัมพัทธ์
- $A_{\text{est}} = -\log_{10}((R+G+B+1.0)/(3 \times 65535.0))$: การดูดกลืนแสงสัมพัทธ์ตามกฎของเบียร์-แลมเบิร์ต

### โครงสร้างโครงข่ายประสาทเทียม (Feed-Forward MLP)
- **Layer 1 (Hidden 1):** $\mathbf{z}^{(1)} = \text{ReLU}(\mathbf{W}^{(1)} \tilde{\mathbf{x}} + \mathbf{b}^{(1)}) \in \mathbb{R}^{12}$
- **Layer 2 (Hidden 2):** $\mathbf{z}^{(2)} = \text{ReLU}(\mathbf{W}^{(2)} \mathbf{z}^{(1)} + \mathbf{b}^{(2)}) \in \mathbb{R}^{8}$
- **Output Layer:** $\hat{\mathbf{y}} = \mathbf{W}^{(3)} \mathbf{z}^{(2)} + \mathbf{b}^{(3)} \in \mathbb{R}^{3} \quad (N, P, K\text{ mg/kg})$

### สมรรถนะโมเดล (Validation Metrics)
- **ไนโตรเจน (N):** $R^2 = 0.9918$
- **ฟอสฟอรัส (P):** $R^2 = 0.9880$
- **โพแทสเซียม (K):** $R^2 = 0.9897$
- **การใช้ทรัพยากร:** แฟลช 864 ไบต์, แรม 128 ไบต์, ความหน่วงเวลาคำนวณ $12.4\ \mu\text{s}$

---

## โครงสร้างโปรเจกต์ (Repository Structure)
```
spectrometer_npk2026/
├── README.md                           # คำอธิบายโปรเจกต์และคู่มือเริ่มต้นฉบับย่อ
├── firmware/
│   ├── TinyML_Model.h                  # เฮดเดอร์โมเดล TinyML C++ Zero-Allocation
│   ├── train_tinyml_model.py           # สคริปต์ฝึกสอนและส่งออกพารามิเตอร์โมเดล AI
│   ├── spectrometer_npk2026/
│   │   ├── spectrometer_npk2026.ino    # สเก็ตช์หลักสำหรับ Arduino IDE / CLI
│   │   └── TinyML_Model.h              # โมเดล TinyML C++ ฝังตัว
│   └── build/                          # ไฟล์ไบนารี .bin, .hex, .uf2 สำหรับแฟลชทันที
├── docs/
│   ├── NPK_Spectrometer_Manual.pdf     # เอกสารคู่มือฉบับสมบูรณ์ (18 หน้า ผ่านมาตรฐาน RBRU)
│   ├── manual_assembly_operation.md    # คู่มือการประกอบและใช้งานแบบ Markdown
│   └── latex/                          # ซอร์สโค้ด XeLaTeX มาตรฐานตำรา มรภ.รำไพพรรณี
└── data/
    └── NPK_sample_log.csv              # ตัวอย่างชุดข้อมูลผลการวัด
```

---

## คู่มือการประกอบและเอกสารทางวิชาการ (Documentation)
- อ่านคู่มือฉบับสมบูรณ์ในรูปแบบ Markdown ได้ที่ [docs/manual_assembly_operation.md](docs/manual_assembly_operation.md)
- ดาวน์โหลดคู่มือวิชาการฉบับพิมพ์ทางการ (PDF 18 หน้า จัดหน้าตามระเบียบ มรภ.รำไพพรรณี) ได้ที่ [docs/NPK_Spectrometer_Manual.pdf](docs/NPK_Spectrometer_Manual.pdf)

---

## ใบอนุญาตและการอ้างอิง (License and Citation)
ผลงานนี้เผยแพร่ภายใต้สัญญาอนุญาต **MIT License**  
หากนำผลงานหรือแบบจำลองไปใช้ในงานวิจัยทางวิชาการ กรุณาอ้างอิง:
> ชีวะ ทัศนา และคณะ. (2569). *คู่มือการประกอบ ติดตั้ง และใช้งานเครื่องสเปกโทรโฟโตมิเตอร์ตรวจวัดธาตุอาหารหลักในดิน (NPK Level Meter 1.02)*. หน่วยวิจัยฟิสิกส์เพื่อการเกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics) สาขาวิชาฟิสิกส์ คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี.
