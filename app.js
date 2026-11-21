/**
 * NexHub Zapret Studio - Interactive UI & Customization Engine
 * Rock-solid stability, zero UI latency, fluid 60 FPS transitions.
 */

const I18N = {
  ru: {
    nav_zapret: "Главная (Запрет)",
    nav_settings: "Настройки и Тема",
    status_ready: "Готов",
    zapret_title: "Обход замедлений <span class=\"text-accent\">Discord & YouTube</span>",
    zapret_subtitle: "Автономная защита видеопотоков, голосовых комнат и стримов через WinDivert",
    btn_fullscreen: "Полноэкранный режим",
    warn_folder_title: "Папка Azapret не найдена на этом ПК",
    warn_folder_desc: "Укажите папку с winws.exe и .bat файлами для работы обхода",
    btn_choose_folder: "Выбрать папку",
    zapret_status_inactive: "ЗАПРЕТ ВЫКЛЮЧЕН",
    zapret_status_active: "ЗАПРЕТ АКТИВЕН",
    zapret_status_sub_inactive: "Нажмите кнопку, чтобы запустить обход блокировок",
    zapret_status_sub_active: "Служба winws.exe запущена и защищает трафик",
    zapret_preset_title: "Пресет запуска (.bat)",
    zapret_preset_sub: "Выберите bat-файл из вашей папки Azapret",
    btn_apply_preset: "Запустить пресет",
    btn_stop: "Остановить",
    zapret_diag_title: "Диагностика службы",
    diag_proc: "Процесс winws:",
    diag_driver: "Драйвер WinDivert:",
    diag_folder: "Каталог:",
    btn_open_folder: "В Проводнике",
    settings_title: "Студия Кастомизации и Настроек",
    settings_subtitle: "Настройте любые цвета, тему, градиенты, интенсивность свечения и размытия",
    set_accent_title: "Акцентный цвет (Accent Color)",
    set_accent_hint: "Выберите цвет из палитры или укажите любой свой оттенок",
    lbl_custom_color: "Свой цвет",
    set_theme_mode: "Стиль темы оформления",
    set_theme_mode_hint: "Базовый тон фона приложения",
    set_effects_title: "Градиент и Неоновое свечение",
    set_effects_hint: "Настройка атмосферных световых эффектов и размытия",
    lbl_glow_intensity: "Интенсивность неонового свечения:",
    lbl_blur_amount: "Степень размытия карточек (Backdrop Blur):",
    lbl_gradient_type: "Тип фонового градиента:",
    grad_radial: "Неоновые сферы",
    grad_aurora: "Аврора (Aurora)",
    grad_linear: "Линейный",
    grad_flat: "Без градиента (Flat)",
    lbl_animations: "Плавные 60 FPS анимации интерфейса",
    lbl_animations_hint: "Отключите для максимальной производительности на слабых ПК",
    set_system_title: "Язык и Пути",
    set_system_hint: "Выбор языка интерфейса и папки Azapret",
    lbl_zapret_path: "Путь к папке Azapret:"
  },
  en: {
    nav_zapret: "Home (Zapret)",
    nav_settings: "Settings & Theme",
    status_ready: "Ready",
    zapret_title: "DPI Bypass <span class=\"text-accent\">Discord & YouTube</span>",
    zapret_subtitle: "Autonomous traffic protection for voice rooms, streams, and 4K video via WinDivert",
    btn_fullscreen: "Fullscreen Mode",
    warn_folder_title: "Azapret folder not found on this PC",
    warn_folder_desc: "Please locate the folder containing winws.exe and .bat preset scripts",
    btn_choose_folder: "Locate Folder",
    zapret_status_inactive: "ZAPRET INACTIVE",
    zapret_status_active: "ZAPRET ACTIVE",
    zapret_status_sub_inactive: "Click the button to start DPI bypass",
    zapret_status_sub_active: "winws.exe service is actively running and filtering traffic",
    zapret_preset_title: "Startup Preset (.bat)",
    zapret_preset_sub: "Choose a bat-file from Azapret folder",
    btn_apply_preset: "Launch Preset",
    btn_stop: "Stop",
    zapret_diag_title: "Service Diagnostics",
    diag_proc: "winws Process:",
    diag_driver: "WinDivert Driver:",
    diag_folder: "Directory:",
    btn_open_folder: "Open Explorer",
    settings_title: "Customization & Theme Studio",
    settings_subtitle: "Personalize colors, themes, gradients, glow intensity, and backdrop blur",
    set_accent_title: "Accent Color",
    set_accent_hint: "Choose from curated presets or pick any custom hex shade",
    lbl_custom_color: "Custom",
    set_theme_mode: "Base Theme Style",
    set_theme_mode_hint: "Primary background tone",
    set_effects_title: "Gradient & Neon Glow Effects",
    set_effects_hint: "Fine-tune atmosphere lighting, glows, and blur",
    lbl_glow_intensity: "Neon Glow Intensity:",
    lbl_blur_amount: "Card Backdrop Blur:",
    lbl_gradient_type: "Background Gradient Type:",
    grad_radial: "Neon Spheres",
    grad_aurora: "Aurora Mesh",
    grad_linear: "Angled Linear",
    grad_flat: "Pure Flat",
    lbl_animations: "Fluid 60 FPS UI Animations",
    lbl_animations_hint: "Disable to optimize for low-spec PCs",
    set_system_title: "Language & Paths",
    set_system_hint: "Interface language and Azapret directory",
    lbl_zapret_path: "Azapret Folder Path:"
  }
};

let currentLang = "ru";
let appConfig = null;
let isZapretRunning = false;
let isPolling = false;
let isActionPending = false;
let isFolderDialogOpen = false;

// Debounced save for slider and color inputs
let saveCustomizationTimer = null;
function debouncedSaveCustomization(data) {
  if (saveCustomizationTimer) clearTimeout(saveCustomizationTimer);
  saveCustomizationTimer = setTimeout(() => {
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.save_customization(data).catch(() => {});
    }
  }, 250);
}

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerText = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(8px)";
    setTimeout(() => toast.remove(), 250);
  }, 2800);
}

function applyLanguage(lang) {
  currentLang = lang;
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (I18N[lang] && I18N[lang][key]) {
      el.innerHTML = I18N[lang][key];
    }
  });

  document.querySelectorAll(".btn-lang").forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-lang") === lang);
  });
}

function applyCustomization(themeData) {
  if (!themeData) return;

  // Accent Color
  if (themeData.accent_color) {
    const color = themeData.accent_color;
    document.documentElement.style.setProperty("--accent-color", color);
    const rgb = hexToRgb(color);
    if (rgb) {
      document.documentElement.style.setProperty("--accent-rgb", `${rgb.r}, ${rgb.g}, ${rgb.b}`);
      document.documentElement.style.setProperty("--accent-glow", `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.45)`);
      document.documentElement.style.setProperty("--accent-gradient", `linear-gradient(135deg, ${color} 0%, rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.75) 100%)`);
    }

    document.querySelectorAll(".color-circle").forEach(c => {
      c.classList.toggle("active", c.getAttribute("data-color").toLowerCase() === color.toLowerCase());
    });
    const cp = document.getElementById("input-custom-color");
    if (cp && cp.value.toLowerCase() !== color.toLowerCase()) {
      cp.value = color;
    }
  }

  // Base Theme
  if (themeData.theme_name) {
    const existingGrad = document.body.classList.contains("grad-aurora") ? "grad-aurora" :
                         document.body.classList.contains("grad-linear") ? "grad-linear" :
                         document.body.classList.contains("grad-flat") ? "grad-flat" : "grad-radial";
    document.body.className = `${themeData.theme_name} ${existingGrad}`;
    document.querySelectorAll(".btn-theme-opt").forEach(btn => {
      btn.classList.toggle("active", btn.getAttribute("data-theme") === themeData.theme_name);
    });
  }

  // Gradient Type
  if (themeData.gradient_type) {
    document.body.classList.remove("grad-radial", "grad-aurora", "grad-linear", "grad-flat");
    document.body.classList.add(`grad-${themeData.gradient_type}`);
    document.querySelectorAll(".btn-grad-type").forEach(btn => {
      btn.classList.toggle("active", btn.getAttribute("data-grad") === themeData.gradient_type);
    });
  }

  // Glow Intensity
  if (themeData.glow_intensity !== undefined) {
    const val = themeData.glow_intensity;
    document.documentElement.style.setProperty("--glow-opacity", `${val / 100}`);
    const r = document.getElementById("range-glow-intensity");
    if (r) r.value = val;
    const l = document.getElementById("val-glow-intensity");
    if (l) l.innerText = `${val}%`;
  }

  // Blur Amount
  if (themeData.blur_amount !== undefined) {
    const val = themeData.blur_amount;
    document.documentElement.style.setProperty("--blur-amount", `${val}px`);
    const r = document.getElementById("range-blur-amount");
    if (r) r.value = val;
    const l = document.getElementById("val-blur-amount");
    if (l) l.innerText = `${val}px`;
  }

  // Animations
  if (themeData.animations !== undefined) {
    const c = document.getElementById("check-animations");
    if (c) c.checked = themeData.animations;
    if (!themeData.animations) {
      document.documentElement.style.setProperty("--transition-fast", "0s");
      document.documentElement.style.setProperty("--transition-smooth", "0s");
    } else {
      document.documentElement.style.setProperty("--transition-fast", "0.16s cubic-bezier(0.16, 1, 0.3, 1)");
      document.documentElement.style.setProperty("--transition-smooth", "0.24s cubic-bezier(0.16, 1, 0.3, 1)");
    }
  }
}

function hexToRgb(hex) {
  let c = hex.replace('#', '');
  if (c.length === 3) c = c.split('').map(x => x + x).join('');
  const num = parseInt(c, 16);
  return isNaN(num) ? null : { r: (num >> 16) & 255, g: (num >> 8) & 255, b: num & 255 };
}

async function toggleZapret() {
  if (isActionPending) return;
  isActionPending = true;

  const batSelect = document.getElementById("select-zapret-bat");
  const batName = batSelect ? batSelect.value : "general.bat";

  try {
    if (isZapretRunning) {
      if (window.pywebview && window.pywebview.api) {
        const res = await window.pywebview.api.stop_zapret();
        if (res && res.success) {
          setZapretUiState(false);
          showToast(currentLang === "ru" ? "Служба Запрет выключена" : "Zapret service stopped");
        } else {
          showToast(res ? res.message : "Ошибка остановки", "danger");
        }
      } else {
        setZapretUiState(false);
        showToast("Запрет выключен (Демо)");
      }
    } else {
      if (window.pywebview && window.pywebview.api) {
        const res = await window.pywebview.api.start_zapret(batName);
        if (res && res.success) {
          showToast(currentLang === "ru" ? `Запуск пресета: ${batName}...` : `Launching: ${batName}...`, "info");
        } else {
          showToast(res ? res.message : "Ошибка запуска", "danger");
        }
      } else {
        setZapretUiState(true);
        showToast("Запрет запущен (Демо)");
      }
    }
  } catch (err) {
    console.error("toggleZapret error:", err);
  } finally {
    setTimeout(() => {
      isActionPending = false;
    }, 350);
  }
}

async function stopZapretDirect() {
  if (isActionPending) return;
  isActionPending = true;
  try {
    if (window.pywebview && window.pywebview.api) {
      await window.pywebview.api.stop_zapret();
    }
    setZapretUiState(false);
    showToast(currentLang === "ru" ? "Служба остановлена" : "Service stopped");
  } catch (err) {
    console.error("stopZapretDirect error:", err);
  } finally {
    setTimeout(() => {
      isActionPending = false;
    }, 350);
  }
}

function setZapretUiState(running) {
  isZapretRunning = running;
  const btn = document.getElementById("btn-zapret-toggle");
  const zapretDot = document.getElementById("zapret-dot");
  const statusTitle = document.getElementById("zapret-status-title");
  const statusSub = document.getElementById("zapret-status-sub");
  const diagStatus = document.getElementById("diag-winws-status");
  const netDot = document.getElementById("network-dot");
  const netStatus = document.getElementById("network-status");

  if (running) {
    if (btn) btn.classList.add("active");
    if (zapretDot) zapretDot.classList.add("active");
    if (statusTitle) {
      statusTitle.innerText = currentLang === "ru" ? "ЗАПРЕТ АКТИВЕН" : "ZAPRET ACTIVE";
      statusTitle.style.color = "var(--success-color)";
    }
    if (statusSub) {
      statusSub.innerText = currentLang === "ru" ? "Служба winws.exe запущена и защищает трафик" : "winws.exe is actively running and filtering traffic";
    }
    if (diagStatus) {
      diagStatus.innerText = currentLang === "ru" ? "Работает (winws.exe)" : "Running (winws.exe)";
      diagStatus.className = "d-val status-val active";
    }
    if (netDot) netDot.className = "status-dot active";
    if (netStatus) netStatus.innerText = currentLang === "ru" ? "Защищено" : "Protected";
  } else {
    if (btn) btn.classList.remove("active");
    if (zapretDot) zapretDot.classList.remove("active");
    if (statusTitle) {
      statusTitle.innerText = currentLang === "ru" ? "ЗАПРЕТ ВЫКЛЮЧЕН" : "ZAPRET INACTIVE";
      statusTitle.style.color = "var(--text-main)";
    }
    if (statusSub) {
      statusSub.innerText = currentLang === "ru" ? "Нажмите кнопку, чтобы запустить обход блокировок" : "Click button to start DPI bypass";
    }
    if (diagStatus) {
      diagStatus.innerText = currentLang === "ru" ? "Остановлен" : "Stopped";
      diagStatus.className = "d-val status-val";
    }
    if (netDot) netDot.className = "status-dot";
    if (netStatus) netStatus.innerText = currentLang === "ru" ? "Готов" : "Ready";
  }
}

async function handleChooseFolder() {
  if (isFolderDialogOpen) return;
  isFolderDialogOpen = true;

  try {
    if (window.pywebview && window.pywebview.api) {
      const res = await window.pywebview.api.choose_zapret_folder();
      if (res && res.success) {
        document.getElementById("diag-folder-path").innerText = res.folder;
        document.getElementById("input-zapret-folder").value = res.folder;
        document.getElementById("zapret-folder-warning").style.display = "none";

        const sel = document.getElementById("select-zapret-bat");
        sel.innerHTML = "";
        res.presets.forEach(p => {
          const opt = document.createElement("option");
          opt.value = p;
          opt.innerText = p + (p === "general.bat" ? " (Рекомендуемый)" : "");
          sel.appendChild(opt);
        });
        showToast(currentLang === "ru" ? "Папка Azapret обновлена!" : "Azapret folder updated!", "success");
      }
    }
  } catch (err) {
    console.error("Choose folder error:", err);
  } finally {
    isFolderDialogOpen = false;
  }
}

async function pollLiveStatus() {
  if (isPolling) return;
  isPolling = true;

  try {
    if (window.pywebview && window.pywebview.api) {
      const status = await window.pywebview.api.get_live_status();
      if (status) {
        if (status.running !== isZapretRunning) {
          setZapretUiState(status.running);
        }
        const warn = document.getElementById("zapret-folder-warning");
        if (warn) {
          warn.style.display = status.folder_exists ? "none" : "flex";
        }
      }
    }
  } catch (err) {
    // Graceful silent recovery
  } finally {
    isPolling = false;
    setTimeout(pollLiveStatus, 1500);
  }
}

async function initApp() {
  // Navigation tabs
  document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", () => {
      const tabId = item.getAttribute("data-tab");
      document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      item.classList.add("active");
      const targetPane = document.getElementById(`pane-${tabId}`);
      if (targetPane) targetPane.classList.add("active");
    });
  });

  // Window Controls
  document.getElementById("btn-fullscreen").addEventListener("click", () => {
    if (window.pywebview && window.pywebview.api) window.pywebview.api.toggle_fullscreen().catch(() => {});
  });
  document.getElementById("btn-quick-fs").addEventListener("click", () => {
    if (window.pywebview && window.pywebview.api) window.pywebview.api.toggle_fullscreen().catch(() => {});
  });
  document.getElementById("btn-minimize").addEventListener("click", () => {
    if (window.pywebview && window.pywebview.api) window.pywebview.api.window_minimize();
  });
  document.getElementById("btn-maximize").addEventListener("click", () => {
    if (window.pywebview && window.pywebview.api) window.pywebview.api.window_maximize();
  });
  document.getElementById("btn-close").addEventListener("click", () => {
    if (window.pywebview && window.pywebview.api) window.pywebview.api.window_close();
  });

  // Keyboard shortcut F11 for Fullscreen
  window.addEventListener("keydown", (e) => {
    if (e.key === "F11") {
      e.preventDefault();
      if (window.pywebview && window.pywebview.api) window.pywebview.api.toggle_fullscreen().catch(() => {});
    }
  });

  // Main Power Toggle & Presets
  document.getElementById("btn-zapret-toggle").addEventListener("click", toggleZapret);
  document.getElementById("btn-zapret-run-preset").addEventListener("click", toggleZapret);
  document.getElementById("btn-zapret-stop").addEventListener("click", stopZapretDirect);

  // Folder Pickers
  document.getElementById("btn-browse-zapret-folder").addEventListener("click", handleChooseFolder);
  document.getElementById("btn-browse-zapret-folder-warn").addEventListener("click", handleChooseFolder);
  document.getElementById("btn-browse-folder-settings").addEventListener("click", handleChooseFolder);
  document.getElementById("btn-open-zapret-folder").addEventListener("click", () => {
    if (window.pywebview && window.pywebview.api) window.pywebview.api.open_zapret_folder().catch(() => {});
  });

  // Customization: Accent Colors
  document.querySelectorAll(".color-circle").forEach(circle => {
    circle.addEventListener("click", () => {
      const color = circle.getAttribute("data-color");
      applyCustomization({ accent_color: color });
      debouncedSaveCustomization({ accent_color: color });
    });
  });

  document.getElementById("input-custom-color").addEventListener("input", (e) => {
    const color = e.target.value;
    applyCustomization({ accent_color: color });
    debouncedSaveCustomization({ accent_color: color });
  });

  // Customization: Theme Mode
  document.querySelectorAll(".btn-theme-opt").forEach(btn => {
    btn.addEventListener("click", () => {
      const t = btn.getAttribute("data-theme");
      applyCustomization({ theme_name: t });
      debouncedSaveCustomization({ theme_name: t });
    });
  });

  // Customization: Gradient Types
  document.querySelectorAll(".btn-grad-type").forEach(btn => {
    btn.addEventListener("click", () => {
      const g = btn.getAttribute("data-grad");
      applyCustomization({ gradient_type: g });
      debouncedSaveCustomization({ gradient_type: g });
    });
  });

  // Customization: Glow Intensity Range (debounced)
  document.getElementById("range-glow-intensity").addEventListener("input", (e) => {
    const val = parseInt(e.target.value);
    applyCustomization({ glow_intensity: val });
    debouncedSaveCustomization({ glow_intensity: val });
  });

  // Customization: Backdrop Blur Range (debounced)
  document.getElementById("range-blur-amount").addEventListener("input", (e) => {
    const val = parseInt(e.target.value);
    applyCustomization({ blur_amount: val });
    debouncedSaveCustomization({ blur_amount: val });
  });

  // Customization: Animations Toggle
  document.getElementById("check-animations").addEventListener("change", (e) => {
    const checked = e.target.checked;
    applyCustomization({ animations: checked });
    debouncedSaveCustomization({ animations: checked });
  });

  // Languages
  document.querySelectorAll(".btn-lang").forEach(btn => {
    btn.addEventListener("click", () => {
      const lang = btn.getAttribute("data-lang");
      applyLanguage(lang);
      if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.save_language(lang).catch(() => {});
      }
    });
  });

  // Fetch initial data
  if (window.pywebview && window.pywebview.api) {
    try {
      const initData = await window.pywebview.api.get_initial_data();
      appConfig = initData.config || {};

      if (appConfig.language) applyLanguage(appConfig.language);
      if (appConfig.theme) applyCustomization(appConfig.theme);

      // Folder check
      const warn = document.getElementById("zapret-folder-warning");
      if (!initData.zapret_folder_exists) {
        warn.style.display = "flex";
      } else {
        warn.style.display = "none";
      }

      document.getElementById("diag-folder-path").innerText = initData.zapret_folder || "Не найден";
      document.getElementById("input-zapret-folder").value = initData.zapret_folder || "";

      const sel = document.getElementById("select-zapret-bat");
      if (sel && initData.zapret_presets) {
        sel.innerHTML = "";
        initData.zapret_presets.forEach(p => {
          const opt = document.createElement("option");
          opt.value = p;
          opt.innerText = p + (p === "general.bat" ? " (Рекомендуемый)" : "");
          sel.appendChild(opt);
        });
        if (appConfig.zapret && appConfig.zapret.preset) {
          sel.value = appConfig.zapret.preset;
        }
      }

      setZapretUiState(Boolean(initData.is_zapret_running));
    } catch (e) {
      console.error("Init data error:", e);
    }
  }

  // Start status polling
  setTimeout(pollLiveStatus, 1200);
}

window.addEventListener("pywebviewready", initApp);
window.addEventListener("DOMContentLoaded", () => {
  if (!window.pywebview) {
    setTimeout(initApp, 300);
  }
});
