import csv
import json
import os
import datetime
from typing import List, Dict, Any

class ReportGenerator:
    """
    Generates forensic reports for recovered files.
    """
    
    @staticmethod
    def generate_all(recovered_files: List[Dict[str, Any]], report_dir: str = "reports"):
        """Generates CSV, JSON, and TXT reports."""
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        ReportGenerator._generate_csv(recovered_files, os.path.join(report_dir, f"report_{timestamp}.csv"))
        ReportGenerator._generate_json(recovered_files, os.path.join(report_dir, f"report_{timestamp}.json"))
        ReportGenerator._generate_txt(recovered_files, os.path.join(report_dir, f"report_{timestamp}.txt"))

    @staticmethod
    def _generate_csv(recovered_files: List[Dict[str, Any]], file_path: str):
        if not recovered_files:
            return
            
        keys = recovered_files[0].keys()
        with open(file_path, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(recovered_files)

    @staticmethod
    def _generate_json(recovered_files: List[Dict[str, Any]], file_path: str):
        with open(file_path, 'w') as f:
            json.dump(recovered_files, f, indent=4)

    @staticmethod
    def _generate_txt(recovered_files: List[Dict[str, Any]], file_path: str):
        with open(file_path, 'w') as f:
            f.write("FORENSIC FILE RECOVERY LOG\n")
            f.write("==========================\n")
            f.write(f"Timestamp: {datetime.datetime.now()}\n")
            f.write(f"Total Files Recovered: {len(recovered_files)}\n\n")
            
            for file in recovered_files:
                f.write(f"Filename: {file['name']}\n")
                f.write(f"  Extension: {file['ext']}\n")
                f.write(f"  Byte Offset: {file['offset']}\n")
                f.write(f"  Size: {file['size']} bytes\n")
                f.write(f"  Status: {file['status']}\n")
                f.write(f"  Confidence: {file['confidence']}\n")
                f.write(f"  SHA256: {file['hash']}\n")
                f.write("-" * 20 + "\n")
