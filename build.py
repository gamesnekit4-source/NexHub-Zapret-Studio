r"""
NexHub Zapret Studio - Build & Packaging Script
Builds lightweight standalone Windows .exe and places it directly into Downloads\NexHub.exe
"""

import os
import sys
import shutil
import subprocess

BASE_DIR = r"C:\Users\games\.gemini\antigravity\scratch\nexhub-vpn"
DOWNLOADS_DIR = os.path.join(os.environ["USERPROFILE"], "Downloads")
OUTPUT_EXE = os.path.join(DOWNLOADS_DIR, "NexHub.exe")

def build():
    os.chdir(BASE_DIR)

    icon_path = os.path.join(BASE_DIR, "assets", "icon.ico")
    if not os.path.exists(icon_path):
        raise FileNotFoundError(f"Icon not found at {icon_path}")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--uac-admin",
        f"--icon={icon_path}",
        "--name=NexHub",
        "--add-data=ui;ui",
        "--add-data=assets;assets",
        "--collect-all=webview",
        "--collect-all=pythonnet",
        "--collect-all=clr_loader",
        "app.py"
    ]

    print("Running PyInstaller build:")
    print(" ".join(cmd))

    res = subprocess.run(cmd, check=True)
    if res.returncode != 0:
        print("PyInstaller build failed!")
        return False

    built_exe = os.path.join(BASE_DIR, "dist", "NexHub.exe")
    if not os.path.exists(built_exe):
        print(f"Error: {built_exe} was not created!")
        return False

    print(f"Copying {built_exe} -> {OUTPUT_EXE}...")
    shutil.copy2(built_exe, OUTPUT_EXE)

    file_size_mb = os.path.getsize(OUTPUT_EXE) / (1024 * 1024)
    print(f"SUCCESS! Output placed at: {OUTPUT_EXE}")
    print(f"File size: {file_size_mb:.2f} MB")
    return True

if __name__ == "__main__":
    build()
