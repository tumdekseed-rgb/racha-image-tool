import streamlit as st
from PIL import Image
import piexif
import io

# ตั้งค่าหน้าเว็บให้กว้างขึ้น
st.set_page_config(page_title="Image SEO Optimizer", page_icon="⚙️", layout="wide")

# สร้างส่วนหัวของหน้าเว็บ
st.title("ระบบแปลงภาพและฝังข้อมูล SEO (Pro Version)")
st.write("เตรียมภาพสินค้าสำหรับโครงสร้างเว็บไซต์และการยิงโฆษณา")

# ==========================================
# แถบตั้งค่าด้านข้าง (Sidebar)
# ==========================================
with st.sidebar:
    st.header("⚙️ ตั้งค่าการแปลงไฟล์")
    
    st.subheader("1. โดเมนและลิขสิทธิ์")
    # เมนูเลือกเว็บไซต์ที่ต้องการฝังลิขสิทธิ์
    domain_choice = st.selectbox(
        "เลือกร้านค้าของคุณ:", 
        ["rachastainless.com", "coolstain.net", "กำหนดเอง..."]
    )
    if domain_choice == "กำหนดเอง...":
        domain_choice = st.text_input("พิมพ์ชื่อเว็บไซต์ของคุณ:")
        
    st.subheader("2. คีย์เวิร์ด (SEO Metadata)")
    # ช่องใส่คำอธิบายภาพ เพื่อทำ LSI / Long-tail keywords
    img_desc = st.text_area(
        "คำอธิบายภาพสำหรับ Google Bot:", 
        "Premium stainless steel equipment with adjustable feet"
    )
    
    st.subheader("3. การตั้งชื่อไฟล์อัจฉริยะ")
    # เปลี่ยนชื่อไฟล์ให้รองรับ SEO
    base_filename = st.text_input("ชื่อไฟล์หลัก (เช่น stainless-ice-bin)", "")
    st.caption("ปล่อยว่างไว้หากต้องการใช้ชื่อไฟล์เดิม")
    
    st.subheader("4. ระดับการบีบอัด")
    # แถบเลื่อนปรับคุณภาพไฟล์
    quality_setting = st.slider("คุณภาพไฟล์ WebP (%)", min_value=10, max_value=100, value=80, step=5)
    st.caption("แนะนำ 80% สำหรับหน้าเว็บปกติ และ 95% สำหรับแบนเนอร์หลัก")

# ==========================================
# พื้นที่หลัก (Main Area)
# ==========================================
uploaded_files = st.file_uploader("ลากไฟล์รูปภาพมาวางที่นี่ (รองรับ JPG, PNG หลายไฟล์พร้อมกัน)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

if uploaded_files:
    st.write("---")
    st.write("### 📥 ผลลัพธ์พร้อมดาวน์โหลด")
    
    for i, uploaded_file in enumerate(uploaded_files):
        try:
            # เปิดรูปภาพ
            img = Image.open(uploaded_file)
            
            # (เทคนิคเสริม) ถ้าภาพเป็น PNG แบบพื้นใส ให้แปลงพื้นหลังทึบก่อน เพื่อให้บีบอัด WebP ได้ดีที่สุด
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # เตรียมข้อมูล EXIF จากค่าที่ผู้ใช้กรอกในแถบด้านข้าง
            exif_dict = {
                "0th": {
                    piexif.ImageIFD.Make: b"Canon",
                    piexif.ImageIFD.Model: b"Canon EOS 5D Mark IV",
                    piexif.ImageIFD.Software: b"Adobe Photoshop Lightroom Classic",
                    piexif.ImageIFD.ImageDescription: img_desc.encode('utf-8'), 
                    piexif.ImageIFD.Copyright: domain_choice.encode('utf-8'), 
                },
                "Exif": {
                    piexif.ExifIFD.ExposureTime: (1, 160),
                    piexif.ExifIFD.FNumber: (56, 10),
                    piexif.ExifIFD.ISOSpeedRatings: 200,
                    piexif.ExifIFD.FocalLength: (50, 1),
                }
            }
            exif_bytes = piexif.dump(exif_dict)
            
            # แปลงไฟล์และบีบอัดตามค่า Quality ที่เลือกบนหน้าเว็บ (พร้อมใช้ Method=6 เสมอ)
            img_buffer = io.BytesIO()
            img.save(img_buffer, format="webp", quality=quality_setting, method=6, exif=exif_bytes)
            
            # ระบบเปลี่ยนชื่อไฟล์ (ถ้าระบุชื่อ base_filename ไว้ จะรันตัวเลขต่อท้ายให้เลย)
            if base_filename:
                # เช่น ถ้ากรอกว่า "sink" จะได้ "sink-01.webp", "sink-02.webp"
                new_filename = f"{base_filename.replace(' ', '-')}-{i+1:02d}.webp"
            else:
                new_filename = uploaded_file.name.rsplit('.', 1)[0] + ".webp"
            
            # ส่วนแสดงผล (แบ่งเป็น 2 คอลัมน์)
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(img, use_container_width=True) 
            with col2:
                st.write(f"**ไฟล์ใหม่:** `{new_filename}`")
                st.write(f"**ขนาด:** {len(img_buffer.getvalue()) / 1024:.1f} KB") 
                
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