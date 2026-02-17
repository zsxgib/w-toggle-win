"""
窗口管理模块
负责窗口枚举、toggle 功能
"""
import win32gui
import win32con


def get_all_windows():
    """
    获取所有可见顶层窗口
    Returns:
        list: 窗口信息列表
    """
    windows = []

    def enum_callback(hwnd, _):
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
        return True

    win32gui.EnumWindows(enum_callback, None)
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
    if not win32gui.IsWindow(hwnd):
        return False

    placement = win32gui.GetWindowPlacement(hwnd)
    show_cmd = placement[1]
    minimized = (show_cmd == win32con.SW_SHOWMINIMIZED)

    print(f"[toggle] hwnd={hwnd}, showCmd={show_cmd}, minimized={minimized}")

    if minimized:
        if show_cmd == win32con.SW_SHOWMAXIMIZED:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED)
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        print(f"[toggle] Restored window")
    else:
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        print(f"[toggle] Minimized window")

    return True


def find_window_by_class(window_class):
    """通过窗口类名查找窗口"""
    windows = get_all_windows()
    for w in windows:
        if w['class_name'] == window_class:
            return w['hwnd']
    return None
