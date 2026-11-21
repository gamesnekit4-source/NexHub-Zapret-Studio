"""
NexHub - Zapret DPI Bypass Studio
High-Performance, Dedicated Discord & YouTube DPI Bypass
Engineered for zero UI latency, instant responsiveness, and rock-solid stability.
"""

import os
import sys
import json
import shutil
import ctypes
from ctypes import wintypes
import webview

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.config_mgr import load_config, save_config, get_config_dir
from backend.zapret_runner import ZapretRunner, kill_winws_instances

# Win32 Process Structures for clean instance management
TH32CS_SNAPPROCESS = 0x00000002
PROCESS_TERMINATE = 0x0001

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ('dwSize', wintypes.DWORD),
        ('cntUsage', wintypes.DWORD),
        ('th32ProcessID', wintypes.DWORD),
        ('th32DefaultHeapID', ctypes.POINTER(ctypes.c_ulong)),
        ('th32ModuleID', wintypes.DWORD),
        ('cntThreads', wintypes.DWORD),
        ('th32ParentProcessID', wintypes.DWORD),
        ('pcPriClassBase', ctypes.c_long),
        ('dwFlags', wintypes.DWORD),
        ('szExeFile', ctypes.c_char * 260)
    ]

def terminate_stale_nexhub_instances():
    """Terminates any orphan background NexHub.exe processes from previous crashes."""
    current_pid = os.getpid()
    try:
        h_snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if h_snapshot and h_snapshot != -1:
            pe = PROCESSENTRY32()
            pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
            if ctypes.windll.kernel32.Process32First(h_snapshot, ctypes.byref(pe)):
                while True:
                    name = pe.szExeFile.decode('utf-8', errors='ignore').lower()
                    if name == "nexhub.exe" and pe.th32ProcessID != current_pid:
                        hp = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pe.th32ProcessID)
                        if hp:
                            ctypes.windll.kernel32.TerminateProcess(hp, 0)
                            ctypes.windll.kernel32.CloseHandle(hp)
                    if not ctypes.windll.kernel32.Process32Next(h_snapshot, ctypes.byref(pe)):
                        break
            ctypes.windll.kernel32.CloseHandle(h_snapshot)
    except Exception:
        pass

# Setup dedicated isolated cache folder per PID to prevent WebView2 lock deadlocks
SESSION_CACHE_DIR = os.path.join(get_config_dir(), f"cache_{os.getpid()}")
try:
    os.makedirs(SESSION_CACHE_DIR, exist_ok=True)
except Exception:
    pass
os.environ["WEBVIEW2_USER_DATA_FOLDER"] = SESSION_CACHE_DIR

def cleanup_stale_cache_dirs():
    """Removes old session cache folders from past runs."""
    try:
        base_dir = get_config_dir()
        current_name = f"cache_{os.getpid()}"
        for item in os.listdir(base_dir):
            if (item.startswith("cache_") and item != current_name) or item == "webview_cache":
                target = os.path.join(base_dir, item)
                try:
                    shutil.rmtree(target, ignore_errors=True)
                except Exception:
                    pass
    except Exception:
        pass

def force_exit():
    """Unconditionally shuts down the process, freeing all locks and memory."""
    try:
        shutil.rmtree(SESSION_CACHE_DIR, ignore_errors=True)
    except Exception:
        pass
    os._exit(0)

def get_bundle_path(relative_path: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(BASE_DIR, relative_path)

def set_dark_window_border(hwnd):
    try:
        DWMWA_BORDER_COLOR = 34
        DWMWA_CAPTION_COLOR = 35
        dark_color = ctypes.c_uint32(0x00140c08)  # BGR for #080c14
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_BORDER_COLOR, ctypes.byref(dark_color), ctypes.sizeof(dark_color)
        )
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_CAPTION_COLOR, ctypes.byref(dark_color), ctypes.sizeof(dark_color)
        )
    except Exception:
        pass

class NexHubApi:
    """
    Exposed JS API for NexHub.
    NOTE: All internal fields MUST begin with an underscore `_`
    so PyWebView's inject_pywebview does not recursively introspect them!
    """
    def __init__(self, window_holder, config: dict, zapret_runner: ZapretRunner):
        self._window_holder = window_holder
        self._config = config
        self._zapret_runner = zapret_runner

    def _get_window(self):
        return self._window_holder[0] if self._window_holder else None

    def get_initial_data(self) -> dict:
        try:
            presets = self._zapret_runner.get_presets()
            is_zapret = self._zapret_runner.is_running()
            return {
                "config": self._config,
                "zapret_presets": presets,
                "zapret_folder": self._zapret_runner.zapret_dir,
                "zapret_folder_exists": self._zapret_runner.folder_exists(),
                "is_zapret_running": is_zapret
            }
        except Exception as e:
            return {"error": str(e), "config": self._config}

    def get_live_status(self) -> dict:
        try:
            return {
                "running": self._zapret_runner.is_running(),
                "folder_exists": self._zapret_runner.folder_exists()
            }
        except Exception:
            return {"running": False, "folder_exists": False}

    def start_zapret(self, bat_name: str = "general.bat") -> dict:
        try:
            if "zapret" not in self._config:
                self._config["zapret"] = {}
            self._config["zapret"]["preset"] = bat_name
            save_config(self._config)

            ok, msg = self._zapret_runner.start(bat_name)
            return {"success": ok, "message": msg}
        except Exception as e:
            return {"success": False, "message": f"Ошибка: {e}"}

    def stop_zapret(self) -> dict:
        try:
            ok, msg = self._zapret_runner.stop()
            return {"success": ok, "message": msg}
        except Exception as e:
            return {"success": False, "message": f"Ошибка: {e}"}

    def choose_zapret_folder(self) -> dict:
        try:
            win = self._get_window()
            if win:
                res = win.create_file_dialog(webview.FOLDER_DIALOG)
                if res and len(res) > 0:
                    chosen = res[0]
                    if os.path.exists(chosen):
                        self._zapret_runner.set_folder(chosen)
                        self._config.setdefault("zapret", {})["folder"] = chosen
                        save_config(self._config)
                        presets = self._zapret_runner.get_presets()
                        return {
                            "success": True,
                            "folder": chosen,
                            "presets": presets
                        }
            return {"success": False, "message": "Выбор отменен"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def open_zapret_folder(self) -> dict:
        try:
            folder = self._zapret_runner.zapret_dir
            if os.path.exists(folder):
                os.startfile(folder)
                return {"success": True}
            return {"success": False, "message": "Папка не найдена на диске"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def save_customization(self, theme_data: dict) -> dict:
        try:
            self._config.setdefault("theme", {}).update(theme_data)
            save_config(self._config)
            return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def save_language(self, lang: str) -> dict:
        try:
            self._config["language"] = lang
            save_config(self._config)
            return {"success": True}
        except Exception:
            return {"success": False}

    def toggle_fullscreen(self) -> dict:
        try:
            win = self._get_window()
            if win:
                win.toggle_fullscreen()
                return {"success": True}
        except Exception as e:
            return {"success": False, "message": str(e)}
        return {"success": False}

    def window_minimize(self):
        try:
            win = self._get_window()
            if win:
                win.minimize()
        except Exception:
            pass

    def window_maximize(self):
        try:
            win = self._get_window()
            if win:
                win.toggle_fullscreen()
        except Exception:
            pass

    def window_close(self):
        try:
            win = self._get_window()
            if win:
                win.destroy()
        finally:
            force_exit()

def main():
    # 1. Terminate any orphan NexHub.exe instances from previous abnormal crashes
    terminate_stale_nexhub_instances()

    # 2. Clean up stale cache directories
    cleanup_stale_cache_dirs()

    # 3. Load user configuration
    config = load_config()

    saved_zapret_dir = config.get("zapret", {}).get("folder", "")
    zapret_runner = ZapretRunner(saved_zapret_dir)

    html_path = get_bundle_path(os.path.join("ui", "index.html"))

    window_holder = [None]
    api = NexHubApi(window_holder, config, zapret_runner)

    window = webview.create_window(
        title="NexHub - Zapret Studio",
        url=html_path,
        js_api=api,
        width=1060,
        height=690,
        min_size=(880, 580),
        frameless=True,
        easy_drag=True,
        background_color='#080c14'
    )
    window_holder[0] = window

    def on_shown():
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, "NexHub - Zapret Studio")
            if hwnd:
                set_dark_window_border(hwnd)
        except Exception:
            pass

    def on_closed():
        force_exit()

    window.events.shown += on_shown
    window.events.closed += on_closed

    webview.start(debug=False)
    force_exit()

if __name__ == "__main__":
    main()
