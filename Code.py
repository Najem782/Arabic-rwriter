import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image, ImageEnhance, ImageOps
import io

st.set_page_config(page_title="مُحسِّن طباعة الكتب", layout="centered")

st.title("🖨️ Arabic Book Print-Quality Enhancer")
st.write("قم برفع ملف الـ PDF الخاص بك لتنظيف الصفحات وتغميق الخط لتسهيل القراءة بعد الطباعة.")

# File Uploader
uploaded_file = st.file_uploader("Upload your Arabic PDF book", type=["pdf"])

if uploaded_file is not None:
    # Let user preview and select a few pages first to test the quality
    st.sidebar.subheader("🎛️ Settings / الإعدادات")
    
    # 1. Text Darkening Control
    contrast_factor = st.sidebar.slider("Text Sharpness / حدة الخط وجلاءه", 1.0, 4.0, 2.5, step=0.5)
    
    # 2. Page Range Selector
    pdf_bytes = uploaded_file.read()
    
    if st.button("✨ Improve & Prepare for Printing"):
        with st.spinner("Processing document pages... This might take a minute."):
            
            # Convert PDF pages to PIL Images
            # Note: For Streamlit Cloud, processing 1-10 pages at a time prevents memory crashes
            pages = convert_from_bytes(pdf_bytes, dpi=150)
            
            processed_pages = []
            
            progress_bar = st.progress(0)
            
            for idx, page in enumerate(pages):
                # Step A: Convert page to Grayscale (removes yellow/gray scanner tints)
                gray_page = ImageOps.grayscale(page)
                
                # Step B: Drastically improve contrast to force faded text into crisp black
                enhancer = ImageEnhance.Contrast(gray_page)
                enhanced_page = enhancer.enhance(contrast_factor)
                
                # Step C: Add a uniform white margin layout for safe paper binding/stapling
                # Adds a 40-pixel white border around the entire page
                padded_page = ImageOps.expand(enhanced_page, border=40, fill="white")
                
                # Convert back to RGB format required for saving to PDF
                processed_pages.append(padded_page.convert('RGB'))
                
                # Update progress bar
                progress_bar.progress((idx + 1) / len(pages))
            
            # Save the processed image pages back into a clean PDF memory buffer
            output_pdf_buffer = io.BytesIO()
            if processed_pages:
                processed_pages[0].save(
                    output_pdf_buffer,
                    format="PDF",
                    save_all=True,
                    append_images=processed_pages[1:]
                )
                output_pdf_buffer.seek(0)
                
                st.success("🎉 Your print-optimized book is ready!")
                
                # Download Button for the newly generated clean PDF
                st.download_button(
                    label="📥 Download Print-Ready PDF / تحميل الملف للطباعة",
                    data=output_pdf_buffer,
                    file_name="print_optimized_book.pdf",
                    mime="application/pdf"
                )
