"""
窗口管理模块
负责窗口枚举、toggle 功能
"""
import win32gui
import win32con
import win32process
import psutil
import ctypes
from ctypes import wintypes
import os

# 图标缓存
_icon_cache = {}


def get_all_windows():
    """
    获取所有可见顶层窗口
    Returns:
        list: 窗口信息列表
    """
    import logging
    logger = logging.getLogger(__name__)

    logger.info("[get_all_windows] Starting")
    windows = []

    def enum_callback(hwnd, _):
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return True

            title = win32gui.GetWindowText(hwnd)
            if not title:
                return True

            class_name = win32gui.GetClassName(hwnd)
            windows.append({
                'hwnd': hwnd,
                'title': title,
                'class_name': class_name
            })
            logger.info(f"[get_all_windows] Found window: {title} ({class_name})")
            return True
        except Exception as e:
            logger.error(f"[get_all_windows] Error in callback: {e}")
            return True

    logger.info("[get_all_windows] Calling EnumWindows")
    win32gui.EnumWindows(enum_callback, None)
    logger.info(f"[get_all_windows] Finished, found {len(windows)} windows")
    return windows


def group_by_class(windows):
    """
    按窗口类名分组
    Args:
        windows: 窗口信息列表
    Returns:
        dict: {class_name: [window_info, ...]}
    """
    groups = {}
    for w in windows:
        class_name = w['class_name']
        if class_name not in groups:
            groups[class_name] = []
        groups[class_name].append(w)
    return groups


def is_valid_window(hwnd):
    """检查窗口句柄是否有效"""
    if not hwnd:
        return False
    return win32gui.IsWindow(hwnd)


def toggle_window(hwnd):
    """
    切换窗口显示/隐藏
    使用 GetWindowPlacement 检测窗口状态
    """
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"[toggle] Starting toggle for hwnd={hwnd}")

    try:
        if not win32gui.IsWindow(hwnd):
            logger.error(f"[toggle] Not a valid window: {hwnd}")
            return False

        logger.info("[toggle] Getting window placement")
        placement = win32gui.GetWindowPlacement(hwnd)
        show_cmd = placement[1]
        minimized = (show_cmd == win32con.SW_SHOWMINIMIZED)

        logger.info(f"[toggle] hwnd={hwnd}, showCmd={show_cmd}, minimized={minimized}")

        if minimized:
            if show_cmd == win32con.SW_SHOWMAXIMIZED:
                logger.info("[toggle] Restoring maximized window")
                win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED)
            else:
                logger.info("[toggle] Restoring normal window")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            logger.info("[toggle] Window restored")
        else:
            logger.info("[toggle] Minimizing window")
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            logger.info("[toggle] Window minimized")

        return True

    except Exception as e:
        logger.error(f"[toggle] Error in toggle_window: {e}", exc_info=True)
        return False


def find_window_by_class(window_class):
    """通过窗口类名查找窗口"""
    windows = get_all_windows()
    for w in windows:
        if w['class_name'] == window_class:
            return w['hwnd']
    return None


def get_window_process_info(hwnd):
    """
    获取窗口对应的进程信息
    Args:
        hwnd: 窗口句柄
    Returns:
        dict: {'pid': int, 'exe_path': str, 'process_name': str} 或 None
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        pid = win32process.GetWindowThreadProcessId(hwnd)[1]  # [1] 是 process_id
        logger.info(f"[get_window_process_info] hwnd={hwnd}, pid={pid}")
        process = psutil.Process(pid)
        result = {
            'pid': pid,
            'exe_path': process.exe(),
            'process_name': process.name()
        }
        logger.info(f"[get_window_process_info] success: {result}")
        return result
    except Exception as e:
        logger.warning(f"[get_window_process_info] failed for hwnd={hwnd}: {e}")
        return None


def get_process_icon(exe_path, size=24):
    """
    获取进程的可执行文件图标
    Args:
        exe_path: 可执行文件路径
        size: 图标大小
    Returns:
        QIcon 或 None
    """
    if not exe_path or not os.path.exists(exe_path):
        return None

    # 检查缓存
    cache_key = f"{exe_path}_{size}"
    if cache_key in _icon_cache:
        return _icon_cache[cache_key]

    try:
        # 获取 HICON
        hicon = _get_hicon_from_file(exe_path)
        if not hicon:
            return None

        # 转换为 QIcon
        qicon = _hicon_to_qicon(hicon, size)

        # 缓存图标
        if qicon:
            _icon_cache[cache_key] = qicon

        return qicon

    except Exception as e:
        print(f"[window] Failed to get process icon: {e}")
        return None


def _get_hicon_from_file(exe_path):
    """使用 SHGetFileInfo 获取 HICON"""
    # 定义 SHFILEINFO 结构体
    class SHFILEINFO(ctypes.Structure):
        _fields_ = [
            ("hIcon", wintypes.HICON),
            ("iIcon", wintypes.INT),
            ("dwAttributes", wintypes.DWORD),
            ("szDisplayName", wintypes.WCHAR * 260),
            ("szTypeName", wintypes.WCHAR * 80)
        ]

    shell32 = ctypes.windll.shell32
    SHGetFileInfoW = shell32.SHGetFileInfoW

    # 设置参数类型
    SHGetFileInfoW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        ctypes.POINTER(SHFILEINFO),
        wintypes.UINT,
        wintypes.UINT
    ]
    SHGetFileInfoW.restype = wintypes.HICON

    # 图标标志
    SHGFI_ICON = 0x000000100
    SHGFI_SMALLICON = 0x000000001

    # 获取图标
    sfi = SHFILEINFO()
    result = SHGetFileInfoW(
        exe_path,
        0,
        ctypes.byref(sfi),
        ctypes.sizeof(sfi),
        SHGFI_ICON | SHGFI_SMALLICON
    )

    if result and sfi.hIcon:
        return sfi.hIcon
    return None


def _hicon_to_qicon(hicon, size=24):
    """将 HICON 转换为 QIcon - 使用更简单的 PIL 方式"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"[icon] Starting icon conversion, hicon={hicon}, size={size}")

    try:
        from PIL import Image
        import numpy as np
        from PyQt6.QtGui import QIcon, QPixmap, QImage
        logger.info("[icon] Imports successful")
    except ImportError as e:
        logger.error(f"[icon] Import error: {e}")
        return None

    try:
        # 使用更简单的方式: 直接用 PIL 读取图标
        # 使用 Windows API 来获取图标数据
        import struct

        # 创建内存 DC 并绘制图标
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32

        # 获取图标位图
        hdc = user32.GetDC(0)
        memdc = gdi32.CreateCompatibleDC(hdc)
        hbmp = gdi32.CreateCompatibleBitmap(hdc, size, size)
        gdi32.SelectObject(memdc, hbmp)

        # 绘制图标
        user32.DrawIconEx(memdc, 0, 0, hicon, size, size, 0, 0, 3)

        # 获取位图数据
        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ("biSize", ctypes.c_ulong),
                ("biWidth", ctypes.c_long),
                ("biHeight", ctypes.c_long),
                ("biPlanes", ctypes.c_short),
                ("biBitCount", ctypes.c_short),
                ("biCompression", ctypes.c_ulong),
                ("biSizeImage", ctypes.c_ulong),
                ("biXPels", ctypes.c_long),
                ("biYPels", ctypes.c_long),
                ("biClrUsed", ctypes.c_ulong),
                ("biClrImportant", ctypes.c_ulong)
            ]

        bmi = BITMAPINFOHEADER()
        bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.biWidth = size
        bmi.biHeight = -size
        bmi.biPlanes = 1
        bmi.biBitCount = 32

        buf = ctypes.create_string_buffer(size * size * 4)
        gdi32.GetDIBits(memdc, hbmp, 0, size, buf, ctypes.byref(bmi), 0)

        # 清理
        gdi32.DeleteObject(hbmp)
        gdi32.DeleteDC(memdc)
        user32.ReleaseDC(0, hdc)

        # 转换为 PIL Image
        img_array = np.frombuffer(buf, dtype=np.uint8)
        img_array = img_array.reshape((size, size, 4))
        # BGRA 转 RGBA
        img_array = img_array[:, :, [2, 1, 0, 3]]

        img = Image.fromarray(img_array, 'RGBA')

        # 转换为 QImage
        img_data = img.tobytes()
        qimage = QImage(img_data, size, size, QImage.Format.Format_RGBA8888)

        pixmap = QPixmap.fromImage(qimage)
        icon = QIcon(pixmap)

        logger.info(f"[icon] Created QIcon successfully")
        return icon

    except Exception as e:
        logger.error(f"[icon] Icon conversion failed: {e}", exc_info=True)
        return None


def get_window_icon(hwnd):
    """
    获取窗口图标（通过进程图标）
    Args:
        hwnd: 窗口句柄
    Returns:
        QIcon 或 None
    """
    info = get_window_process_info(hwnd)
    if info and info['exe_path']:
        return get_process_icon(info['exe_path'])
    return None
