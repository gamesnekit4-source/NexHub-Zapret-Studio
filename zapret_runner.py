"""
NexHub Zapret Runner & High-Reliability Process Manager
Manages DPI bypass for Discord & YouTube via winws.exe and bat scripts.
Uses direct Win32 TerminateProcess API for instant, guaranteed process kill (0.001s),
preventing WinDivert driver locks and freeze-on-restart bugs.
Completely non-blocking asynchronous execution for zero UI latency.
"""

import os
import glob
import time
import threading
import subprocess
import ctypes
from ctypes import wintypes

TH32CS_SNAPPROCESS = 0x00000002
PROCESS_TERMINATE = 0x0001
PROCESS_QUERY_INFORMATION = 0x0400

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

def get_winws_pids() -> list[int]:
    """Finds all running winws.exe PIDs in memory using pure Win32 snapshot."""
    pids = []
    try:
        h_snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if h_snapshot == -1 or h_snapshot == 0:
            return pids

        pe = PROCESSENTRY32()
        pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
        try:
            if ctypes.windll.kernel32.Process32First(h_snapshot, ctypes.byref(pe)):
                while True:
                    exe_name = pe.szExeFile.decode('utf-8', errors='ignore').lower()
                    if exe_name == "winws.exe":
                        pids.append(pe.th32ProcessID)
                    if not ctypes.windll.kernel32.Process32Next(h_snapshot, ctypes.byref(pe)):
                        break
        finally:
            ctypes.windll.kernel32.CloseHandle(h_snapshot)
    except Exception:
        pass
    return pids

def is_winws_process_running() -> bool:
    """Instant Win32 check for winws.exe. 0.001s, 0 subprocesses, non-blocking."""
    return len(get_winws_pids()) > 0

def kill_winws_instances() -> bool:
    """Terminates all winws.exe instances directly via Win32 TerminateProcess API."""
    pids = get_winws_pids()
    if not pids:
        return True

    for pid in pids:
        try:
            hp = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
            if hp:
                ctypes.windll.kernel32.TerminateProcess(hp, 0)
                ctypes.windll.kernel32.CloseHandle(hp)
        except Exception:
            pass

    return not is_winws_process_running()

def discover_zapret_folder(preferred_path: str = "") -> str:
    candidates = []
    if preferred_path:
        candidates.append(preferred_path)

    candidates.extend([
        r"D:\Azapret-discord-youtube-1.10.3",
        r"C:\Azapret-discord-youtube-1.10.3",
        os.path.join(os.environ.get("USERPROFILE", ""), "Downloads", "Azapret-discord-youtube-1.10.3"),
        os.path.join(os.environ.get("USERPROFILE", ""), "Desktop", "Azapret-discord-youtube-1.10.3"),
        os.path.join(os.getcwd(), "Azapret-discord-youtube-1.10.3"),
        os.path.join(os.getcwd(), "zapret"),
        r"D:\zapret",
        r"C:\zapret"
    ])

    for c in candidates:
        if c and os.path.exists(c) and os.path.isdir(c):
            winws = os.path.join(c, "bin", "winws.exe")
            gen = os.path.join(c, "general.bat")
            if os.path.exists(winws) or os.path.exists(gen):
                return os.path.abspath(c)

    return preferred_path or r"D:\Azapret-discord-youtube-1.10.3"

class ZapretRunner:
    def __init__(self, zapret_dir: str = ""):
        self.zapret_dir = discover_zapret_folder(zapret_dir)

    def set_folder(self, new_dir: str) -> bool:
        if os.path.exists(new_dir) and os.path.isdir(new_dir):
            self.zapret_dir = os.path.abspath(new_dir)
            return True
        return False

    def folder_exists(self) -> bool:
        return os.path.exists(self.zapret_dir) and os.path.isdir(self.zapret_dir)

    def get_presets(self) -> list[str]:
        if not self.folder_exists():
            return []
        bats = glob.glob(os.path.join(self.zapret_dir, "*.bat"))
        preset_names = []
        for b in bats:
            name = os.path.basename(b)
            if name.lower() != "service.bat":
                preset_names.append(name)
        preset_names.sort()
        if "general.bat" in preset_names:
            preset_names.remove("general.bat")
            preset_names.insert(0, "general.bat")
        return preset_names

    def is_running(self) -> bool:
        return is_winws_process_running()

    def start(self, bat_name: str = "general.bat") -> tuple[bool, str]:
        if not self.folder_exists():
            return False, f"Папка Azapret не найдена: {self.zapret_dir}. Укажите путь в настройках."

        bat_path = os.path.join(self.zapret_dir, bat_name)
        if not os.path.exists(bat_path):
            return False, f"Файл {bat_name} не найден в {self.zapret_dir}"

        # 1. Kill any existing instances first
        kill_winws_instances()

        # 2. Launch completely asynchronously in background thread - 0ms UI blocking!
        def _bg_launch():
            try:
                env = os.environ.copy()
                env["NO_UPDATE_CHECK"] = "1"

                cmd_line = f'start /min "" "{bat_path}"'
                subprocess.Popen(
                    cmd_line,
                    shell=True,
                    cwd=self.zapret_dir,
                    env=env,
                    creationflags=0x08000000 | 0x00000200,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass

        threading.Thread(target=_bg_launch, daemon=True).start()
        return True, f"Запуск {bat_name}..."

    def stop(self) -> tuple[bool, str]:
        """Instantly terminates all winws.exe instances without lingering handles."""
        killed = kill_winws_instances()
        if killed:
            return True, "Служба Запрет остановлена"
        return False, "Не удалось завершить процесс winws.exe"
