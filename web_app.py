import streamlit as st
from PIL import Image
import piexif
import io
import random

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Image SEO Optimizer Pro", page_icon="⚙️", layout="wide")
st.title("ระบบแปลงภาพและฝังข้อมูล SEO (Pro Version)")
st.write("อัปเกรดระบบสุ่มค่ากล้อง (Randomize) และฝัง Metadata ระดับลึกรองรับ Windows Properties")

# ==========================================
# ข้อมูลจำลองกล้อง (Camera Profiles)
# ==========================================
CAMERA_PROFILES = {
    "📱 Apple iPhone 15 Pro Max": {"make": b"Apple", "model": b"iPhone 15 Pro Max"},
    "📷 Full-Frame: Canon EOS R5": {"make": b"Canon", "model": b"Canon EOS R5"},
    "📷 Full-Frame: Sony Alpha 1": {"make": b"SONY", "model": b"ILCE-1"},
    "📷 Full-Frame: Nikon Z9": {"make": b"NIKON CORPORATION", "model": b"NIKON Z 9"},
    "📸 Medium Format: Hasselblad X2D": {"make": b"Hasselblad", "model": b"X2D 100C"},
    "📸 Medium Format: Fujifilm GFX 100S": {"make": b"FUJIFILM", "model": b"GFX 100S"}
}

# ==========================================
# แถบตั้งค่าด้านข้าง (Sidebar)
# ==========================================
with st.sidebar:
    st.header("⚙️ ตั้งค่าการแปลงไฟล์")
    
    st.subheader("1. โดเมนและลิขสิทธิ์")
    domain_choice = st.selectbox("เลือกร้านค้าของคุณ:", ["rachastainless.com", "coolstain.net", "กำหนดเอง..."])
    if domain_choice == "กำหนดเอง...":
        domain_choice = st.text_input("พิมพ์ชื่อเว็บไซต์ของคุณ:")
        
    st.subheader("2. คีย์เวิร์ดและชื่อไฟล์")
    img_desc = st.text_area("คีย์เวิร์ด/คำอธิบายภาพ (SEO):", "Premium stainless steel equipment")
    
    # ระบบเลือกตำแหน่งชื่อไฟล์
    keyword_name = st.text_input("คำศัพท์สำหรับตั้งชื่อไฟล์ (เช่น ice-bin)", "")
    name_position = st.radio("ตำแหน่งคีย์เวิร์ดในชื่อไฟล์:", ["เอาไว้ด้านหน้า (Prefix)", "เอาไว้ด้านหลัง (Suffix)"])
    
    st.subheader("3. จำลองกล้องถ่ายภาพ")
    cam_choice = st.selectbox("เลือกรุ่นกล้องเพื่อฝังข้อมูล:", list(CAMERA_PROFILES.keys()))
    
    st.subheader("4. ระดับการบีบอัด")
    quality_setting = st.slider("คุณภาพไฟล์ WebP (%)", min_value=10, max_value=100, value=80, step=5)

# ==========================================
# พื้นที่หลัก (Main Area)
# ==========================================
uploaded_files = st.file_uploader("ลากไฟล์รูปภาพมาวางที่นี่", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

if uploaded_files:
    st.write("---")
    st.write("### 📥 ผลลัพธ์พร้อมดาวน์โหลด")
    
    for i, uploaded_file in enumerate(uploaded_files):
        try:
            img = Image.open(uploaded_file)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # --- ระบบสุ่มค่าสมจริง (Randomize EXIF Data) ---
            # สุ่มรูรับแสง f/1.4 ถึง f/8.0 (ค่าใน EXIF ต้องคูณ 10)
            f_val = random.choice([(14, 10), (18, 10), (28, 10), (40, 10), (56, 10), (80, 10)])
            # สุ่มสปีดชัตเตอร์ 1/125 ถึง 1/1000
            exp_val = random.choice([(1, 125), (1, 160), (1, 250), (1, 500), (1, 1000)])
            # สุ่ม ISO
            iso_val = random.choice([100, 200, 400, 800])
            # สุ่มระยะเลนส์ (Focal Length)
            focal_val = random.choice([(24, 1), (35, 1), (50, 1), (85, 1)])
            
            # แปลงคีย์เวิร์ดให้รองรับระบบ Windows Properties (ต้องเข้ารหัสเป็น utf-16le)
            windows_title = img_desc.encode('utf-16le')
            
            exif_dict = {
                "0th": {
                    piexif.ImageIFD.Make: CAMERA_PROFILES[cam_choice]["make"],
                    piexif.ImageIFD.Model: CAMERA_PROFILES[cam_choice]["model"],
                    piexif.ImageIFD.Software: b"Adobe Photoshop Lightroom Classic",
                    piexif.ImageIFD.ImageDescription: img_desc.encode('utf-8'), 
                    piexif.ImageIFD.Copyright: domain_choice.encode('utf-8'), 
                    # แทรกแท็กพิเศษเพื่อให้โชว์ในแท็บ Details ของ Windows
                    piexif.ImageIFD.XPTitle: windows_title,
                    piexif.ImageIFD.XPComment: windows_title,
                },
                "Exif": {
                    piexif.ExifIFD.ExposureTime: exp_val,
                    piexif.ExifIFD.FNumber: f_val,
                    piexif.ExifIFD.ISOSpeedRatings: iso_val,
                    piexif.ExifIFD.FocalLength: focal_val,
                }
            }
            exif_bytes = piexif.dump(exif_dict)
            
            # บีบอัดภาพ
            img_buffer = io.BytesIO()
            img.save(img_buffer, format="webp", quality=quality_setting, method=6, exif=exif_bytes)
            
            # --- ระบบตั้งชื่อไฟล์ ---
            orig_name = uploaded_file.name.rsplit('.', 1)[0]
            if keyword_name:
                # ลบช่องว่างออกและแทนด้วยขีด (-)
                clean_keyword = keyword_name.replace(" ", "-")
                if name_position == "เอาไว้ด้านหน้า (Prefix)":
                    new_filename = f"{clean_keyword}-{orig_name}.webp"
                else:
                    new_filename = f"{orig_name}-{clean_keyword}.webp"
            else:
                new_filename = f"{orig_name}.webp"
            
            # แสดงผลและปุ่มดาวน์โหลด
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(img, use_container_width=True) 
            with col2:
                st.write(f"**ไฟล์ใหม่:** `{new_filename}`")
                st.write(f"**ขนาด:** {len(img_buffer.getvalue()) / 1024:.1f} KB") 
                st.caption(f"📸 สุ่มค่า: f/{f_val[0]/10} | 1/{exp_val[1]}s | ISO {iso_val} | เลนส์ {focal_val[0]}mm")
                
                st.download_button(
                    label=f"⬇️ ดาวน์โหลด",
                    data=img_buffer.getvalue(),
                    file_name=new_filename,
                    mime="image/webp",
                    key=f"download_{i}_{new_filename}" 
                )
            st.write("---")
            
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาดกับไฟล์ {uploaded_file.name}: {e}")
