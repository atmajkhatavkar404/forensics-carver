import os
import threading
import time
from typing import Callable, Optional, List, Dict, Any
from .signatures import FILE_SIGNATURES, get_signature_by_header
from .validator import FileValidator
from .utils import calculate_checksum, setup_logging, format_bytes, get_sector_offset

class ForensicCarver:
    """
    Main file carving engine.
    """
    
    def __init__(self, 
                 image_path: str, 
                 output_dir: str, 
                 chunk_size: int = 1024 * 1024, # 1MB
                 sector_size: int = 512,
                 update_callback: Optional[Callable] = None,
                 log_callback: Optional[Callable] = None):
        self.image_path = image_path
        self.output_dir = output_dir
        self.chunk_size = chunk_size
        self.sector_size = sector_size
        self.update_callback = update_callback # Callback for UI progress
        self.log_callback = log_callback # Callback for live log in UI
        
        self.logger = setup_logging()
        self.is_running = False
        self.total_size = os.path.getsize(image_path)
        self.recovered_files: List[Dict[str, Any]] = []
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _log(self, message: str, level: str = "info"):
        """Logs message to file and UI."""
        if level == "info":
            self.logger.info(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "debug":
            self.logger.debug(message)
            
        if self.log_callback:
            self.log_callback(f"[{level.upper()}] {message}")

    def stop(self):
        self.is_running = False
        self._log("Carving process stopped by user.")

    def start(self):
        """Starts the carving process in a separate thread."""
        self.is_running = True
        thread = threading.Thread(target=self._run_carving_loop)
        thread.daemon = True
        thread.start()
        return thread

    def _run_carving_loop(self):
        start_time = time.time()
        byte_offset = 0
        file_count = 0
        
        try:
            with open(self.image_path, "rb") as disk:
                while self.is_running and byte_offset < self.total_size:
                    # Sector aligned read
                    disk.seek(byte_offset)
                    data = disk.read(self.chunk_size)
                    if not data:
                        break
                    
                    # Search for headers within the chunk
                    self._scan_data_for_headers(data, byte_offset, disk)
                    
                    byte_offset += len(data)
                    
                    # Update progress
                    percent = (byte_offset / self.total_size) * 100
                    if self.update_callback:
                        self.update_callback(percent, len(self.recovered_files))
            
            total_time = time.time() - start_time
            self._log(f"Carving complete. Found {len(self.recovered_files)} files in {total_time:.2f}s.")
        except Exception as e:
            self._log(f"Critical error during carving: {str(e)}", "error")
        finally:
            self.is_running = False

    def _scan_data_for_headers(self, data: bytes, chunk_offset: int, disk_file):
        """Scans a chunk of data for magic headers."""
        # Forensics: we should ideally check every byte or stay sector-aligned
        # For performance, we'll scan byte-by-byte within the chunk
        for ext, sig in FILE_SIGNATURES.items():
            header = sig["header"]
            header_pos = data.find(header)
            
            while header_pos != -1:
                absolute_offset = chunk_offset + header_pos
                self._handle_header_found(ext, sig, absolute_offset, disk_file)
                
                # Look for more headers of the same type in the same chunk
                header_pos = data.find(header, header_pos + 1)

    def _handle_header_found(self, ext: str, sig: Dict, offset: int, disk_file):
        """Handles a found header: looks for footer and extracts."""
        self._log(f"Header found: {ext.upper()} at offset {offset} (Sector: {get_sector_offset(offset)})")
        
        footer = sig.get("footer")
        max_size = sig.get("max_size", 10 * 1024 * 1024)
        
        file_data = b""
        disk_file.seek(offset)
        
        # Read max_size to look for footer
        try:
            buffer = disk_file.read(max_size)
            if footer:
                footer_pos = buffer.find(footer)
                if footer_pos != -1:
                    actual_size = footer_pos + len(footer)
                    file_data = buffer[:actual_size]
                else:
                    # Footer not found? Maybe corrupted or partial
                    self._log(f"Footer not found for {ext} at {offset}. Using heuristic size.", "debug")
                    file_data = buffer # Recover what we can
            else:
                # No footer signature (e.g. BMP)
                file_data = buffer
                
            if not file_data:
                return

            # Validate the data
            status, score = FileValidator.validate(file_data, ext)
            
            # Save the file
            filename = f"recovered_{offset}_{ext}.{ext}"
            file_path = os.path.join(self.output_dir, filename)
            
            with open(file_path, "wb") as f:
                f.write(file_data)
            
            # Calculate SHA256
            final_hash = calculate_checksum(file_data)
            
            file_info = {
                "name": filename,
                "ext": ext,
                "offset": offset,
                "size": len(file_data),
                "status": status,
                "confidence": score,
                "hash": final_hash,
                "path": file_path
            }
            
            self.recovered_files.append(file_info)
            self._log(f"Recovered: {filename} ({format_bytes(len(file_data))}) - Status: {status}")
            
        except Exception as e:
            self._log(f"Error extracting {ext} at {offset}: {str(e)}", "error")
