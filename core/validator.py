import io
import zipfile
import olefile
from PIL import Image as PILImage
from typing import Optional, Tuple

class FileValidator:
    """
    Validates recovered file segments to determine if they are corrupt, partial, or valid.
    """
    
    @staticmethod
    def validate(data: bytes, extension: str) -> Tuple[str, float]:
        """
        Validates the file data based on extension.
        Returns: (status, confidence_score)
        """
        extension = extension.lower().strip('.')
        
        if extension in ["jpg", "jpeg", "png", "gif", "bmp"]:
            return FileValidator._validate_image(data)
        elif extension in ["docx", "xlsx", "pptx", "zip"]:
            return FileValidator._validate_zip(data)
        elif extension in ["pdf"]:
            return FileValidator._validate_pdf(data)
        elif extension in ["doc", "xls", "ppt"]:
            return FileValidator._validate_ole(data)
        elif extension in ["txt"]:
            return FileValidator._validate_txt(data)
        
        # Default for unknown/unhandled types
        return "partial", 0.5

    @staticmethod
    def _validate_image(data: bytes) -> Tuple[str, float]:
        try:
            img = PILImage.open(io.BytesIO(data))
            img.verify()
            return "valid", 1.0
        except Exception:
            return "corrupted", 0.1

    @staticmethod
    def _validate_zip(data: bytes) -> Tuple[str, float]:
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                ret = zf.testzip()
                if ret is None:
                    return "valid", 1.0
                else:
                    return "partial", 0.6
        except Exception:
            return "corrupted", 0.1

    @staticmethod
    def _validate_pdf(data: bytes) -> Tuple[str, float]:
        if data.startswith(b"%PDF") and (b"%%EOF" in data):
            # Check structure minimally
            if len(data) > 100:
                return "valid", 0.95
            return "partial", 0.5
        return "corrupted", 0.1

    @staticmethod
    def _validate_ole(data: bytes) -> Tuple[str, float]:
        try:
            if olefile.isOleFile(io.BytesIO(data)):
                return "valid", 0.9
            return "partial", 0.4
        except Exception:
            return "corrupted", 0.1

    @staticmethod
    def _validate_txt(data: bytes) -> Tuple[str, float]:
        try:
            data.decode('utf-8')
            return "valid", 1.0
        except UnicodeDecodeError:
            try:
                data.decode('latin-1')
                return "valid", 0.8
            except Exception:
                return "corrupted", 0.2
