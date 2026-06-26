import streamlit as st
from PIL import Image
import piexif
import io
import random

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Image SEO Optimizer Max", page_icon="⚙️", layout="wide")
st.title("ระบบแปลงภาพและฝังข้อมูล SEO (Max Version)")

# ==========================================
# จัดการ State สำหรับการซ่อน/ลบรูปภาพ
# ==========================================
if 'dismissed_files' not in st.session_state:
    st.session_state.dismissed_files = set()

# ==========================================
# ข้อมูลจำลองกล้อง (Camera Profiles)
# ==========================================
CAMERA_PROFILES = {
    "📱 Apple iPhone 17 Pro Max": {"make": b"Apple", "model": b"iPhone 17 Pro Max"},
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
    img_desc = st.text_area(
        "คีย์เวิร์ด/คำอธิบายภาพ (ปล่อยว่างได้):", 
        value="", 
        placeholder="เช่น Premium SUS 304 stainless steel equipment with adjustable feet"
    )
    
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

# ✨ ฟีเจอร์ใหม่: ล้างความจำอัตโนมัติเมื่อกดกากบาทเอาไฟล์ออกจากกล่องด้านบนจนหมด
if not uploaded_files:
    st.session_state.dismissed_files = set()

if uploaded_files:
    # กรองไฟล์ที่ผู้ใช้เคยกดปุ่ม "ลบ" ออกไปแล้ว
    active_files = [f for f in uploaded_files if f.name not in st.session_state.dismissed_files]
    
    if active_files:
        st.write("---")
        col_title, col_clear = st.columns([3, 1])
        with col_title:
            st.write("### 📥 ผลลัพธ์พร้อมดาวน์โหลด")
        with col_clear:
            if st.button("🗑️ เคลียร์ภาพทั้งหมดบนหน้าจอ", use_container_width=True):
                # นำไฟล์ที่เหลือทั้งหมดไปใส่ในรายการที่ถูกลบ
                st.session_state.dismissed_files.update([f.name for f in active_files])
                st.rerun()
        
        for i, uploaded_file in enumerate(active_files):
            try:
                img = Image.open(uploaded_file)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # --- ระบบสุ่มค่าสมจริงระดับสูง ---
                f_val = random.choice([(14, 10), (18, 10), (22, 10), (28, 10), (40, 10), (56, 10), (80, 10)])
                exp_val = random.choice([(1, 60), (1, 125), (1, 160), (1, 250), (1, 500), (1, 1000), (1, 2000)])
                iso_val = random.choice([50, 100, 200, 400, 800, 1600])
                focal_val = random.choice([(13, 1), (24, 1), (35, 1), (50, 1), (85, 1), (120, 1)])
                
                contrast_val = random.choice([0, 1, 2])
                saturation_val = random.choice([0, 1, 2])
                sharpness_val = random.choice([0, 1, 2])
                wb_val = random.choice([0, 1])
                metering_val = random.choice([2, 3, 5])
                exp_prog_val = random.choice([2, 3, 4])
                flash_val = random.choice([0, 16, 24])
                digi_zoom_val = random.choice([(10, 10), (12, 10), (20, 10)])
                
                exif_dict = {
                    "0th": {
                        piexif.ImageIFD.Make: CAMERA_PROFILES[cam_choice]["make"],
                        piexif.ImageIFD.Model: CAMERA_PROFILES[cam_choice]["model"],
                        piexif.ImageIFD.Software: b"Adobe Photoshop Lightroom Classic",
                        piexif.ImageIFD.Copyright: domain_choice.encode('utf-8'), 
                    },
                    "Exif": {
                        piexif.ExifIFD.ExposureTime: exp_val,
                        piexif.ExifIFD.FNumber: f_val,
                        piexif.ExifIFD.ISOSpeedRatings: iso_val,
                        piexif.ExifIFD.FocalLength: focal_val,
                        piexif.ExifIFD.Contrast: contrast_val,
                        piexif.ExifIFD.Saturation: saturation_val,
                        piexif.ExifIFD.Sharpness: sharpness_val,
                        piexif.ExifIFD.WhiteBalance: wb_val,
                        piexif.ExifIFD.MeteringMode: metering_val,
                        piexif.ExifIFD.ExposureProgram: exp_prog_val,
                        piexif.ExifIFD.Flash: flash_val,
                        piexif.ExifIFD.DigitalZoomRatio: digi_zoom_val,
                        piexif.ExifIFD.CustomRendered: 0,
                        piexif.ExifIFD.SceneCaptureType: 0,
                    }
                }
                
                if img_desc.strip():
                    windows_title = img_desc.encode('utf-16le')
                    exif_dict["0th"][piexif.ImageIFD.ImageDescription] = img_desc.encode('utf-8')
                    exif_dict["0th"][piexif.ImageIFD.XPTitle] = windows_title
                    exif_dict["0th"][piexif.ImageIFD.XPComment] = windows_title
                
                exif_bytes = piexif.dump(exif_dict)
                img_buffer = io.BytesIO()
                img.save(img_buffer, format="webp", quality=quality_setting, method=6, exif=exif_bytes)
                
                # --- ระบบตั้งชื่อไฟล์ ---
                orig_name = uploaded_file.name.rsplit('.', 1)[0]
                if keyword_name.strip():
                    clean_keyword = keyword_name.strip().replace(" ", "-")
                    if name_position == "เอาไว้ด้านหน้า (Prefix)":
                        new_filename = f"{clean_keyword}-{orig_name}.webp"
                    else:
                        new_filename = f"{orig_name}-{clean_keyword}.webp"
                else:
                    new_filename = f"{orig_name}.webp"
                
                # --- ส่วนแสดงผล ---
                col_img, col_info, col_action = st.columns([1.5, 3, 1])
                with col_img:
                    st.image(img, use_container_width=True) 
                with col_info:
                    st.write(f"**ไฟล์ใหม่:** `{new_filename}`")
                    st.write(f"**ขนาด:** {len(img_buffer.getvalue()) / 1024:.1f} KB") 
                    st.caption(f"📸 สุ่มค่า: f/{f_val[0]/10} | 1/{exp_val[1]}s | ISO {iso_val} | เลนส์ {focal_val[0]}mm")
                    if img_desc.strip():
                        st.caption(f"🏷️ แนบคำอธิบายภาพแล้ว")
                with col_action:
                    st.download_button(
                        label=f"⬇️ โหลด",
                        data=img_buffer.getvalue(),
                        file_name=new_filename,
                        mime="image/webp",
                        key=f"dl_{i}_{uploaded_file.name}",
                        use_container_width=True
                    )
                    # ปุ่มลบ
                    if st.button("❌ ลบ", key=f"del_{i}_{uploaded_file.name}", use_container_width=True):
                        st.session_state.dismissed_files.add(uploaded_file.name)
                        st.rerun()
                        
                st.write("---")
                
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดกับไฟล์ {uploaded_file.name}: {e}")
    else:
        # ✨ ฟีเจอร์ใหม่: ถ้าเผลอกดลบไปหมดแล้ว จะมีปุ่มให้กดเรียกกลับคืนมาได้
        st.info("รูปภาพชุดนี้ถูกเคลียร์ออกไปจากหน้าจอแล้วครับ")
        if st.button("🔄 ดึงภาพชุดเดิมกลับมาใหม่", use_container_width=True):
            st.session_state.dismissed_files = set()
            st.rerun()
