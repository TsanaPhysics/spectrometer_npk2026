#!/usr/bin/env python3
"""Replace long Thai recommendation strings with shortened versions."""
import re

replacements = [
    # P page - saturation
    ('drawThaiTextSm("สถานะ : แสงอิ่มตัว (A > 0.500) เจือจาง 1:5"',
     'drawThaiTextSm("สถานะ แสงอิ่มตัว เจือจาง 1:5"'),
    ('drawThaiTextSm("คำเตือน : กรุณาเจือจางตัวอย่างก่อนวัดซ้ำ"',
     'drawThaiTextSm("คำเตือน วัดซ้ำหลังเจือจาง 1:5"'),
    # P page - low
    ('drawThaiTextSm("สถานะ : ฟอสฟอรัสต่ำกว่าเกณฑ์"',
     'drawThaiTextSm("สถานะ P ต่ำกว่าเกณฑ์"'),
    ('drawThaiTextSm("แนะนำ : ใส่ปุ๋ยฟอสเฟตบำรุงรากและตาดอก"',
     'drawThaiTextSm("แนะนำ ปุ๋ยฟอสเฟต 18-46-0 บำรุงราก"'),
    # P page - ok
    ('drawThaiTextSm("สถานะ : ฟอสฟอรัสระดับเหมาะสม"',
     'drawThaiTextSm("สถานะ P ระดับเหมาะสม"'),
    ('drawThaiTextSm("แนะนำ : ธาตุอาหารพร้อมใช้ ระบบรากสมบูรณ์"',
     'drawThaiTextSm("แนะนำ บำรุงราก ส่งเสริมตาดอก"'),
    # P page - high
    ('drawThaiTextSm("สถานะ : ฟอสฟอรัสสะสมสูง"',
     'drawThaiTextSm("สถานะ P สะสมสูง"'),
    ('drawThaiTextSm("แนะนำ : งดปุ๋ยฟอสฟอรัสป้องกันตรึงจุลธาตุ"',
     'drawThaiTextSm("แนะนำ งดปุ๋ย P ป้องกันตรึงจุลธาตุ"'),
    # K page - low
    ('drawThaiTextSm("สถานะ : โพแทสเซียมต่ำกว่าเกณฑ์"',
     'drawThaiTextSm("สถานะ K ต่ำกว่าเกณฑ์"'),
    ('drawThaiTextSm("แนะนำ : เสริมปุ๋ยโพแทสเซียมเพิ่มความแข็งแรง"',
     'drawThaiTextSm("แนะนำ เสริมปุ๋ย KCl 0-0-60"'),
    # K page - ok
    ('drawThaiTextSm("สถานะ : โพแทสเซียมระดับเหมาะสม"',
     'drawThaiTextSm("สถานะ K ระดับเหมาะสม"'),
    ('drawThaiTextSm("แนะนำ : ช่วยพัฒนาคุณภาพผลผลิตเพิ่มความหวาน"',
     'drawThaiTextSm("แนะนำ ช่วยคุณภาพผล เพิ่มความหวาน"'),
    # K page - high
    ('drawThaiTextSm("สถานะ : โพแทสเซียมสะสมสูง"',
     'drawThaiTextSm("สถานะ K สะสมปริมาณสูง"'),
    ('drawThaiTextSm("แนะนำ : ชะลอปุ๋ย K ป้องกันยับยั้งแคลเซียม"',
     'drawThaiTextSm("แนะนำ ชะลอ K ป้องกัน Ca/Mg"'),
    # pH page - strong acid
    ('drawThaiTextSm("วินิจฉัย : ดินกรดรุนแรง (pH < 4.5)"',
     'drawThaiTextSm("การวินิจฉัย ดินกรดรุนแรง pH < 4.5"'),
    ('drawThaiTextSm("แนะนำ : ใส่ปูนโดโลไมต์ 100-200 กก./ไร่"',
     'drawThaiTextSm("แนะนำ ปูนโดโลไมต์ 100-200 กก./ไร่"'),
    # pH page - moderate acid
    ('drawThaiTextSm("วินิจฉัย : ดินกรดปานกลาง (pH 4.5-5.5)"',
     'drawThaiTextSm("การวินิจฉัย ดินกรดปานกลาง 4.5-5.5"'),
    ('drawThaiTextSm("แนะนำ : เสริมปูนขาวยกระดับ pH ดิน"',
     'drawThaiTextSm("แนะนำ เสริมปูนขาว ยก pH ดิน"'),
    # pH page - optimal
    ('drawThaiTextSm("วินิจฉัย : ดินเหมาะสมสำหรับทุเรียน"',
     'drawThaiTextSm("การวินิจฉัย ดินเหมาะสม pH ทุเรียน"'),
    ('drawThaiTextSm("แนะนำ : รักษาระดับดิน ดูดซึมธาตุอาหารสูงสุด"',
     'drawThaiTextSm("แนะนำ รักษาระดับ ดูดซึมสูงสุด"'),
    # pH page - alkaline
    ('drawThaiTextSm("วินิจฉัย : ดินเป็นด่าง (pH > 6.5)"',
     'drawThaiTextSm("การวินิจฉัย ดินเป็นด่าง pH > 6.5"'),
    ('drawThaiTextSm("แนะนำ : เติมยิปซัมเกษตรปรับลด pH"',
     'drawThaiTextSm("แนะนำ ยิปซัมเกษตร ปรับลด pH"'),
]

with open('firmware/spectrometer_npk2026.ino', 'r', encoding='utf-8') as f:
    content = f.read()

original = content
for old, new in replacements:
    content = content.replace(old, new)

changed = sum(1 for o, n in replacements if o.split('"')[1] not in content)
with open('firmware/spectrometer_npk2026.ino', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Done. Applied replacements. File changed: {content != original}")
# Show which ones were actually found and replaced
for old, new in replacements:
    key = old.split('"')[1]
    if key not in content:
        print(f"  REPLACED: {key[:40]}")
    else:
        print(f"  NOT FOUND: {key[:40]}")
