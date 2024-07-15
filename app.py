import streamlit as st
import requests
import qrcode
import os
from zipfile import ZipFile

# Fetch a useless fact with error handling
fact_url = "https://uselessfacts.jsph.pl/random.json?language=en"
try:
    response = requests.get(fact_url)
    response.raise_for_status()
    fact = response.json().get("text", "No fact available today!")
except requests.exceptions.RequestException as e:
    fact = f"Failed to fetch useless fact: {e}"

st.set_page_config(layout="wide")

st.sidebar.title(f":) useless fact of the day: {fact}")

voucher_codes = st.file_uploader("Upload Voucher file TXT", type="txt")

if voucher_codes is not None:
    # Create images directory if it doesn't exist
    os.makedirs("VoucherCodes", exist_ok=True)
    
    # Initialize a list to keep track of generated image files
    img_files = []

    with voucher_codes:
        name = 1
        for line in voucher_codes:
            line = line.strip()  # Remove any trailing newlines or spaces
            if line:
                img = qrcode.make(line)
                img_path = f"VoucherCodes/voucher_{name}.png"
                img.save(img_path)
                img_files.append(img_path)
                name += 1

    # Create a ZIP file containing all the QR code images
    zip_file_path = "qr_codes.zip"
    with ZipFile(zip_file_path, 'w') as zip_file:
        for img_file in img_files:
            zip_file.write(img_file)

    # Provide a download button for the ZIP file
    with open(zip_file_path, "rb") as zip_file:
        btn = st.download_button(
            label="Download QR Codes ZIP FILE",
            data=zip_file,
            file_name="qr_codes.zip",
            mime="application/zip"
        )