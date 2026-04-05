import os

def create_demo_image(filename, size_mb=1):
    """
    Creates a dummy disk image with embedded file signatures.
    """
    print(f"Creating {filename}...")
    # Create a buffer filled with null bytes (representing empty disk space)
    size_bytes = size_mb * 1024 * 1024
    data = bytearray(size_bytes)
    
    # Signatures to embed
    # 1. PNG at offset 1024
    png_header = b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"
    png_body = b"This is a fake PNG content for demo purposes."
    png_footer = b"\x49\x45\x4E\x44\xAE\x42\x60\x82"
    png_data = png_header + png_body + png_footer
    offset_png = 1024
    data[offset_png:offset_png+len(png_data)] = png_data
    
    # 2. JPEG at offset 4096
    jpg_header = b"\xFF\xD8\xFF"
    jpg_body = b"This is a fake JPEG content for demo purposes."
    jpg_footer = b"\xFF\xD9"
    jpg_data = jpg_header + jpg_body + jpg_footer
    offset_jpg = 4096
    data[offset_jpg:offset_jpg+len(jpg_data)] = jpg_data
    
    # 3. PDF at offset 8192
    pdf_header = b"\x25\x50\x44\x46"
    pdf_body = b"This is a fake PDF content for demo purposes."
    pdf_footer = b"\x25\x25\x45\x4F\x46"
    pdf_data = pdf_header + pdf_body + pdf_footer
    offset_pdf = 8192
    data[offset_pdf:offset_pdf+len(pdf_data)] = pdf_data

    # Write to file
    with open(filename, "wb") as f:
        f.write(data)
    print(f"Successfully created {filename} at {os.path.abspath(filename)}")

if __name__ == "__main__":
    target_dir = "test_images"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    create_demo_image(os.path.join(target_dir, "demo_disk.img"))
    create_demo_image(os.path.join(target_dir, "forensic_dump.dd"))
