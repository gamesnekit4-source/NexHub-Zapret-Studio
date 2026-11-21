# ⚡ NexHub — Zapret DPI Studio

A modern, fast, and elegant GUI for bypassing Discord & YouTube throttling on Windows (powered by WinDivert / winws).

---

## 💡 Why NexHub?

Traditional DPI bypass tools rely on black command prompt windows and manual configuration files. **NexHub** elevates this experience by providing:
- A clean, modern Glassmorphism interface with zero command prompt clutter.
- One-click startup preset switching (`.bat` profiles).
- High reliability with a pure Win32 process controller that prevents driver deadlocks and memory leaks.
- Complete visual personalization (OLED Black, Cyberpunk, custom accent colors, glows, and backdrop blurs).

---

## ✨ Features

- 🚀 **1-Click Control:** Instant start and stop for packet filtering services.
- 📁 **Automatic Preset Discovery:** Scans your Azapret folder and dynamically detects all available `.bat` scripts (`general.bat`, alternate strategies, etc.).
- 🎨 **Customization Studio:**
  - 8 curated color presets + custom Hex Color Picker.
  - 4 Base Theme Styles: *Midnight*, *OLED Pure Black*, *Cyberpunk*, *Slate*.
  - 4 Ambient Gradient Types: *Radial Spheres*, *Aurora Mesh*, *Linear*, *Pure Flat*.
  - Fine-grained sliders for Neon Glow Intensity and Backdrop Blur.
  - Optional toggle to disable animations for maximum performance on lower-end systems.
- ⚡ **Rock-Solid Stability:**
  - Instant process kill via native Win32 `TerminateProcess` API.
  - Completely non-blocking asynchronous launch (0 ms UI latency).
  - Isolated WebView2 session cache per instance to prevent sharing violations and "Not Responding" errors.
- 🖥️ **Fullscreen Mode:** Toggle via header button or standard `F11` shortcut.
- 🌐 **Dual Language Support:** Instant switching between English and Russian (EN / RU).
- 💾 **State Persistence:** Automatically saves your preferred preset, theme, and language.

---

## 🛠️ System Requirements

- **OS:** Windows 10 / 11 (64-bit)
- **Privileges:** Administrator rights (required for the low-level WinDivert network packet filter driver)
- **Dependencies:** An Azapret distribution folder containing `winws.exe` (e.g. `D:\Azapret-discord-youtube-1.10.3`)

---

## 🚀 Installation & Usage

### Option 1: Standalone Binary (For End Users)
1. Download the latest **`NexHub.exe`** from the [Releases](../../releases) section.
2. Run the application as **Administrator**.
3. Select your desired preset from the dropdown and click **"Launch Preset"**.

### Option 2: Run from Source (For Developers)
1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/NexHub.git
   cd NexHub
   ```
2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the application:
   ```bash
   python app.py
   ```

---

## 📦 Building Standalone Executable

To package the project into a single, self-contained `.exe` with elevated permissions and icon:
```bash
python build.py
```
The compiled output will be generated inside `dist/NexHub.exe`.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Description |
| :--- | :--- |
| <kbd>F11</kbd> | Toggle Fullscreen Mode |
| <kbd>Esc</kbd> | Dismiss active dialogs |

---

## ⚖️ License & Disclaimer

Distributed under the **MIT License**.

*NexHub is a graphical front-end for the `winws` utility and traffic routing scripts. It is designed to optimize multimedia streaming connectivity and prevent packet loss.*
