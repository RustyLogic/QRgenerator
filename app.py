import streamlit as st
import requests
import qrcode
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
from zipfile import ZipFile
import io

st.set_page_config(layout="wide")

# Upload voucher file
voucher_codes = st.file_uploader("Upload Voucher file TXT", type="txt")

# Input description text
description_text = st.text_input("Enter description text for the QR code images:")

if voucher_codes is not None:
    # Create images directory if it doesn't exist
    os.makedirs("VoucherCodes", exist_ok=True)
    
    # Initialize a list to keep track of generated image files
    img_files = []

    # URL of the Roboto Regular TTF file hosted on CDN
    font_url = "https://cdn.jsdelivr.net/npm/roboto-font@0.1.0/fonts/Roboto_slab/robotoslab-regular-webfont.ttf"

    # Fetch the font file from the URL
    response = requests.get(font_url)
    response.raise_for_status()  # Ensure the request was successful

    # Load the font into PIL using a BytesIO stream
    font_size = 24  # Adjust the size as needed
    font = ImageFont.truetype(io.BytesIO(response.content), font_size)

    with voucher_codes:
        name = 1
        for line in voucher_codes:
            line = line.strip()  # Remove any trailing newlines or spaces
            if line:
                # Create QR code
                qr_img = qrcode.make(line)
                qr_width, qr_height = qr_img.size

                # Wrap the description text to fit within the image width
                max_width = 24  # Number of characters per line, adjust as needed
                wrapped_description = textwrap.fill(description_text, width=max_width)

                # Measure the description text height for each line
                desc_lines = wrapped_description.split('\n')
                desc_height = sum(font.getbbox(line)[3] - font.getbbox(line)[1] for line in desc_lines)
                
                # Measure the voucher code text height
                code_bbox = font.getbbox(line)
                code_height = code_bbox[3] - code_bbox[1]

                # Calculate the vertical padding between the QR code and the text
                padding = 20
                total_height = qr_height + desc_height + code_height + (3 * padding)

                # Create a new blank image with extra space for text
                img = Image.new("RGB", (qr_width, total_height), "white")
                draw = ImageDraw.Draw(img)

                # Add wrapped description text at the top
                y_text = padding
                for desc_line in desc_lines:
                    desc_width = draw.textbbox((0, 0), desc_line, font=font)[2]
                    draw.text(((qr_width - desc_width) / 2, y_text), desc_line, fill="black", font=font)
                    y_text += font.getbbox(desc_line)[3] - font.getbbox(desc_line)[1]

                qr_img = qr_img.convert("RGB")  # Convert QR code to RGB mode
                # Paste the QR code into the blank image, centered vertically
                img.paste(qr_img, (0, y_text + padding // 2))

                # Add voucher code at the bottom
                y_text += qr_height + padding
                code_width = draw.textbbox((0, 0), line, font=font)[2]
                draw.text(((qr_width - code_width) / 2, y_text), line, fill="black", font=font)

                # Save the image
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
