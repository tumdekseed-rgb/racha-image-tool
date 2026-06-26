import streamlit as st
from PIL import Image
import piexif
import io
import random
import google.generativeai as genai

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Image SEO Optimizer Max Pro", page_icon="🚀", layout="wide")
st.title("ระบบแปลงภาพ ฝังข้อมูล SEO และประทับลายน้ำ (Max Pro Version)")

# จัดการ State
if 'dismissed_files' not in st.session_state:
    st.session_state.dismissed_files = set()
if 'ai_results' not in st.session_state:
    st.session_state.ai_results = {}

# โปรไฟล์กล้องระดับโปร
CAMERA_PROFILES = {
    "📱 Apple iPhone 17 Pro Max": {"make": b"Apple", "model": b"iPhone 17 Pro Max"},
    "📱 Apple iPhone 15 Pro Max": {"make": b"Apple", "model": b"iPhone 15 Pro Max"},
    "📷 Full-Frame: Canon EOS R5": {"make": b"Canon", "model": b"Canon EOS R5"},
    "📷 Full-Frame: Sony Alpha 1": {"make": b"SONY", "model": b"ILCE-1"},
    "📸 Medium Format: Hasselblad X2D": {"make": b"Hasselblad", "model": b"X2D 100C"},
    "📸 Medium Format: Fujifilm GFX 100S": {"make": b"FUJIFILM", "model": b"GFX 100S"}
}

# ==========================================
# แถบตั้งค่าด้านข้าง (Sidebar)
# ==========================================
with st.sidebar:
    st.header("🔑 1. ระบบ AI วิเคราะห์ภาพจริง")
    api_key = st.text_input("ใส่ Gemini API Key (ถ้ามี):", type="password", help="ใส่คีย์เพื่อเปิดใช้งานระบบสแกนภาพจริง")
    ai_lang = st.radio("ภาษาที่ต้องการให้ AI วิเคราะห์ทำ SEO:", ["ภาษาไทย (Thai)", "ภาษาอังกฤษ (English)"])
    
    st.header("🛡️ 2. ระบบประทับตราลายน้ำ")
    watermark_file = st.file_uploader("อัปโหลดโลโก้ร้านค้า (ไฟล์ .PNG พื้นใส):", type=['png'])
    
    if watermark_file:
        wm_position = st.selectbox("ตำแหน่งลายน้ำ:", ["ขวาล่าง (Bottom-Right)", "ซ้ายล่าง (Bottom-Left)", "ตรงกลาง (Center)", "ขวาบน (Top-Right)", "ซ้ายบน (Top-Left)"])
        wm_opacity = st.slider("ความจางของลายน้ำ (Opacity)", 0.1, 1.0, 0.3, 0.05)
        wm_size = st.slider("ขนาดของลายน้ำ (% เทียบกับภาพ)", 5, 50, 20, 5)

    st.header("⚙️ 3. ข้อมูลลิขสิทธิ์และตัวแปลงไฟล์")
    domain_choice = st.selectbox("เลือกร้านค้าของคุณ:", ["rachastainless.com", "coolstain.net", "กำหนดเอง..."])
    if domain_choice == "กำหนดเอง...":
        domain_choice = st.text_input("พิมพ์ชื่อเว็บไซต์ของคุณ:")
        
    cam_choice = st.selectbox("เลือกรุ่นกล้องเพื่อฝังข้อมูล:", list(CAMERA_PROFILES.keys()))
    quality_setting = st.slider("คุณภาพไฟล์ WebP (%)", min_value=10, max_value=100, value=80, step=5)

if api_key:
    genai.configure(api_key=api_key)

# ฟังก์ชันจัดการภาพลายน้ำ
def apply_watermark(base_img, wm_file, position, opacity, size_pct):
    wm = Image.open(wm_file).convert("RGBA")
    base_w, base_h = base_img.size
    new_w = int(base_w * (size_pct / 100))
    new_h = int(wm.height * (new_w / wm.width))
    wm = wm.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    alpha = wm.split()[3]
    alpha = alpha.point(lambda p: int(p * opacity))
    wm.putalpha(alpha)
    
    watermark_layer = Image.new("RGBA", (base_w, base_h), (0, 0, 0, 0))
    
    if position == "ตรงกลาง (Center)":
        pos = ((base_w - new_w) // 2, (base_h - new_h) // 2)
    elif position == "ซ้ายบน (Top-Left)":
        pos = (20, 20)
    elif position == "ขวาบน (Top-Right)":
        pos = (base_w - new_w - 20, 20)
    elif position == "ซ้ายล่าง (Bottom-Left)":
        pos = (20, base_h - new_h - 20)
    else:
        pos = (base_w - new_w - 20, base_h - new_h - 20)
        
    watermark_layer.paste(wm, pos)
    if base_img.mode != "RGBA":
        base_img = base_img.convert("RGBA")
    return Image.alpha_composite(base_img, watermark_layer).convert("RGB")

# ==========================================
# พื้นที่หลัก (Main Area)
# ==========================================
uploaded_files = st.file_uploader("ลากไฟล์รูปภาพสินค้ามาวางที่นี่", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

if not uploaded_files:
    st.session_state.dismissed_files = set()
    st.session_state.ai_results = {}

if uploaded_files:
    active_files = [f for f in uploaded_files if f.name not in st.session_state.dismissed_files]
    
    if active_files:
        st.write("---")
        col_title, col_clear = st.columns([3, 1])
        with col_title:
            st.write("### 📥 ผลลัพธ์พร้อมดาวน์โหลดและปรับแต่งคีย์เวิร์ด")
        with col_clear:
            if st.button("🗑️ เคลียร์ภาพทั้งหมดบนหน้าจอ", use_container_width=True):
                st.session_state.dismissed_files.update([f.name for f in active_files])
                st.rerun()
        
        for i, uploaded_file in enumerate(active_files):
            file_key = uploaded_file.name
            
            # ✨ [แก้ไขบั๊กที่นี่] สร้างตัวแปรตั้งต้นให้พร้อมใช้งานเสมอ ไม่ว่าจะรีเฟรชกี่รอบ
            if "ภาษาไทย" in ai_lang:
                default_filename = "ตู้ซิงค์สแตนเลส-อ่างล้างจาน-304"
                default_desc = "เครื่องครัวสแตนเลสเกรด 304 คุณภาพสูง ทนทาน พื้นผิวสวยงาม พร้อมขาปรับระดับได้"
            else:
                default_filename = "commercial-stainless-steel-sink-cabinet"
                default_desc = "Premium grade 304 stainless steel commercial kitchen equipment with heavy duty adjustable feet"
            
            if file_key not in st.session_state.ai_results:
                st.session_state.ai_results[file_key] = {"filename": default_filename, "desc": default_desc, "analyzed": False}
            
            try:
                orig_img = Image.open(uploaded_file)
                st.write(f"🖼️ **รูปภาพที่ {i+1}: {file_key}**")
                
                col_ui_img, col_ui_edit, col_ui_btn = st.columns([1.5, 3, 1])
                
                with col_ui_img:
                    st.image(orig_img, use_container_width=True)
                
                with col_ui_btn:
                    if st.button("🤖 ให้ AI รีเสิร์จคีย์เวิร์ดจริง", key=f"ai_btn_{i}"):
                        if not api_key:
                            st.warning("⚠️ กรุณากรอก Gemini API Key ที่แถบด้านซ้ายก่อนครับ")
                        else:
                            with st.spinner("AI กำลังวิเคราะห์..."):
                                try:
                                    model = genai.GenerativeModel('gemini-2.5-flash')
                                    if "ภาษาไทย" in ai_lang:
                                        prompt = "คุณคือผู้เชี่ยวชาญด้าน Image SEO ให้วิเคราะห์ภาพสินค้าสแตนเลสนี้ แล้วค้นหาคีย์เวิร์ดภาษาไทยที่มีคนค้นหาจริงบน Google นำคีย์เวิร์ดคำค้นหาหลักมาตั้งชื่อไฟล์แบบเชื่อมด้วยขีด (-) และแต่งประโยคคำอธิบายภาพ SEO ที่มีคำค้นหารอง เช่น อ่างล้างจาน, ถังน้ำแข็ง, ตู้สแตนเลส, ขาปรับระดับ ตอบกลับในรูปแบบนี้เท่านั้น บรรทัดแรก FILENAME: [ชื่อไฟล์ไม่มีนามสกุล] บรรทัดสอง DESCRIPTION: [คำอธิบายภาพ]"
                                    else:
                                        prompt = "You are an Image SEO expert. Analyze this stainless steel product image. Provide a primary high-volume keyword hyphenated for the FILENAME and create a short SEO description with LSI keywords like adjustable feet, hairline finish, ice bin. Reply STRICTLY in this format: Line 1 FILENAME: [hyphenated-name-without-extension] Line 2 DESCRIPTION: [seo-description]"
                                    
                                    response = model.generate_content([prompt, orig_img])
                                    lines = response.text.split('\n')
                                    
                                    # นำค่าตั้งต้นมารอไว้ก่อน เผื่อ AI ตอบไม่ครบ
                                    fname_res = default_filename
                                    desc_res = default_desc
                                    
                                    for line in lines:
                                        if line.startswith("FILENAME:"):
                                            fname_res = line.replace("FILENAME:", "").strip()
                                        elif line.startswith("DESCRIPTION:"):
                                            desc_res = line.replace("DESCRIPTION:", "").strip()
                                            
                                    st.session_state.ai_results[file_key] = {"filename": fname_res, "desc": desc_res, "analyzed": True}
                                    st.rerun()
                                except Exception as ai_err:
                                    st.error(f"ระบบ AI ขัดข้อง: {ai_err}")
                    
                    if st.button("❌ ลบภาพนี้ออก", key=f"del_btn_{i}", use_container_width=True):
                        st.session_state.dismissed_files.add(file_key)
                        st.rerun()
                
                with col_ui_edit:
                    if st.session_state.ai_results[file_key]["analyzed"]:
                        st.success("✨ AI ค้นหาคีย์เวิร์ดจริงเสร็จสมบูรณ์!")
                    else:
                        st.caption("💡 ระบบจำลองข้อมูลตั้งต้นไว้ให้ กดปุ่ม AI เพื่อดึงคีย์เวิร์ดจริงได้เลย")
                        
                    final_fname = st.text_input("📁 แก้ไขชื่อไฟล์สำหรับ SEO:", value=st.session_state.ai_results[file_key]["filename"], key=f"fn_input_{i}")
                    final_desc = st.text_input("📝 แก้ไขรายละเอียดคีย์เวิร์ดฝังหลังภาพ:", value=st.session_state.ai_results[file_key]["desc"], key=f"desc_input_{i}")
                
                proc_img = orig_img
                if watermark_file:
                    proc_img = apply_watermark(proc_img, watermark_file, wm_position, wm_opacity, wm_size)
                
                if proc_img.mode in ("RGBA", "P"):
                    proc_img = proc_img.convert("RGB")
                
                f_val = random.choice([(14, 10), (18, 10), (22, 10), (28, 10), (40, 10), (56, 10), (80, 10)])
                exp_val = random.choice([(1, 60), (1, 125), (1, 160), (1, 250), (1, 500), (1, 1000), (1, 2000)])
                iso_val = random.choice([50, 100, 200, 400, 800, 1600])
                focal_val = random.choice([(13, 1), (24, 1), (35, 1), (50, 1), (85, 1), (120, 1)])
                
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
                        piexif.ExifIFD.Contrast: random.choice([0, 1, 2]),
                        piexif.ExifIFD.Saturation: random.choice([0, 1, 2]),
                        piexif.ExifIFD.Sharpness: random.choice([0, 1, 2]),
                        piexif.ExifIFD.WhiteBalance: random.choice([0, 1]),
                        piexif.ExifIFD.MeteringMode: random.choice([2, 3, 5]),
                        piexif.ExifIFD.ExposureProgram: random.choice([2, 3, 4]),
                        piexif.ExifIFD.Flash: random.choice([0, 16, 24]),
                        piexif.ExifIFD.DigitalZoomRatio: random.choice([(10, 10), (12, 10)]),
                    }
                }
                
                if final_desc.strip():
                    windows_title = final_desc.encode('utf-16le')
                    exif_dict["0th"][piexif.ImageIFD.ImageDescription] = final_desc.encode('utf-8')
                    exif_dict["0th"][piexif.ImageIFD.XPTitle] = windows_title
                    exif_dict["0th"][piexif.ImageIFD.XPComment] = windows_title
                
                exif_bytes = piexif.dump(exif_dict)
                img_buffer = io.BytesIO()
                proc_img.save(img_buffer, format="webp", quality=quality_setting, method=6, exif=exif_bytes)
                
                clean_download_name = final_fname.strip().replace(" ", "-") + ".webp"
                
                with col_ui_btn:
                    st.download_button(
                        label=f"⬇️ โหลดภาพ WebP",
                        data=img_buffer.getvalue(),
                        file_name=clean_download_name,
                        mime="image/webp",
                        key=f"dl_btn_real_{i}",
                        use_container_width=True
                    )
                    st.caption(f"📦 ขนาด: {len(img_buffer.getvalue()) / 1024:.1f} KB")
                
                st.write("---")
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดกับไฟล์ {file_key}: {e}")
                
    else:
        st.info("ไม่มีรูปภาพรอประมวลผลบนหน้าจอแล้วครับ สามารถลากไฟล์ภาพชุดใหม่ลงมาได้เลย")
