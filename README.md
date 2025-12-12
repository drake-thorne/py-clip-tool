# Movie Recap Tool (Python GUI)

A lightweight Python GUI tool for cutting a movie file into multiple short clips using FFmpeg.  
Useful for movie recap channels, commentary videos, or automated content workflows.

## Features
- GUI-based movie file and destination folder selector
- Add/remove multiple timestamp ranges
- Supports timestamps in **hh:mm:ss**, **mm:ss**, or **seconds** format
  - Examples:
    - `1:30` → 1 minute 30 seconds
    - `01:30` → same as above
    - `90` → 90 seconds
    - `0` → start of the video
- Description and heading in GUI for clarity
- Auto-export all clips using FFmpeg without manual video editing
- Fast stream-copy export (`-c copy`) to avoid re-encoding

## Requirements
- Python 3.8+
- FFmpeg installed on your system (must be in PATH)
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
  - Windows: download from [ffmpeg.org](https://ffmpeg.org/) and add to PATH

## Run
1. Clone the repository or download `gui.py`.
2. Open a terminal or command prompt.
3. Run:
   ```bash
   python gui.py
