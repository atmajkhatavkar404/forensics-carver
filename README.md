# Advanced Signature-Based File Recovery and File Carving System

A professional digital forensics tool for recovering deleted files from raw disk images (.img, .dd, .bin, .raw) using signature-based carving techniques.

## Features
- **Signature-Based Carving**: Supports 20+ file types (Images, Documents, Archives, Media).
- **Validation Layer**: Automatically validates recovered files for integrity and corruption.
- **Modern GUI**: Built with CustomTkinter for a premium dark forensic theme.
- **Streaming Scan**: Optimized for large disk images (>100GB) with chunk-based processing.
- **Threaded Execution**: Non-blocking UI during intense scanning operations.
- **Detailed Reporting**: Exports CSV, JSON, and TXT forensic logs.

## Supported File Types
- **Images**: JPG, PNG, GIF, BMP
- **Documents**: PDF, DOCX, XLSX, PPTX, DOC, XLS, PPT, TXT, RTF
- **Archives**: ZIP, RAR, 7Z
- **Media**: MP4, AVI, MP3, WAV

## Installation
1. Install Python 3.11+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. *Linux Note*: You may need to install `libmagic1` (e.g., `sudo apt-get install libmagic1`).
4. *Windows Note*: The `python-magic-bin` package is included in requirements for Windows compatibility.

## Usage
1. Launch the application:
   ```bash
   python main.py
   ```
2. Select the target disk image file.
3. Select an output folder for recovered files.
4. Click **Start Scan**.
5. Monitor progress and view recovered files in the dashboard.

## Forensic Methodology
The carver scans the image bit-by-bit (in sectors) for known file magic headers. Once a header is identified, it searches for the corresponding footer while respecting maximum size heuristics. Every carved file undergoes a validation check (e.g., CRC, structure parsing) to ensure it is not just random data.

## Project Structure
- `core/`: Heavy lifting backend for signatures, carving, and validation.
- `gui/`: CustomTkinter interface components.
- `recovered/`: Default directory for carved files.
- `reports/`: Generated forensic metadata and logs.
