import streamlit as st
import cv2
import numpy as np
import json
import os
import sys

# Ensure repo is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.pipeline import PharmaPipeline

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Pharma-Context Engine",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main {
        background-color: #fcefe9; /* Very light medical feel */
    }
    .stApp > header {
        background-color: transparent;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    h1, h2, h3 {
        color: #0d47a1; /* Medical Dark Blue */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .verified-badge {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        border: 1px solid #c8e6c9;
    }
    .warning-badge {
        background-color: #ffebee;
        color: #c62828;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        border: 1px solid #ffcdd2;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3004/3004458.png", width=80)
    st.title("Settings")
    st.info("System Ready")
    
    show_raw_ocr = st.checkbox("Show Raw OCR Data", value=False)
    enable_enrichment = st.checkbox("Enable FDA Enrichment", value=True)
    
    st.markdown("---")
    st.markdown("### Model Status")
    st.success("✅ Neural Network Active")
    st.caption("Model: YOLOv8-FineTuned (v1.0)")
    
    st.markdown("---")
    st.button("Reset Application")

# --- MAIN HEADER ---
col1, col2 = st.columns([1, 4])
with col1:
    st.empty() # Spacer
with col2:
    st.title("Intelligent Pharma-Context Engine")
    st.markdown("#### *AI-Powered Prescriptive Intelligence & Verification*")

# --- LOAD PIPELINE ---
@st.cache_resource
def load_pipeline():
    return PharmaPipeline()

pipeline = load_pipeline()

# --- MAIN WORKFLOW ---
st.markdown("---")
uploaded_file = st.file_uploader("📂 Upload Medicine Image (Bottle or Label)", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Read Image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    
    # Save temp for pipeline
    temp_path = "temp_upload.jpg"
    cv2.imwrite(temp_path, image)
    
    # --- TWO COLUMN LAYOUT ---
    left_col, right_col = st.columns([1, 1.2])
    
    # --- ANALYSIS WITH SPINNER ---
    with st.spinner("🔍 Scanning Image... Detecting Regions... Verifying against FDA Database..."):
        try:
            result = pipeline.process_image(temp_path)
            
            # --- DRAW BOUNDING BOXES ---
            annotated_img = image.copy()
            regions = result['fields'].get('regions', [])
            
            # Draw boxes
            if regions:
                for region in regions:
                    # coords is [x1, y1, x2, y2]
                    coords = region['coords']
                    label_text = region['label']
                    if label_text == '0':
                         label_text = "Medicine Bottle"
                    
                    label_display = f"{label_text} {region['confidence']:.2f}"
                    cv2.rectangle(annotated_img, (coords[0], coords[1]), (coords[2], coords[3]), (0, 0, 255), 3)
                    cv2.putText(annotated_img, label_display, (coords[0], coords[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            
            # --- LEFT COLUMN: IMAGE ---
            with left_col:
                st.subheader("📸 Detected Object")
                # Convert BGR to RGB for Streamlit
                st_img = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
                st.image(image, caption="Uploaded Image", use_container_width=True)
                
                if regions:
                    st.success(f"Detected {len(regions)} Region(s) of Interest")
                else:
                    st.warning("No medicine bottle regions detected via YOLO.")

            # --- RIGHT COLUMN: RESULTS ---
            with right_col:
                st.subheader("📋 Analysis Report")
                
                # Top Card: Drug Name & Verification
                drug_name = result['fields']['drug_name']['value']
                is_verified = result['verification']['matched_source'] is not None
                
                # HTML Badge
                if is_verified:
                    badge_html = f"""
                    <div style="background-color: #f0f4ff; padding: 20px; border-radius: 10px; border-left: 5px solid #29b6f6;">
                        <span style="color: #555; font-size: 0.9em;">IDENTIFIED DRUG</span><br>
                        <span style="color: #0d47a1; font-size: 2.2em; font-weight: bold;">{drug_name}</span><br>
                        <span class="verified-badge">✅ FDA VERIFIED</span>
                    </div>
                    """
                else:
                    badge_html = f"""
                    <div style="background-color: #fff3e0; padding: 20px; border-radius: 10px; border-left: 5px solid #ff9800;">
                        <span style="color: #555; font-size: 0.9em;">EXTRACTED TEXT</span><br>
                        <span style="color: #e65100; font-size: 2.2em; font-weight: bold;">{drug_name}</span><br>
                        <span class="warning-badge">⚠️ UNVERIFIED</span>
                    </div>
                    """
                st.markdown(badge_html, unsafe_allow_html=True)
                
                st.markdown("###") # Spacer

                # Tabs
                tab_label, tab_clinical, tab_tech, tab_raw = st.tabs(["🧪 Extracted Entities", "💊 Clinical Context", "🔍 Technical Details", "📊 Raw Data"])
                
                with tab_label:
                    meta = result['fields'].get('meta', {})
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Manufacturer:**")
                        mfg = meta.get('manufacturer')
                        if mfg:
                            st.success(mfg)
                        else:
                            st.warning("Not Detected")
                            
                        st.markdown("**Dosage / Strength:**")
                        dosage = meta.get('dosage')
                        st.info(dosage if dosage else "Not Detected")

                    with c2:
                        st.markdown("**Quantity/Form:**")
                        qty = meta.get('quantity')
                        st.info(qty if qty else "Not Detected")
                        
                        st.markdown("**Presumed Composition:**")
                        # MVP: Compose name + dosage
                        if drug_name and dosage:
                            st.write(f"{drug_name} ({dosage})")
                        else:
                            st.write("Unknown")

                with tab_clinical:
                    enrich = result['enrichment']
                    if enrich:
                        st.markdown(f"**Storage Instructions:**")
                        st.info(enrich.get('storage', 'No specific storage info found.'))
                        
                        st.markdown(f"**Safety Warnings:**")
                        st.error(enrich.get('warnings', 'No major warnings found in index.'))
                        
                        with st.expander("Common Side Effects"):
                            st.write(enrich.get('side_effects', 'Data not available.'))
                    else:
                        st.info("Clinical enrichment requires a verified drug match.")

                with tab_tech:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("OCR Confidence", f"{result['fields']['drug_name']['confidence']*100:.1f}%")
                    with col_b:
                        st.metric("Barcode Type", "QR/DataMatrix" if result['fields']['barcode']['value'] else "None")
                    
                    st.write(f"**RxNorm CUI:** `{result['verification']['rxcui'] or 'N/A'}`")
                    st.write(f"**Match Score:** {result['verification']['match_score']}/100")

                with tab_raw:
                    st.json(result)

        except Exception as e:
            st.error("An unexpected error occurred during processing.")
            st.code(e)
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)

else:
    # Empty State - Show placeholder or instructions
    st.info("👆 Please upload an image to begin the analysis.")
