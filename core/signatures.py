"""
Signature database for file headers and footers.
"""

from typing import Dict, List, Optional, Union

# Signature definitions (Hexadecimal)
# header: Magic bytes for the start of the file
# footer: Magic bytes for the end of the file (optional)
# max_size: Maximum expected size if no footer is found (in bytes)
# confidence: Initial confidence level for the signature

FILE_SIGNATURES = {
    "jpg": {
        "header": b"\xFF\xD8\xFF",
        "footer": b"\xFF\xD9",
        "max_size": 20 * 1024 * 1024,  # 20 MB
        "description": "JPEG Image",
        "category": "Images"
    },
    "png": {
        "header": b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A",
        "footer": b"\x49\x45\x4E\x44\xAE\x42\x60\x82",
        "max_size": 25 * 1024 * 1024,  # 25 MB
        "description": "Portable Network Graphics",
        "category": "Images"
    },
    "gif": {
        "header": b"\x47\x49\x46\x38", # GIF87a or GIF89a
        "footer": b"\x00\x3B",
        "max_size": 10 * 1024 * 1024,  # 10 MB
        "description": "Graphics Interchange Format",
        "category": "Images"
    },
    "bmp": {
        "header": b"\x42\x4D", # BM
        "footer": None,
        "max_size": 15 * 1024 * 1024,  # 15 MB
        "description": "Bitmap Image",
        "category": "Images"
    },
    "pdf": {
        "header": b"\x25\x50\x44\x46", # %PDF
        "footer": b"\x25\x25\x45\x4F\x46", # %%EOF
        "max_size": 100 * 1024 * 1024, # 100 MB
        "description": "Portable Document Format",
        "category": "Documents"
    },
    "docx": {
        "header": b"\x50\x4B\x03\x04", # PK..
        "footer": b"\x50\x4B\x05\x06", # PK (End of Central Directory)
        "max_size": 50 * 1024 * 1024,  # 50 MB
        "description": "Microsoft Word Document (XML)",
        "category": "Documents"
    },
    "xlsx": {
        "header": b"\x50\x4B\x03\x04",
        "footer": b"\x50\x4B\x05\x06",
        "max_size": 50 * 1024 * 1024,
        "description": "Microsoft Excel calculation (XML)",
        "category": "Documents"
    },
    "pptx": {
        "header": b"\x50\x4B\x03\x04",
        "footer": b"\x50\x4B\x05\x06",
        "max_size": 50 * 1024 * 1024,
        "description": "Microsoft PowerPoint Presentation (XML)",
        "category": "Documents"
    },
    "doc": {
        "header": b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1", # OLE CF
        "footer": None,
        "max_size": 50 * 1024 * 1024,
        "description": "Microsoft Word Document (Legacy)",
        "category": "Documents"
    },
    "zip": {
        "header": b"\x50\x4B\x03\x04",
        "footer": b"\x50\x4B\x05\x06",
        "max_size": 500 * 1024 * 1024, # 500 MB
        "description": "ZIP Archive",
        "category": "Archives"
    },
    "rar": {
        "header": b"\x52\x61\x72\x21\x1A\x07", # Rar!
        "footer": None,
        "max_size": 500 * 1024 * 1024,
        "description": "RAR Archive",
        "category": "Archives"
    },
    "7z": {
        "header": b"\x37\x7A\xBC\xAF\x27\x1C", # 7z
        "footer": None,
        "max_size": 500 * 1024 * 1024,
        "description": "7-Zip Archive",
        "category": "Archives"
    },
    "mp4": {
        "header": b"ftyp", # Offset by 4 usually, but we'll scan for it
        "footer": None,
        "max_size": 1024 * 1024 * 1024, # 1 GB
        "description": "MPEG-4 Video",
        "category": "Media"
    },
    "mp3": {
        "header": b"\x49\x44\x33", # ID3
        "footer": None,
        "max_size": 50 * 1024 * 1024,
        "description": "MP3 Audio",
        "category": "Media"
    },
    "wav": {
        "header": b"\x52\x49\x46\x46", # RIFF
        "footer": None,
        "max_size": 100 * 1024 * 1024,
        "description": "WAVE Audio",
        "category": "Media"
    }
}

def get_signature_by_header(header_start: bytes) -> Optional[str]:
    """Returns the file extension if the header_start matches any known signature."""
    for ext, sig in FILE_SIGNATURES.items():
        if header_start.startswith(sig["header"]):
            return ext
    return None
