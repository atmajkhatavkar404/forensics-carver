import customtkinter as ctk
import os
import io
from PIL import Image
from typing import Optional

class PreviewPanel(ctk.CTkFrame):
    """
    Shows a preview of the selected recovered file.
    """
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.label = ctk.CTkLabel(self, text="File Preview", font=ctk.CTkFont(size=16, weight="bold"))
        self.label.pack(pady=10)
        
        self.preview_image_label = ctk.CTkLabel(self, text="Select a file to preview")
        self.preview_image_label.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.hex_text = ctk.CTkTextbox(self, height=200, state="disabled")
        self.hex_text.pack(expand=True, fill="both", padx=20, pady=10)
        
        self.metadata_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12))
        self.metadata_label.pack(pady=10)

    def show_preview(self, file_path: str, file_info: dict):
        """Shows image or hex preview based on file type."""
        # Clear previous
        self.preview_image_label.configure(image=None, text="")
        self.hex_text.configure(state="normal")
        self.hex_text.delete("0.0", "end")
        
        ext = file_info.get("ext", "").lower()
        
        # Show Metadata
        metadata = f"Name: {file_info['name']}\n"
        metadata += f"Size: {file_info['size']} bytes\n"
        metadata += f"Status: {file_info['status']}\n"
        metadata += f"Confidence: {file_info['confidence']}\n"
        metadata += f"Hash: {file_info['hash'][:32]}..."
        self.metadata_label.configure(text=metadata)
        
        # Image Preview
        if ext in ["jpg", "jpeg", "png", "gif", "bmp"]:
            try:
                img = Image.open(file_path)
                # Resize for preview wrapper
                width, height = img.size
                ratio = min(300/width, 300/height)
                new_size = (int(width * ratio), int(height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=new_size)
                self.preview_image_label.configure(image=ctk_img, text="")
            except Exception as e:
                self.preview_image_label.configure(text=f"Error loading image: {str(e)}")
        else:
            self.preview_image_label.configure(text=f"No preview available for {ext.upper()}")
            
        # Hex Preview
        try:
            with open(file_path, "rb") as f:
                header = f.read(256)
                hex_dump = ""
                for i in range(0, len(header), 16):
                    chunk = header[i:i+16]
                    hex_str = " ".join([f"{b:02X}" for b in chunk])
                    ascii_str = "".join([chr(b) if 32 <= b <= 126 else "." for b in chunk])
                    hex_dump += f"{i:04X}  {hex_str:<48}  {ascii_str}\n"
                
                self.hex_text.insert("0.0", hex_dump)
        except Exception as e:
            self.hex_text.insert("0.0", f"Error reading hex: {str(e)}")
            
        self.hex_text.configure(state="disabled")
