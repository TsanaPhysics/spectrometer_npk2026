# ⚛️ The Quantum Quartet • 3D Chibi Collection (Pixar / Ghibli Style)
### ชุดแบบจำลอง 3 มิติหัวโตสไตล์พิกซาร์-จิบลิ: สี่บิดาแห่งฟิสิกส์ควอนตัม
**Albert Einstein • Max Planck • Werner Heisenberg • Erwin Schrödinger**
**สังกัด:** หน่วยวิจัยฟิสิกส์เกษตรดิจิทัลและปัญญาประดิษฐ์ (AI4D AgriPhysics) สาขาวิชาฟิสิกส์ คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี

---

## 📌 ภาพรวมโครงการ (Project Overview)

โครงการนี้ออกแบบและสร้างสรรค์ชุดแบบจำลอง 3 มิติเต็มตัว (Full-Body Chibi Figurines) ในอัตราส่วนหัวโตสไตล์แอนิเมชันระดับโลก **Pixar Animation Studios & Studio Ghibli** เพื่อถ่ายทอดเรื่องราว ประวัติศาสตร์ และสมการเอกลักษณ์ของ 4 เสาหลักผู้ให้กำเนิดกลศาสตร์ควอนตัมและฟิสิกส์ยุคใหม่:
1. **อัลเบิร์ต ไอน์สไตน์ (Albert Einstein)**
2. **มักซ์ พลังค์ (Max Planck)**
3. **แวร์เนอร์ ไฮเซินแบร์ก (Werner Heisenberg)**
4. **แอร์วิน ชเรอดิงเงอร์ (Erwin Schrödinger & His Cat)**

โครงสร้างโมเดลสร้างขึ้นด้วยระบบคณิตศาสตร์ **Vectorized Signed Distance Fields (SDF)** และอัลกอริทึม **Marching Cubes** การันตีโครงสร้างตาข่ายสามเหลี่ยมเนื้อตันสมบูรณ์แบบ **100% Watertight Manifold (ขอบเปิด Boundary Edges = 0)** พร้อมพิมพ์ 3 มิติ (3D Printing Ready) ทุกระบบ ทั้ง FDM/FFF และ SLA/Resin

![The Quantum Quartet 3D Concept Art](quantum_chibi_quartet.jpg)

---

## 🎨 การสร้างโมเดล 3 มิติให้มีสีสันสมจริง (How to Create Realistic Colored 3D Models)

### 1. ทำไมไฟล์ `.stl` ทั่วไปจึงไม่มีสี?
ไฟล์ **STL (StereoLithography)** ถูกคิดค้นขึ้นตั้งแต่ปี 1987 โดยมีเป้าหมายหลักสำหรับการส่งพิกัดทางเรขาคณิตไปยังเครื่องพิมพ์ 3D ดั้งเดิม โครงสร้างข้อมูลของ STL บันทึกเพียง **พิกัดจุดยอด (Vertices) และเวกเตอร์แนวฉาก (Normals)** ของสามเหลี่ยมเท่านั้น **ไม่มีฟิลด์สำหรับเก็บข้อมูลสี วัสดุ หรือเท็กซ์เจอร์ใดๆ เลย** ส่งผลให้เมื่อเปิดในโปรแกรม CAD หรือ Slicer ทั่วไป โมเดลจะแสดงผลเป็นสีเทา สีเบจ หรือสีพื้นโมโนโครม

### 2. เทคโนโลยีและฟอร์แมตสำหรับโมเดล 3 มิติสีสันสมจริง
เพื่อให้โมเดลมีสีสัน แสงเงา และมิติสมจริงตามภาพคอนเซ็ปต์อาร์ต 8K โครงการนี้ได้พัฒนาไปป์ไลน์สร้างโมเดลสีขั้นสูงใน 3 ฟอร์แมตหลัก:

1. **GLB / glTF 2.0 (PBR Photorealistic 3D Standard - แนะนำสูงสุด):**
   - มาตรฐานอุตสาหกรรมยุคใหม่ (JPEG of 3D) ที่ผสานข้อมูลเรขาคณิต ตาข่าย และคุณสมบัติวัสดุฟิสิกส์ **PBR (Physically Based Rendering)** ไว้ในไฟล์เดียว
   - รองรับ **Base Color (Albedo)**, **Roughness (ความหยาบ/ด้านของผิวผ้า)**, **Metallic (ความเงาวาวของป้ายทองเหลือง)**, และ **Emissive Glow (การเรืองแสงเปล่งพลังงานของลูกแก้ว $h\nu$ และอะตอม $\Delta x \Delta p$)**
   - สามารถเปิดดูได้ทันทีบนเบราว์เซอร์ (WebGL Three.js), Windows 3D Viewer, macOS QuickLook (กด Spacebar ดูได้ทันทีใน Finder), Blender, Maya, Unreal Engine, และ Unity
2. **Color PLY (Polygon File Format with Vertex Colors):**
   - บันทึกพิกัด $(x, y, z)$ ควบคู่กับค่าสีจริงแบบจุดต่อจุด $(R, G, B)$ สำหรับโปรแกรมตัดต่อ 3D และเครื่องพิมพ์ 3D สีระบบ Binder Jetting (เช่น Mimaki, ZCorp)
3. **3MF / Multi-Color Slicing (สำหรับเครื่องพิมพ์ 3D FDM หลายสี):**
   - รองรับระบบหัวฉีดหลายสี (Bambu Lab AMS, Prusa MMU3, Anycubic Kobra 3) โดยสามารถแยกพาร์ตหรือใช้ระบบระบายสีใน Bambu Studio / PrusaSlicer ได้อย่างแม่นยำ

---

## 🧑‍🔬 3. รายละเอียด 4 ตัวละครและการเทียบเฉดสีตามภาพคอนเซ็ปต์ (Color Palette Calibration)

| ตัวละคร (Physicist) | สไตล์และรายละเอียดสีสันตามภาพคอนเซ็ปต์ | พร็อพเอกลักษณ์และระบบเรืองแสง (Emissive Glow) | สมการก้องโลก (Signature Formula) |
| :--- | :--- | :--- | :--- |
| **Albert Einstein**<br>*(อัลเบิร์ต ไอน์สไตน์)* | • ผิวสีพีชอบอุ่น `#fcd5be` แก้มชมพูระเรื่อ `#fca5a5`<br>• นัยน์ตาสีน้ำตาลเข้มแวววาว พร้อมประกายไฮไลต์สีขาว `#ffffff`<br>• ทรงผมฟูฟ่องและหนวดหนาสีขาวนวล `#f8fafc`<br>• เสื้อสเวตเตอร์ไหมพรมสีเทาเฮเทอร์ `#64748b` กางเกงน้ำตาล | **กระดานชนวนชอล์ก E=mc²**<br>• กรอบไม้โอ๊กสีน้ำตาลทอง `#b45309`<br>• แผ่นกระดานชนวนสีดำด้าน `#1e293b`<br>• ตัวอักษรชอล์กสีขาวคมชัด `E = mc²` | $$E = mc^2$$<br>$$h\nu = W + E_k$$ *(Nobel 1921)* |
| **Max Planck**<br>*(มักซ์ พลังค์)* | • หน้าผากกว้าง ทรงผมและหนวดสุภาพบุรุษสีเงินประกายเทา `#a1a1aa`<br>• แว่นตาหนีบจมูก (Pince-Nez) สีโลหะเข้ม `#374151`<br>• สูททักซิโด้สีดำสนิท `#18181b` เสื้อเชิ้ตขาว หูกระต่ายดำ | **ลูกแก้วควอนตัมพลังงานเรืองแสง (hν)**<br>• แกนกลางเปล่งแสงทองเจิดจ้า `#fffbeb`<br>• ผิวลูกแก้วสีทองอำพันเรืองแสง `#fbbf24` (Emissive)<br>• วงแหวนระดับพลังงานหมุนวนรอบตัว | $$E = nh\nu$$<br>$$h = 6.626 \times 10^{-34}\text{ J}\cdot\text{s}$$ *(Nobel 1918)* |
| **Werner Heisenberg**<br>*(แวร์เนอร์ ไฮเซินแบร์ก)* | • ทรงผมลอนปัดข้างสีน้ำตาลเชสต์นัต `#6b3e26`<br>• นัยน์ตาสีน้ำตาลสดใส ผิวขาวอมชมพูสไตล์หนุ่ม 1920s<br>• เสื้อคาร์ดิแกนสีน้ำเงินรอยัลบลู `#2563eb` เนกไทสีกรมท่า `#1e3a8a`<br>• กางเกงสแล็กสีเบจชิโน `#a89078` | **วงแหวนออร์บิทัลอะตอมควอนตัม**<br>• นิวเคลียสอะตอมสีฟ้าขาวเรืองแสง `#e0f2fe`<br>• วงแหวนความน่าจะเป็นสีฟ้าครามนีออน `#00e5ff` (Emissive Glow) ตัดกัน 2 ระนาบ | $$\Delta x \cdot \Delta p \ge \frac{\hbar}{2}$$<br>Matrix Mechanics *(Nobel 1932)* |
| **Erwin Schrödinger**<br>*(แอร์วิน ชเรอดิงเงอร์)* | • ทรงผมหวีเรียบสีน้ำตาลเข้ม `#3a2312`<br>• แว่นตากรอบกลมวินเทจสีเทาเข้ม `#374151`<br>• เสื้อกั๊กไหมพรมถักลายสีเขียวเอเมอรัลด์ `#166534` เสื้อเชิ้ตขาว<br>• กางเกงผ้าทวีดสีเทาควันบุหรี่ `#475569` | **กล่องทดลองและน้องแมวควอนตัม**<br>• กล่องกระดาษคราฟต์สีน้ำตาลอ่อน `#d97706` สลัก `Ψ?`<br>• น้องแมวส้มขนนุ่ม `#ea580c` หน้าอกและสองอุ้งเท้าสีขาว `#fff7ed`<br>• ใบหูด้านในและจมูกสีชมพูอ่อน `#f472b6` | $$i\hbar \frac{\partial \psi}{\partial t} = \hat{H}\psi$$<br>Schrödinger's Cat *(Nobel 1933)* |
| **ฐานรอง Plinth**<br>*(ทุกตัวละคร)* | • แท่นไม้วอลนัตแกะสลักสีน้ำตาลเข้มขัดเงา `#3e2723` (ความหยาบ Roughness 0.45)<br>• ป้ายชื่อโลหะทองเหลืองโบราณ `#d4af37` (ความวาว Metallic 0.85) พร้อมตัวอักษรจารึกชื่อ-นามสกุลคมชัด | | |

![Quantum Chibi 3D Mesh Showcase](quantum_chibi_showcase.png)

---

## 📁 โครงสร้างไฟล์ในโฟลเดอร์ (Directory Architecture)

```
models_3d/quantum_physicists_chibi/
├── README.md                          # เอกสารกำกับ ทฤษฎีสี PBR และการพิมพ์ 3 มิติ (ไฟล์นี้)
├── quantum_physicists_chibi.scad      # ซอร์สโค้ดพารามิเตอร์ OpenSCAD (ปรับแต่งขนาดและโมดูลาร์ได้อิสระ)
├── quantum_chibi_quartet.jpg          # ภาพเรนเดอร์คอนเซ็ปต์อาร์ต 3D Pixar/Ghibli สี่บิดาควอนตัม (8K Master)
├── quantum_chibi_showcase.png         # ภาพพล็อตเปรียบเทียบเมช 3 มิติ 4 บิดาควอนตัมความละเอียดสูง
├── quantum_chibi_viewer_3d.html       # เว็บแอป Three.js Full-Color PBR & STL Interactive Viewer
│
├── 🌈 [FULL-COLOR PBR GLB FILES]      # ไฟล์โมเดล 3D สีสันสมจริงตามภาพคอนเซ็ปต์ (glTF 2.0 PBR)
│   ├── einstein_chibi_colored.glb     # ไอน์สไตน์สีสมจริง (เสื้อเทา, กระดานไม้ E=mc², ผมขาวฟู)
│   ├── planck_chibi_colored.glb       # พลังค์สีสมจริง (ทักซิโด้ดำ, แว่นหนีบจมูก, ลูกแก้วทองเรืองแสง hν)
│   ├── heisenberg_chibi_colored.glb   # ไฮเซินแบร์กสีสมจริง (คาร์ดิแกนน้ำเงิน, อะตอมฟ้าครามเรืองแสง)
│   ├── schrodinger_chibi_colored.glb  # ชเรอดิงเงอร์สีสมจริง (กั๊กเขียว, กล่องคราฟต์ Ψ?, น้องแมวส้มหูชมพู)
│   └── quantum_quartet_diorama_colored.glb # ไดโอรามา 4 ท่านสีสมจริงครบทีมบนฐานไม้วอลนัตและป้ายทองเหลือง
│
├── 🎨 [COLOR PLY VERTEX MESHES]       # ไฟล์โมเดลสีแบบ Per-Vertex RGB สำหรับพิมพ์สี / Blender
│   ├── einstein_chibi_colored.ply     # ไอน์สไตน์ Color PLY (2.80 MB)
│   ├── planck_chibi_colored.ply       # พลังค์ Color PLY (2.52 MB)
│   ├── heisenberg_chibi_colored.ply   # ไฮเซินแบร์ก Color PLY (2.59 MB)
│   ├── schrodinger_chibi_colored.ply  # ชเรอดิงเงอร์ Color PLY (2.58 MB)
│   └── quantum_quartet_diorama_colored.ply # ไดโอรามา Color PLY (5.69 MB)
│
└── 🖨️ [3D PRINTING WATERTIGHT STLS]   # ไฟล์โมเดลเนื้อตัน 100% Watertight Solid (0 Boundary Edges)
    ├── einstein_chibi_3d.stl          # ไอน์สไตน์ STL พร้อมพิมพ์ (143,180 Tris | 6.83 MB)
    ├── planck_chibi_3d.stl            # พลังค์ STL พร้อมพิมพ์ (128,752 Tris | 6.14 MB)
    ├── heisenberg_chibi_3d.stl        # ไฮเซินแบร์ก STL พร้อมพิมพ์ (132,700 Tris | 6.33 MB)
    ├── schrodinger_chibi_3d.stl       # ชเรอดิงเงอร์ STL พร้อมพิมพ์ (132,048 Tris | 6.30 MB)
    └── quantum_quartet_diorama_3d.stl # ไดโอรามา STL พร้อมพิมพ์ (290,830 Tris | 13.87 MB)
```

---

## 🖨️ คำแนะนำการพิมพ์ 3 มิติ (3D Printing & Slicing Guide)

### 1. ขนาดโมเดลแนะนำ (Scale Guide)
* **สเกลตั้งโต๊ะสะสม (Default 1:1 Scale in CAD):** ความสูง $90 - 100\text{ mm}$ (ฐานกว้าง $52 \times 42\text{ mm}$) เหมาะกับการตั้งบนโต๊ะทำงาน แท่นจัดแสดง หรือโต๊ะทดลองฟิสิกส์
* **สเกลย่อส่วนพวงกุญแจ (Keyring Mini 50%):** ปรับลดเหลือ $50\text{ mm}$ ในโปรแกรม Slicer
* **สเกลใหญ่สำหรับงานจัดแสดง (Display Grade 150%):** ขยายเป็น $150\text{ mm}$ เพื่อความคมชัดสูงสุดของตัวอักษรบนกระดาน $E=mc^2$ และใบหน้าน้องแมว

### 2. การตั้งค่าเครื่องพิมพ์เส้นพลาสติก (FDM/FFF: Prusa, Bambu Lab, Creality)
- **Layer Height:** `0.12 mm` (แนะนำสำหรับงานสะสม) หรือ `0.16 mm`
- **Support:** เปิดใช้งาน **Tree Support (Organic)** ทำมุมโอเวอร์แฮงก์ > `48°` รองรับใต้คาง ใต้กล่อง/กระดาน และชายแขนเสื้อ แกะออกง่ายไม่ทิ้งรอย
- **Infill:** `15% - 20%` ลาย **Gyroid**
- **วัสดุ:** PLA+ สีหินอ่อน (Marble White), สีบรอนซ์ (Silk Gold), หรือสีขาวด้านสำหรับเพ้นท์สีโมเดล

### 3. การตั้งค่าเครื่องพิมพ์เรซิน (SLA/MSLA/DLP: Anycubic, Elegoo)
- **Layer Height:** `0.05 mm` (50 ไมครอน) หรือ `0.025 mm`
- **Orientation:** เอียงตัวโมเดลไปด้านหลังทำมุม $25^\circ - 30^\circ$ เทียบกับฐานพิมพ์
- **Supports:** ใช้ Light Supports บริเวณเส้นผมและกรอบแว่นตาตา, Medium Supports ใต้ฐาน Plinth

---

## 🌐 การใช้งาน WebGL 3D Interactive Viewer (`quantum_chibi_viewer_3d.html`)

สามารถเปิดดูและหมุนโมเดล 3 มิติแบบ 360 องศาได้ทั้งในคอมพิวเตอร์และมือถือ:
- **เปิดไฟล์โดยตรง:** ดับเบิลคลิกเปิด [`quantum_chibi_viewer_3d.html`](quantum_chibi_viewer_3d.html) หรือเปิดผ่าน [`../../web/quantum_chibi_viewer_3d.html`](../../web/quantum_chibi_viewer_3d.html)
- **สลับตัวละคร:** เลือกชมฟิกเกอร์เดี่ยวหรือไดโอรามาครบทีม 4 ท่าน
- **โหมดแสงสตูดิโอ 4 ธีม:**
  - 🎨 **Pixar Warm Studio:** แสงอบอุ่นนุ่มนวล เน้นผิวและเสื้อผ้าสไตล์ 3D Clay
  - 🌿 **Ghibli Sunlight:** แสงแดดยามบ่ายในทุ่งหญ้า สดใส ละมุนตา
  - ⚡ **Quantum Cyber:** แสงไฟนีออนฟ้า-ชมพูสไตล์ควอนตัมแล็บ
  - 🏛️ **Alabaster Marble:** แสงสตูดิโอสีขาวบริสุทธิ์โชว์สรีระรูปปั้นหินอ่อน
- **ปุ่มดาวน์โหลด:** โหลดไฟล์ `.stl` ของตัวละครที่กำลังเลือก, โค้ด `.scad`, และภาพคอนเซ็ปต์อาร์ตได้ทันที
