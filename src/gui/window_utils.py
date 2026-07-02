import ctypes
import sys


def set_dark_titlebar(window):
    # Seteaza titlebar-ul ferestrei in Dark Mode

    if sys.platform == "win32":
        try:
            hwnd = int(window.winId())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            DWMWA_USE_IMMERSIVE_DARK_MODE_V2 = 19

            value = ctypes.c_int(2)  # 2 = enable
            res = ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
            if res != 0:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_V2, ctypes.byref(value), ctypes.sizeof(value))
        except Exception as e:
            pass
