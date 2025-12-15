import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from gtts import gTTS

def parse_time(time_str):
    try:
        parts = list(map(float, time_str.strip().split(":")))
        if len(parts) == 3:
            return parts[0]*3600 + parts[1]*60 + parts[2]
        elif len(parts) == 2:
            return parts[0]*60 + parts[1]
        elif len(parts) == 1:
            return parts[0]
    except ValueError:
        return None

class ClipRow:
    def __init__(self, parent, remove_callback):
        self.frame = tk.Frame(parent)
        self.start_entry = tk.Entry(self.frame, width=12)
        self.start_entry.grid(row=0, column=0, padx=5)
        self.end_entry = tk.Entry(self.frame, width=12)
        self.end_entry.grid(row=0, column=1, padx=5)
        tk.Button(self.frame, text="-", width=3, command=self.remove).grid(row=0, column=2)
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
        self.root.title("Video Clip Tool")
        self.root.title("Video Clip Tool")
        self.movie_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value="clips")
        self.merge_dir_var = tk.StringVar(value="clips")
        self.voice_dir_var = tk.StringVar(value="voice")
        self.clip_rows = []

        notebook = ttk.Notebook(root)
        notebook.pack(expand=True, fill="both")

        self.clip_tab = tk.Frame(notebook)
        self.merge_tab = tk.Frame(notebook)
        self.voice_tab = tk.Frame(notebook)

        notebook.add(self.clip_tab, text="Clip Cutter")
        notebook.add(self.merge_tab, text="Merge Clips")
        notebook.add(self.voice_tab, text="Voiceover")

        self.build_clip_tab()
        self.build_merge_tab()
        self.build_voice_tab()

    # ---------------- CLIP CUTTER TAB ---------------- #
    def build_clip_tab(self):
        frame = self.clip_tab
        frame = self.clip_tab
        
        # Movie File Selection
        tk.Label(frame, text="Video File").pack(anchor="w", padx=10)
        file_frame = tk.Frame(frame)
        file_frame.pack(fill="x", padx=10)
        tk.Entry(file_frame, textvariable=self.movie_file_var, state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(file_frame, text="Browse...", command=self.select_file).pack(side="left", padx=5)

        # Output Directory Selection
        tk.Label(frame, text="Output Directory").pack(anchor="w", padx=10, pady=(10, 0))
        out_frame = tk.Frame(frame)
        out_frame.pack(fill="x", padx=10)
        tk.Entry(out_frame, textvariable=self.output_dir_var, state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(out_frame, text="Select Folder...", command=self.select_output_dir).pack(side="left", padx=5)

        tk.Label(frame, text="Clip Ranges (hh:mm:ss or mm:ss)", font=("Arial", 10, "bold")).pack(pady=10)
        self.rows_container = tk.Frame(frame)
        self.rows_container.pack()
        tk.Button(frame, text="+ Add Range", command=self.add_row).pack(pady=5)
        tk.Button(frame, text="Export Clips", command=self.export_clips).pack(pady=5)
        self.add_row()

    def select_file(self):
        file = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.mov *.mkv")])
        if file:
            self.movie_file_var.set(file)

    def select_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_var.set(directory)

    def add_row(self):
        row = ClipRow(self.rows_container, self.clip_rows.remove)
        row.frame.pack()
        self.clip_rows.append(row)

    def export_clips(self):
        movie_file = self.movie_file_var.get()
        if not movie_file:
            messagebox.showerror("Error", "Select a movie first.")
            return
        
        output_dir = self.output_dir_var.get()
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), "clips")
            
        os.makedirs(output_dir, exist_ok=True)
        for i, row in enumerate(self.clip_rows, start=1):
            values = row.get_values()
            if not values:
                messagebox.showerror("Error", f"Invalid time in clip {i}")
                return
            start, end = values
            out = os.path.join(output_dir, f"clip_{i}.mp4")
            subprocess.run([
                "ffmpeg", "-ss", str(start), "-i", movie_file,
                "-t", str(end-start), "-c", "copy", out
            ])
        messagebox.showinfo("Done", "Clips exported successfully.")

    # ---------------- MERGE TAB ---------------- #
    def build_merge_tab(self):
        frame = self.merge_tab
        
        tk.Label(frame, text="Clips Directory").pack(anchor="w", padx=10, pady=(10, 0))
        merge_frame = tk.Frame(frame)
        merge_frame.pack(fill="x", padx=10)
        tk.Entry(merge_frame, textvariable=self.merge_dir_var, state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(merge_frame, text="Select Folder...", command=self.select_merge_dir).pack(side="left", padx=5)

        tk.Button(frame, text="Merge Clips", command=self.merge_clips).pack(pady=20)

    def select_merge_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.merge_dir_var.set(directory)

    def merge_clips(self):
        merge_dir = self.merge_dir_var.get()
        if not merge_dir:
             merge_dir = os.path.join(os.getcwd(), "clips")

        if not os.path.exists(merge_dir):
             messagebox.showerror("Error", f"Directory not found: {merge_dir}")
             return

        clips = sorted(f for f in os.listdir(merge_dir) if f.startswith("clip_"))
        if not clips:
            messagebox.showerror("Error", "No clips found.")
            return
        output = os.path.join(merge_dir, "clips_merged.mp4")
        # Generate temporary list file
        list_file_path = os.path.join(merge_dir, "clips_list.txt")
        with open(list_file_path, "w") as f:
            for clip in clips:
                # Use absolute path to avoid relative path issues with ffmpeg concat
                abs_path = os.path.abspath(os.path.join(merge_dir, clip))
                f.write(f"file '{abs_path}'\n")
        subprocess.run([
            "ffmpeg", "-f", "concat", "-safe", "0",
            "-i", list_file_path, "-c", "copy", output
        ])
        os.remove(list_file_path)
        messagebox.showinfo("Done", f"Clips merged to {output}")

    # ---------------- VOICEOVER TAB ---------------- #
    def build_voice_tab(self):
        frame = self.voice_tab
        
        tk.Label(frame, text="Output Directory").pack(anchor="w", padx=10, pady=(10, 0))
        voice_frame = tk.Frame(frame)
        voice_frame.pack(fill="x", padx=10)
        tk.Entry(voice_frame, textvariable=self.voice_dir_var, state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(voice_frame, text="Select Folder...", command=self.select_voice_dir).pack(side="left", padx=5)

        tk.Label(frame, text="Narration Script", font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=5)
        self.script_box = tk.Text(frame, height=15, wrap="word")
        self.script_box.pack(fill="both", expand=True, padx=10)
        tk.Button(frame, text="Generate Voiceover (Male)", command=self.generate_voiceover).pack(pady=10)

    def select_voice_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.voice_dir_var.set(directory)

    def generate_voiceover(self):
        script = self.script_box.get("1.0", "end").strip()
        if not script:
            messagebox.showerror("Error", "Script is empty.")
            return
            
        voice_dir = self.voice_dir_var.get()
        if not voice_dir:
            voice_dir = os.path.join(os.getcwd(), "voice")
            
        os.makedirs(voice_dir, exist_ok=True)
        paragraphs = [p.strip() for p in script.split("\n\n") if p.strip()]
        for i, text in enumerate(paragraphs, start=1):
            tts = gTTS(text=text, lang="en", tld="co.uk")  # tld=co.uk gives slightly deeper/male sounding voice
            tts.save(os.path.join(voice_dir, f"narration_{i}.mp3"))
        messagebox.showinfo("Done", f"Generated {len(paragraphs)} narration clips in {voice_dir}")

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x450")
    ClipGUI(root)
    root.mainloop()
