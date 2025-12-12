import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def parse_time(time_str):
    """Convert hh:mm:ss or mm:ss or ss string to seconds (float)."""
    try:
        parts = list(map(float, time_str.strip().split(":")))
        if len(parts) == 3:  # hh:mm:ss
            return parts[0]*3600 + parts[1]*60 + parts[2]
        elif len(parts) == 2:  # mm:ss
            return parts[0]*60 + parts[1]
        elif len(parts) == 1:  # ss
            return parts[0]
        else:
            return None
    except ValueError:
        return None

class ClipRow:
    def __init__(self, parent, remove_callback):
        self.frame = tk.Frame(parent)
        
        self.start_entry = tk.Entry(self.frame, width=12)
        self.start_entry.grid(row=0, column=0, padx=5, pady=2)

        self.end_entry = tk.Entry(self.frame, width=12)
        self.end_entry.grid(row=0, column=1, padx=5, pady=2)

        self.remove_button = tk.Button(self.frame, text="-", command=self.remove, width=3)
        self.remove_button.grid(row=0, column=2, padx=5, pady=2)

        self.remove_callback = remove_callback

    def remove(self):
        self.frame.destroy()
        self.remove_callback(self)

    def get_values(self):
        start = parse_time(self.start_entry.get())
        end = parse_time(self.end_entry.get())
        if start is not None and end is not None:
            return start, end
        return None

class ClipGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Clip Cutter")

        self.movie_file = None
        self.output_dir = "clips"  # default
        self.clip_rows = []

        # Movie selector
        self.file_frame = tk.Frame(root)
        self.file_frame.pack(pady=10, fill="x", padx=10)

        self.file_label = tk.Label(self.file_frame, text="Movie File: None", anchor="w")
        self.file_label.grid(row=0, column=0, sticky="w")
        self.file_button = tk.Button(self.file_frame, text="Browse...", command=self.select_file)
        self.file_button.grid(row=0, column=1, padx=5, sticky="e")

        # Destination selector
        self.dest_frame = tk.Frame(root)
        self.dest_frame.pack(pady=5, fill="x", padx=10)

        self.dest_label = tk.Label(self.dest_frame, text=f"Destination: {self.output_dir}", anchor="w")
        self.dest_label.grid(row=0, column=0, sticky="w")
        self.dest_button = tk.Button(self.dest_frame, text="Browse...", command=self.select_destination)
        self.dest_button.grid(row=0, column=1, padx=5, sticky="e")

        # Rows container
        self.rows_frame = tk.Frame(root)
        self.rows_frame.pack(pady=5, fill="x", padx=10)

        # Heading + description
        self.heading_label = tk.Label(self.rows_frame, text="Clip Ranges (Start → End)", font=("Arial", 10, "bold"))
        self.heading_label.pack(pady=(0,2))
        self.desc_label = tk.Label(
            self.rows_frame, 
            text="Enter time as hh:mm:ss or mm:ss (e.g., 01:30 → 1 min 30 sec)", 
            font=("Arial", 8), fg="gray"
        )
        self.desc_label.pack(pady=(0,5))

        # Container for actual clip rows
        self.clip_rows_container = tk.Frame(self.rows_frame)
        self.clip_rows_container.pack()

        # Add row button
        self.add_button = tk.Button(root, text="+ Add Timestamp Range", command=self.add_row)
        self.add_button.pack(pady=5)

        # Export button
        self.export_button = tk.Button(root, text="Export Clips", command=self.export_clips)
        self.export_button.pack(pady=10)

        # Start with one row
        self.add_row()

    def select_file(self):
        file = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.mov *.mkv *.avi")]
        )
        if file:
            self.movie_file = file
            filename = os.path.basename(file)
            self.file_label.config(text=f"Movie File: {filename}")

    def select_destination(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            self.dest_label.config(text=f"Destination: {self.output_dir}")

    def add_row(self):
        row = ClipRow(self.clip_rows_container, self.remove_row)
        row.frame.pack()
        self.clip_rows.append(row)

    def remove_row(self, row):
        self.clip_rows.remove(row)

    def export_clips(self):
        if not self.movie_file:
            messagebox.showerror("Error", "Please select a movie file first.")
            return

        os.makedirs(self.output_dir, exist_ok=True)

        idx = 1
        for row in self.clip_rows:
            values = row.get_values()
            if not values:
                messagebox.showerror("Error", f"Invalid start or end time for clip {idx}.")
                return
            
            start, end = values
            if end <= start:
                messagebox.showerror("Error", f"End time must be greater than start time for clip {idx}.")
                return

            duration = end - start
            out_path = os.path.join(self.output_dir, f"clip_{idx}.mp4")

            cmd = [
                "ffmpeg",
                "-ss", str(start),
                "-i", self.movie_file,
                "-t", str(duration),
                "-c", "copy",
                out_path
            ]

            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("FFmpeg Error", f"Failed to export clip {idx}.\n{e}")
                return

            idx += 1

        messagebox.showinfo("Done", f"All clips exported successfully to:\n{self.output_dir}")

if __name__ == "__main__":
    root = tk.Tk()

    # Keep window on top until fully loaded
    root.attributes("-topmost", True)

    # Center window on screen
    root.update_idletasks()
    w = 500
    h = 350
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    app = ClipGUI(root)

    # Disable topmost after 500ms
    root.after(500, lambda: root.attributes("-topmost", False))

    root.mainloop()
