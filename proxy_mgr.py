"""
NexHub Windows System Proxy Manager
Enables or disables system-wide HTTP/HTTPS proxy via Windows Registry and WinINet API.
"""

import winreg
import ctypes
from ctypes import wintypes

INTERNET_SETTINGS = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
INTERNET_OPTION_SETTINGS_CHANGED = 39
INTERNET_OPTION_REFRESH = 37

def set_system_proxy(enable: bool, host: str = "127.0.0.1", port: int = 10809) -> bool:
    """Sets or clears Windows system proxy."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, INTERNET_SETTINGS, 0, winreg.KEY_WRITE) as key:
            if enable:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, f"{host}:{port}")
                winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, "<local>;localhost;127.*;192.168.*")
            else:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
        
        # Notify WinINet
        try:
            ctypes.windll.wininet.InternetSetOptionW(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
            ctypes.windll.wininet.InternetSetOptionW(0, INTERNET_OPTION_REFRESH, 0, 0)
        except Exception as e:
            print("WinINet notify error:", e)
            
        return True
    except Exception as e:
        print("System proxy error:", e)
        return False

def get_system_proxy_status() -> dict:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, INTERNET_SETTINGS, 0, winreg.KEY_READ) as key:
            try:
                enabled, _ = winreg.QueryValueEx(key, "ProxyEnable")
            except Exception:
                enabled = 0
            try:
                server, _ = winreg.QueryValueEx(key, "ProxyServer")
            except Exception:
                server = ""
        return {"enabled": bool(enabled), "server": server}
    except Exception:
        return {"enabled": False, "server": ""}
