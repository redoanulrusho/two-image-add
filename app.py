import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="Background Removal ROI Merger", page_icon="🖼️", layout="wide")

st.title("🖼️ Remove Background & Merge Images (Interactive)")

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Tools & Settings")

# Upload images
file1 = st.sidebar.file_uploader("Upload First Image (Background)", type=["jpg", "png", "jpeg"])
file2 = st.sidebar.file_uploader("Upload Second Image (Object with background)", type=["jpg", "png", "jpeg"])

if file1 and file2:
    # Read images
    img1 = np.array(Image.open(file1).convert("RGB"))
    img2 = np.array(Image.open(file2).convert("RGB"))

    # Resize object
    scale_percent = st.sidebar.slider("Scale Object (%)", 10, 200, 100)
    width = int(img2.shape[1] * scale_percent / 100)
    height = int(img2.shape[0] * scale_percent / 100)
    img2_resized = cv2.resize(img2, (width, height))

    # Position sliders
    x_offset = st.sidebar.slider("X Position", 0, max(1, img1.shape[1] - width), 0)
    y_offset = st.sidebar.slider("Y Position", 0, max(1, img1.shape[0] - height), 0)

    # HSV sliders for background removal
    st.sidebar.subheader("🎛 Background Removal")
    h_min = st.sidebar.slider("Hue Min", 0, 179, 0)
    h_max = st.sidebar.slider("Hue Max", 0, 179, 179)
    s_min = st.sidebar.slider("Saturation Min", 0, 255, 0)
    s_max = st.sidebar.slider("Saturation Max", 0, 255, 255)
    v_min = st.sidebar.slider("Value Min", 0, 255, 0)
    v_max = st.sidebar.slider("Value Max", 0, 255, 255)

    # Convert to HSV and create mask
    hsv = cv2.cvtColor(img2_resized, cv2.COLOR_RGB2HSV)
    lower_color = np.array([h_min, s_min, v_min], dtype=np.uint8)
    upper_color = np.array([h_max, s_max, v_max], dtype=np.uint8)

    mask = cv2.inRange(hsv, lower_color, upper_color)
    mask_inv = cv2.bitwise_not(mask)

    # Extract object without background
    img2_fg = cv2.bitwise_and(img2_resized, img2_resized, mask=mask_inv)

    # --- Live Mask Preview ---
    st.subheader("🎭 Mask Preview")
    st.image(mask_inv, caption="Mask (White = Object, Black = Removed Background)", use_column_width=True)

    # Prepare ROI
    rows, cols = img2_fg.shape[:2]
    roi = img1[y_offset:y_offset+rows, x_offset:x_offset+cols]

    # Remove background from ROI
    img1_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)

    # Merge object onto background
    dst = cv2.add(img1_bg, img2_fg)
    img1[y_offset:y_offset+rows, x_offset:x_offset+cols] = dst

    # --- Final Preview ---
    st.subheader("🔍 Final Image Preview")
    st.image(img1, caption="Merged Image", use_column_width=True)

    # Download Button
    result_img = Image.fromarray(img1)
    buf = io.BytesIO()
    result_img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="⬇️ Download Final Image",
        data=byte_im,
        file_name="merged_no_bg.png",
        mime="image/png"
    )
else:
    st.info("⬅️ Please upload both images from the sidebar to begin.")
