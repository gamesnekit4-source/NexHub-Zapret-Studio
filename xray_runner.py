"""
NexHub Xray Core Runner & Live Traffic Monitor
Operates safely out of %APPDATA%\\NexHub\\bin for maximum portability across all Windows PCs.
"""

import os
import sys
import json
import time
import shutil
import subprocess
import ctypes
from ctypes import wintypes
from backend.parser import build_xray_config
from backend.proxy_mgr import set_system_proxy

PROCESS_QUERY_INFORMATION = 0x0400

class IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ('ReadOperationCount', ctypes.c_uint64),
        ('WriteOperationCount', ctypes.c_uint64),
        ('OtherOperationCount', ctypes.c_uint64),
        ('ReadTransferCount', ctypes.c_uint64),
        ('WriteTransferCount', ctypes.c_uint64),
        ('OtherTransferCount', ctypes.c_uint64),
    ]

def format_speed(bytes_per_sec: float) -> str:
    if bytes_per_sec <= 0:
        return "0 B/s"
    elif bytes_per_sec < 1024:
        return f"{int(bytes_per_sec)} B/s"
    elif bytes_per_sec < 1024 * 1024:
        return f"{bytes_per_sec / 1024:.1f} KB/s"
    elif bytes_per_sec < 1024 * 1024 * 1024:
        return f"{bytes_per_sec / (1024 * 1024):.1f} MB/s"
    else:
        return f"{bytes_per_sec / (1024 * 1024 * 1024):.2f} GB/s"

def ensure_bin_directory(bundled_core_dir: str) -> str:
    """Copies xray.exe and data files to %APPDATA%\\NexHub\\bin for permanent execution permissions."""
    appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
    target_bin = os.path.join(appdata, "NexHub", "bin")
    os.makedirs(target_bin, exist_ok=True)
    
    if os.path.exists(bundled_core_dir):
        for item in os.listdir(bundled_core_dir):
            s_file = os.path.join(bundled_core_dir, item)
            d_file = os.path.join(target_bin, item)
            if os.path.isfile(s_file):
                try:
                    if not os.path.exists(d_file) or os.path.getsize(s_file) != os.path.getsize(d_file):
                        shutil.copy2(s_file, d_file)
                except Exception as e:
                    print(f"Warning copying {item} to {target_bin}: {e}")
    return target_bin

class XrayRunner:
    def __init__(self, bundled_core_dir: str):
        self.working_dir = ensure_bin_directory(bundled_core_dir)
        self.xray_path = os.path.join(self.working_dir, "xray.exe")
        self.proc: subprocess.Popen | None = None
        self.proc_handle = None
        self.last_check_time = 0.0
        self.last_read_bytes = 0
        self.last_write_bytes = 0
        self.download_speed = 0.0
        self.upload_speed = 0.0
        self.active_node = None

    def is_running(self) -> bool:
        if self.proc is None:
            return False
        return self.proc.poll() is None

    def start(self, node: dict, socks_port: int = 10808, http_port: int = 10809, enable_sys_proxy: bool = True) -> tuple[bool, str]:
        self.stop(disable_sys_proxy=False)
        
        # Check node validity
        host = node.get("host", "").strip()
        if not host or host in ("0.0.0.0", "127.0.0.1", "localhost"):
            return False, f"Некорректный адрес сервера ({host}). Обновите ссылку на VPN."

        if not os.path.exists(self.xray_path):
            return False, f"Файл xray.exe не найден в {self.working_dir}"

        config = build_xray_config(node, socks_port, http_port)
        config_path = os.path.join(self.working_dir, "active_config.json")
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            return False, f"Не удалось записать конфигурацию: {e}"

        try:
            flags = 0x08000000  # CREATE_NO_WINDOW
            self.proc = subprocess.Popen(
                [self.xray_path, "run", "-c", config_path],
                cwd=self.working_dir,
                creationflags=flags,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )

            # Wait briefly to detect immediate crash
            time.sleep(0.4)
            if self.proc.poll() is not None:
                err_msg = ""
                try:
                    err_msg = self.proc.stderr.read().decode('utf-8', errors='ignore')
                except Exception:
                    pass
                self.proc = None
                return False, f"Ошибка запуска Xray: {err_msg[:120] if err_msg else 'Проверьте настройки соединения'}"

            # Open process handle for I/O monitoring
            try:
                self.proc_handle = ctypes.windll.kernel32.OpenProcess(
                    PROCESS_QUERY_INFORMATION, False, self.proc.pid
                )
            except Exception:
                self.proc_handle = None

            self.last_check_time = time.perf_counter()
            self.last_read_bytes = 0
            self.last_write_bytes = 0
            self.download_speed = 0.0
            self.upload_speed = 0.0
            self.active_node = node

            if enable_sys_proxy:
                set_system_proxy(True, "127.0.0.1", http_port)

            return True, "Подключение установлено"
        except Exception as e:
            return False, f"Исключение при запуске: {e}"

    def stop(self, disable_sys_proxy: bool = True) -> bool:
        if disable_sys_proxy:
            set_system_proxy(False)

        if self.proc:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=0.6)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
            self.proc = None

        if self.proc_handle:
            try:
                ctypes.windll.kernel32.CloseHandle(self.proc_handle)
            except Exception:
                pass
            self.proc_handle = None

        self.active_node = None
        self.download_speed = 0.0
        self.upload_speed = 0.0
        return True

    def get_stats(self) -> dict:
        if not self.is_running() or not self.proc_handle:
            return {
                "running": False,
                "download_speed_str": "0 B/s",
                "upload_speed_str": "0 B/s",
                "download_speed": 0,
                "upload_speed": 0,
                "total_read": 0,
                "total_write": 0
            }

        io = IO_COUNTERS()
        now = time.perf_counter()
        elapsed = now - self.last_check_time

        total_read = 0
        total_write = 0
        try:
            if ctypes.windll.kernel32.GetProcessIoCounters(self.proc_handle, ctypes.byref(io)):
                total_read = io.ReadTransferCount
                total_write = io.WriteTransferCount

                if elapsed > 0.4:
                    diff_read = max(0, total_read - self.last_read_bytes)
                    diff_write = max(0, total_write - self.last_write_bytes)
                    self.download_speed = diff_read / elapsed
                    self.upload_speed = diff_write / elapsed
                    self.last_read_bytes = total_read
                    self.last_write_bytes = total_write
                    self.last_check_time = now
        except Exception:
            pass

        return {
            "running": True,
            "download_speed_str": format_speed(self.download_speed),
            "upload_speed_str": format_speed(self.upload_speed),
            "download_speed": int(self.download_speed),
            "upload_speed": int(self.upload_speed),
            "total_read": total_read,
            "total_write": total_write
        }
