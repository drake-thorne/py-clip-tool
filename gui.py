import os
import subprocess
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# convert hh:mm:ss or mm:ss or ss string to seconds in float
def parse_time(time_str):
    try:
        parts = list(map(float, time_str.strip().split(":")))
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        elif len(parts) == 1:
            return parts[0]
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

        self.remove_button = tk.Button(
            self.frame, text="-", command=self.remove, width=3
        )
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
        self.root.title("Movie Clip Tool")

        self.movie_file = None
        self.output_dir = "clips"
        self.clip_rows = []
        self.merge_dir = None

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        self.clip_tab = tk.Frame(notebook)
        self.merge_tab = tk.Frame(notebook)

        notebook.add(self.clip_tab, text="Clip Cutter")
        notebook.add(self.merge_tab, text="Merge Clips")

        self.build_clip_tab()
        self.build_merge_tab()

    # =========================
    # Clip Cutter Tab
    # =========================
    def build_clip_tab(self):
        file_frame = tk.Frame(self.clip_tab)
        file_frame.pack(pady=10, fill="x", padx=10)

        self.file_label = tk.Label(file_frame, text="Movie File: None", anchor="w")
        self.file_label.grid(row=0, column=0, sticky="w")

        tk.Button(file_frame, text="Browse...", command=self.select_file)\
            .grid(row=0, column=1, padx=5)

        dest_frame = tk.Frame(self.clip_tab)
        dest_frame.pack(pady=5, fill="x", padx=10)

        self.dest_label = tk.Label(
            dest_frame, text=f"Destination: {self.output_dir}", anchor="w"
        )
        self.dest_label.grid(row=0, column=0, sticky="w")

        tk.Button(dest_frame, text="Browse...", command=self.select_destination)\
            .grid(row=0, column=1, padx=5)

        rows_frame = tk.Frame(self.clip_tab)
        rows_frame.pack(pady=5, padx=10)

        tk.Label(
            rows_frame,
            text="Clip Ranges (Start → End)",
            font=("Arial", 10, "bold")
        ).pack()

        tk.Label(
            rows_frame,
            text="Enter time as hh:mm:ss, mm:ss, or seconds (e.g. 1:30 or 90)",
            font=("Arial", 8),
            fg="gray"
        ).pack(pady=(0, 5))

        self.clip_rows_container = tk.Frame(rows_frame)
        self.clip_rows_container.pack()

        tk.Button(
            self.clip_tab,
            text="+ Add Timestamp Range",
            command=self.add_row
        ).pack(pady=5)

        tk.Button(
            self.clip_tab,
            text="Export Clips",
            command=self.export_clips
        ).pack(pady=10)

        self.add_row()

    # =========================
    # Merge Clips Tab
    # =========================
    def build_merge_tab(self):
        frame = tk.Frame(self.merge_tab)
        frame.pack(pady=20, padx=20, fill="x")

        self.merge_label = tk.Label(
            frame, text="Clips Folder: None", anchor="w"
        )
        self.merge_label.grid(row=0, column=0, sticky="w")

        tk.Button(
            frame,
            text="Browse...",
            command=self.select_merge_dir
        ).grid(row=0, column=1, padx=5)

        tk.Label(
            self.merge_tab,
            text="Merges clip_*.mp4 into clips_merged.mp4 (no re-encoding)",
            font=("Arial", 8),
            fg="gray"
        ).pack(pady=(5, 10))

        tk.Button(
            self.merge_tab,
            text="Merge Clips",
            command=self.merge_clips,
            width=20
        ).pack()

    # Clip Cutter Logic
    def select_file(self):
        file = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.mov *.mkv *.avi")]
        )
        if file:
            self.movie_file = file
            self.file_label.config(
                text=f"Movie File: {os.path.basename(file)}"
            )

    def select_destination(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            self.dest_label.config(text=f"Destination: {folder}")

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

        for idx, row in enumerate(self.clip_rows, start=1):
            values = row.get_values()
            if not values:
                messagebox.showerror("Error", f"Invalid time for clip {idx}.")
                return

            start, end = values
            if end <= start:
                messagebox.showerror(
                    "Error",
                    f"End time must be greater than start time for clip {idx}."
                )
                return

            out_path = os.path.join(self.output_dir, f"clip_{idx}.mp4")

            cmd = [
                "ffmpeg",
                "-ss", str(start),
                "-i", self.movie_file,
                "-t", str(end - start),
                "-c", "copy",
                out_path
            ]

            subprocess.run(cmd, check=True)

        messagebox.showinfo(
            "Done",
            f"All clips exported successfully to:\n{self.output_dir}"
        )

    # Merge Logic
    def select_merge_dir(self):
        folder = filedialog.askdirectory()
        if folder:
            self.merge_dir = folder
            self.merge_label.config(text=f"Clips Folder: {folder}")

    def merge_clips(self):
        if not self.merge_dir:
            messagebox.showerror("Error", "Please select a clips folder.")
            return

        clips = sorted(
            f for f in os.listdir(self.merge_dir)
            if f.lower().endswith(".mp4") and f.startswith("clip_")
        )

        if not clips:
            messagebox.showerror(
                "Error",
                "No clip_*.mp4 files found in the selected folder."
            )
            return

        # Temporary concat list (no clutter)
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt"
        ) as f:
            list_file = f.name
            for clip in clips:
                f.write(
                    f"file '{os.path.join(self.merge_dir, clip)}'\n"
                )

        output_path = os.path.join(
            self.merge_dir, "clips_merged.mp4"
        )

        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            output_path
        ]

        try:
            subprocess.run(cmd, check=True)
            messagebox.showinfo(
                "Done",
                f"Clips merged successfully:\n{output_path}"
            )
        except subprocess.CalledProcessError as e:
            messagebox.showerror("FFmpeg Error", str(e))
        finally:
            os.remove(list_file)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("520x420")
    ClipGUI(root)
    root.mainloop()
