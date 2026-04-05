import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from .preview_panel import PreviewPanel
from core.carver import ForensicCarver
from core.report_generator import ReportGenerator

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    """
    Main application window for the Forensic File Recovery System.
    """
    
    def __init__(self):
        super().__init__()
        
        self.title("Advanced Signature-Based File Recovery & Carving System")
        self.geometry("1280x800")
        
        # State
        self.image_path = tk.StringVar(value="")
        self.output_dir = tk.StringVar(value=os.path.abspath("recovered"))
        self.carver = None
        self.recovered_data = [] # List of dicts
        
        self._setup_layout()
        self._setup_sidebar()
        self._setup_main_area()
        self._setup_styles()

    def _setup_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="FORENSIC CARVER", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20, padx=20)
        
        # Image Selection
        self.select_img_btn = ctk.CTkButton(self.sidebar_frame, text="Select Disk Image", command=self._select_image)
        self.select_img_btn.pack(pady=10, padx=20)
        
        self.img_label = ctk.CTkLabel(self.sidebar_frame, text="No Image selected", wraplength=150, font=ctk.CTkFont(size=10))
        self.img_label.pack(pady=5, padx=20)
        
        # Output Selection
        self.select_out_btn = ctk.CTkButton(self.sidebar_frame, text="Select Output Folder", command=self._select_output)
        self.select_out_btn.pack(pady=10, padx=20)
        
        self.out_label = ctk.CTkLabel(self.sidebar_frame, text=self.output_dir.get(), wraplength=150, font=ctk.CTkFont(size=10))
        self.out_label.pack(pady=5, padx=20)
        
        # Control Buttons
        self.start_btn = ctk.CTkButton(self.sidebar_frame, text="START SCAN", fg_color="green", hover_color="#006400", command=self._start_scan)
        self.start_btn.pack(pady=20, padx=20)
        
        self.stop_btn = ctk.CTkButton(self.sidebar_frame, text="STOP SCAN", fg_color="red", hover_color="#8B0000", state="disabled", command=self._stop_scan)
        self.stop_btn.pack(pady=10, padx=20)
        
        # Tools
        self.export_btn = ctk.CTkButton(self.sidebar_frame, text="Export Forensic Reports", command=self._export_reports)
        self.export_btn.pack(pady=10, padx=20)
        
        self.open_folder_btn = ctk.CTkButton(self.sidebar_frame, text="Open Recovered Folder", command=self._open_recovered_folder)
        self.open_folder_btn.pack(pady=10, padx=20)

    def _setup_main_area(self):
        self.main_container = ctk.CTkFrame(self, bg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.main_container.grid_columnconfigure(0, weight=3)
        self.main_container.grid_columnconfigure(1, weight=1) # Reduced weight for preview
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(2, weight=1)

        # 1. Stats Dashboard
        self.stats_frame = ctk.CTkFrame(self.main_container, height=100)
        self.stats_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 20))
        
        self.progress_bar = ctk.CTkProgressBar(self.stats_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=(20, 10))
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self.stats_frame, text="Status: Ready", font=ctk.CTkFont(size=14))
        self.status_label.pack(side="left", padx=20, pady=5)
        
        self.files_found_label = ctk.CTkLabel(self.stats_frame, text="Files Found: 0", font=ctk.CTkFont(size=14, weight="bold"))
        self.files_found_label.pack(side="right", padx=20, pady=5)

        # 2. Results List (TreeView)
        self.list_frame = ctk.CTkFrame(self.main_container)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=(0,10))
        
        self.tree = ttk.Treeview(self.list_frame, columns=("name", "ext", "offset", "size", "status", "confidence"), show="headings")
        self.tree.heading("name", text="Filename")
        self.tree.heading("ext", text="Type")
        self.tree.heading("offset", text="Offset")
        self.tree.heading("size", text="Size")
        self.tree.heading("status", text="Status")
        self.tree.heading("confidence", text="Conf.")
        
        self.tree.column("name", width=150)
        self.tree.column("ext", width=50)
        self.tree.column("offset", width=80)
        self.tree.column("size", width=80)
        self.tree.column("status", width=80)
        self.tree.column("confidence", width=50)
        
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        
        # Scrollbar for tree
        self.tree_scroll = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree_scroll.pack(side="right", fill="y")

        # 3. Preview Panel
        self.preview_panel = PreviewPanel(self.main_container)
        self.preview_panel.grid(row=1, column=1, rowspan=2, sticky="nsew")

        # 4. Live Console
        self.console_frame = ctk.CTkFrame(self.main_container)
        self.console_frame.grid(row=2, column=0, sticky="nsew", pady=(20, 0), padx=(0, 10))
        
        self.console_text = ctk.CTkTextbox(self.console_frame, state="disabled", font=ctk.CTkFont(family="Courier", size=12))
        self.console_text.pack(fill="both", expand=True, padx=10, pady=10)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b", 
                        borderwidth=0)
        style.map("Treeview", background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", 
                        background="#212121", 
                        foreground="white", 
                        relief="flat")

    def _select_image(self):
        path = filedialog.askopenfilename(title="Select Disk Image", filetypes=[("Disk Images", "*.img *.dd *.bin *.raw"), ("All Files", "*.*")])
        if path:
            self.image_path.set(path)
            self.img_label.configure(text=os.path.basename(path))

    def _select_output(self):
        path = filedialog.askdirectory(title="Select Output Folder")
        if path:
            self.output_dir.set(path)
            self.out_label.configure(text=path)

    def _start_scan(self):
        if not self.image_path.get():
            messagebox.showerror("Error", "Please select a disk image first.")
            return
            
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.tree.delete(*self.tree.get_children())
        self.recovered_data = []
        
        self.carver = ForensicCarver(
            image_path=self.image_path.get(),
            output_dir=self.output_dir.get(),
            update_callback=self._update_ui_progress,
            log_callback=self._update_ui_log
        )
        
        self.carver.start()
        self.status_label.configure(text="Status: Scanning...")

    def _stop_scan(self):
        if self.carver:
            self.carver.stop()
            self.status_label.configure(text="Status: Stopping...")
            self.stop_btn.configure(state="disabled")

    def _update_ui_progress(self, percent: float, count: int):
        self.progress_bar.set(percent / 100)
        self.files_found_label.configure(text=f"Files Found: {count}")
        
        # If new files were added to carver list but not to tree
        if count > len(self.recovered_data):
            # Get latest files from carver list
            for i in range(len(self.recovered_data), count):
                file_info = self.carver.recovered_files[i]
                self.recovered_data.append(file_info)
                self.tree.insert("", "end", values=(
                    file_info["name"], 
                    file_info["ext"].upper(), 
                    f"0x{file_info['offset']:X}", 
                    f"{file_info['size']/1024:.1f} KB", 
                    file_info["status"], 
                    f"{file_info['confidence']:.2f}"
                ))

        if percent >= 100:
            self.status_label.configure(text="Status: Completed")
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")

    def _update_ui_log(self, message: str):
        self.console_text.configure(state="normal")
        self.console_text.insert("end", f"{message}\n")
        self.console_text.see("end")
        self.console_text.configure(state="disabled")

    def _on_tree_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        item_index = self.tree.index(selected_item[0])
        file_info = self.recovered_data[item_index]
        file_path = file_info["path"]
        
        self.preview_panel.show_preview(file_path, file_info)

    def _export_reports(self):
        if not self.recovered_data:
            messagebox.showinfo("Info", "No recovered files to report.")
            return
            
        ReportGenerator.generate_all(self.recovered_data)
        messagebox.showinfo("Success", "Forensic reports generated in the 'reports/' folder.")

    def _open_recovered_folder(self):
        os.startfile(self.output_dir.get()) if os.name == 'nt' else os.system(f'xdg-open "{self.output_dir.get()}"')
