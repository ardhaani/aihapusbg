import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from rembg import remove
import os
import threading

class BackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Background Remover")
        self.root.geometry("800x600")
        
        # Variabel untuk menyimpan path gambar
        self.input_path = None
        self.output_path = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame utama
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Area preview gambar
        self.preview_frame = ttk.LabelFrame(main_frame, text="Preview Sebelum dan Sesudah", padding="5")
        self.preview_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Label judul preview
        self.label_before = ttk.Label(self.preview_frame, text="Sebelum")
        self.label_before.grid(row=0, column=0, padx=5, pady=(0, 2))

        self.label_after = ttk.Label(self.preview_frame, text="Sesudah")
        self.label_after.grid(row=0, column=1, padx=5, pady=(0, 2))
        
        # Label untuk preview gambar sebelum dan sesudah
        self.preview_before_label = ttk.Label(self.preview_frame, text="Belum ada gambar")
        self.preview_before_label.grid(row=1, column=0, padx=5, pady=5)

        self.preview_after_label = ttk.Label(self.preview_frame, text="Belum ada hasil")
        self.preview_after_label.grid(row=1, column=1, padx=5, pady=5)
        
        # Tombol pilih file
        self.select_btn = ttk.Button(main_frame, text="Pilih Gambar", command=self.select_file)
        self.select_btn.grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        
        # Label untuk menampilkan path file
        self.file_label = ttk.Label(main_frame, text="Tidak ada file dipilih")
        self.file_label.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Tombol proses
        self.process_btn = ttk.Button(main_frame, text="Hapus Background", command=self.process_image, state=tk.DISABLED)
        self.process_btn.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Status: Siap")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Konfigurasi grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def select_file(self):
        filetypes = (
            ('Image files', '*.jpg *.jpeg *.png'),
            ('All files', '*.*')
        )
        
        filename = filedialog.askopenfilename(
            title='Pilih Gambar',
            filetypes=filetypes
        )
        
        if filename:
            self.input_path = filename
            self.file_label.config(text=os.path.basename(filename))
            self.process_btn.config(state=tk.NORMAL)
            self.show_preview(before_path=filename)
            
    def show_preview(self, before_path=None, after_path=None):
        def load_and_resize(image_path):
            image = Image.open(image_path)
            aspect_ratio = image.width / image.height
            new_width = 300
            new_height = int(new_width / aspect_ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        
        if before_path:
            before_image = load_and_resize(before_path)
            self.preview_before_label.config(image=before_image)
            self.preview_before_label.image = before_image  # Keep reference
        
        if after_path:
            after_image = load_and_resize(after_path)
            self.preview_after_label.config(image=after_image)
            self.preview_after_label.image = after_image  # Keep reference
            
    def process_image(self):
        if not self.input_path:
            messagebox.showerror("Error", "Pilih gambar terlebih dahulu!")
            return
            
        # Dapatkan output path
        output_dir = os.path.dirname(self.input_path)
        filename = os.path.basename(self.input_path)
        name, ext = os.path.splitext(filename)
        self.output_path = os.path.join(output_dir, f"{name}_no_bg.png")
        
        # Disable tombol selama pemrosesan
        self.process_btn.config(state=tk.DISABLED)
        self.select_btn.config(state=tk.DISABLED)
        
        # Mulai progress bar
        self.progress.start()
        self.status_label.config(text="Status: Memproses...")
        
        # Jalankan pemrosesan di thread terpisah
        thread = threading.Thread(target=self.remove_background_thread)
        thread.start()
        
    def remove_background_thread(self):
        try:
            # Baca gambar input
            input_image = Image.open(self.input_path)
            
            # Hapus background
            output_image = remove(input_image)
            
            # Simpan hasil
            output_image.save(self.output_path)
            
            # Update UI di main thread
            self.root.after(0, self.process_complete)
            
        except Exception as e:
            # Update UI di main thread
            self.root.after(0, lambda: self.process_error(str(e)))
            
    def process_complete(self):
        self.progress.stop()
        self.status_label.config(text=f"Status: Selesai! File disimpan di: {self.output_path}")
        self.process_btn.config(state=tk.NORMAL)
        self.select_btn.config(state=tk.NORMAL)
        
        # Tampilkan preview hasil
        self.show_preview(before_path=self.input_path, after_path=self.output_path)
        
        messagebox.showinfo("Sukses", "Background berhasil dihapus!")
        
    def process_error(self, error_message):
        self.progress.stop()
        self.status_label.config(text="Status: Error!")
        self.process_btn.config(state=tk.NORMAL)
        self.select_btn.config(state=tk.NORMAL)
        messagebox.showerror("Error", f"Terjadi kesalahan: {error_message}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BackgroundRemoverApp(root)
    root.mainloop()
