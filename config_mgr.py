"""
NexHub Persistent Configuration Manager
Stores full themes, custom gradients, colors, blur, animation speed, and Zapret presets.
"""

import os
import json

DEFAULT_CONFIG = {
    "language": "ru",
    "theme": {
        "accent_color": "#3b82f6",
        "theme_name": "theme-dark",
        "gradient_type": "radial",
        "glow_intensity": 75,
        "blur_amount": 16,
        "animations": True
    },
    "zapret": {
        "folder": r"D:\Azapret-discord-youtube-1.10.3",
        "preset": "general (ALT11).bat"
    }
}

def get_config_dir() -> str:
    appdata = os.environ.get("APPDATA")
    if appdata:
        cfg_dir = os.path.join(appdata, "NexHub")
    else:
        cfg_dir = os.path.expanduser(r"~\.nexhub")
    os.makedirs(cfg_dir, exist_ok=True)
    return cfg_dir

def get_config_path() -> str:
    return os.path.join(get_config_dir(), "nexhub_config.json")

def load_config() -> dict:
    path = get_config_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
                config = dict(DEFAULT_CONFIG)
                for k, v in saved.items():
                    if isinstance(v, dict) and k in config and isinstance(config[k], dict):
                        config[k].update(v)
                    else:
                        config[k] = v
                return config
        except Exception as e:
            print("Error loading config:", e)
    return dict(DEFAULT_CONFIG)

def save_config(config: dict) -> bool:
    path = get_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print("Error saving config:", e)
        return False
