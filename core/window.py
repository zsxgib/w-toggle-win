"""
窗口管理模块
负责窗口枚举、toggle 功能
"""
import os
import re
import win32gui
import win32con
import win32process
import psutil

# Windows API 常量
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
MAX_PATH = 260

# 使用 ctypes 加载 Windows API
kernel32 = __import__('ctypes').windll.kernel32

# class_name 到进程名的映射表
CLASS_NAME_TO_PROCNAME = {
    'Chrome_WidgetWin_1': 'Chrome',
    'Chrome_WidgetWin_2': 'Chrome',
    'Chrome_WidgetWin_3': 'Chrome',
    'Chrome_RenderWidgetHostHWND': 'Chrome',
    'MozillaDialogClass': 'Firefox',
    'MozillaWindowClass': 'Firefox',
    'AfxFrameOrView': 'Firefox',
    'WeChatLoginWnd': 'WeChat',
    'Qt51514QWindowIcon': 'WeChat',
    'Qt5152QWindowIcon': 'WeChat',
    'Qt5152QWindowToolSaveBits': 'AliWangWang',
    'AliWangWangDesktop': 'AliWangWang',
    'CASCADIA_HOSTING_WINDOW_CLASS': 'Terminal',
    'CabinetWClass': 'Explorer',
    'Progman': 'Explorer',
    'ApplicationFrameWindow': 'App',
    'Windows.UI.Core.CoreWindow': 'App',
    'WinUIDesktopWin32WindowClass': 'App',
    'SunAwtFrame': 'CrossPaste',
    'Notepad++': 'Notepad++',
    'emeditor': 'EmEditor',
    'SessionDetailWindowClass': 'Steam',
    'UnityContainerClass': 'Unity',
    'UnrealWindows': 'Unreal',
}

# 跳过后台/系统窗口 class names
SKIP_CLASS_NAMES = {
    'Default IME',
    'MSCTFIME UI',
    'CiceroUIWndFrame',
    'IME',
    'GDI+ Hook Window Class',
    'Dwm',
    '.NET-BroadcastEventWindow',
    '_q_titlebar',
    'adpsdknotification',
    'BluetoothNotificationAreaIconWindowClass',
    'CConnectionProvider_Class',
    'COMTASKSWINDOWCLASS',
    'CrossDeviceResumeWindowClass',
    'H.NotifyIcon',
    'Microsoft.UI.Content.PopupWindowSiteBridge',
    'MiracastConnectionWindow',
    'MS_WebcheckMonitor',
    'NvContainerWindowClass',
    'NVIDIA WMI Provider',
    'NVSVC64.DLL',
    'OleDdeWndClass',
    'PToyTrayIconWindow',
    'PushNotificationsPowerManagement',
    'PyInstallerOnefileHiddenWindow',
    'Qt51514WxTrayIconMessageWindowClass',
    'Qt5152TrayIconMessageWindowClass',
    'Qt6102TrayIconMessageWindowClass',
    'Qt6110TrayIconMessageWindowClass',
    'Qt643TrayIconMessageWindowClass',
    'Qt653TrayIconMessageWindowClass',
    'RealtekAudioAdminBackgroundProcessClass',
    'RealtekAudioBackgroundProcessClass',
    'SunAwtToolkit',
    'SunAwtTrayIcon',
    'SystemTray_Main',
    'TopLevelWindowForOverflowXamlIsland',
    'UxdService',
    'wingetWindow',
    'XamlExplorerHostIslandWindow',
}

# 跳过标题关键词（这些不是用户窗口）
SKIP_TITLE_KEYWORDS = {
    'toast 通知', 'PopupHost', 'Task Switching',
    'System tray overflow', 'Battery Meter',
    'DesktopWindowXamlSource', 'WinUI Desktop',
    'Windows Input Experience', 'FancyZones',
    'Find My Mouse', 'Mouse Highlighter',
    'H.NotifyIcon_', 'NvContainerWindowClass',
    'FLUTTER_RUNNER_WIN32_WINDOW', 'LocalSend',
    'WindowsForms10.Window', 'Coremail',
    'QuickSearchOptions', 'AIGlobalEntryFrame',
    'PopupMessageWindow', 'WindowsForms',
    'panel', '提醒',
    'Hotkeys', 'msedgewebview',
    'Settings',  # 系统设置窗口
    '命令面板',  # 系统命令面板
    'Window Toggle',  # 自己的应用
    'window-toggle',
    'ShareX',  # 截图工具后台窗口
    'Intel',  # Intel 后台窗口
}


def get_process_name(hwnd):
    """
    获取窗口对应的进程名
    Args:
        hwnd: 窗口句柄
    Returns:
        str: 进程名（如 "Chrome", "WeChat"）或 None
    """
    try:
        # 获取窗口所属的进程 ID
        pid = win32process.GetWindowThreadProcessId(hwnd)[0]

        # 先尝试用 psutil（更快）
        try:
            process = psutil.Process(pid)
            name = process.name()
            if name.lower().endswith('.exe'):
                name = name[:-4]
            return name
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

        # psutil 失败时，使用 Windows API
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return None

        try:
            name_buf = __import__('ctypes').create_unicode_buffer(MAX_PATH)
            size = __import__('ctypes').byref(__import__('ctypes').c_uint(MAX_PATH))

            if kernel32.QueryFullProcessImageNameW(handle, 0, name_buf, size):
                return os.path.basename(name_buf.value).lower().replace('.exe', '')
        finally:
            kernel32.CloseHandle(handle)

        return None
    except Exception:
        return None


def get_display_name(hwnd, class_name, title):
    """
    获取用于显示的进程名
    优先级: 1.从标题推断 2.通过class_name映射 3.尝试获取进程名 4.class_name
    """
    # 1. 尝试从标题推断进程名
    if title:
        title_lower = title.lower()
        if 'microsoft edge' in title_lower or 'msedge' in title_lower:
            return 'Edge'
        if ' - google chrome' in title_lower or ' - chrome' in title_lower:
            return 'Chrome'
        if 'mozilla firefox' in title_lower:
            return 'Firefox'
        if 'visual studio' in title_lower or 'visualstudio' in title_lower:
            return 'Visual Studio'
        if 'jetbrains' in title_lower:
            return 'JetBrains'
        if 'notepad++' in title_lower:
            return 'Notepad++'
        if 'powershell' in title_lower:
            return 'PowerShell'
        if 'visual studio code' in title_lower or 'vscode' in title_lower:
            return 'VSCode'
        if 'windows terminal' in title_lower:
            return 'Windows Terminal'
        if title_lower == 'claude':
            return 'Claude'
        if title_lower == 'windows terminal':
            return 'Windows Terminal'

    # 2. 通过 class_name 映射
    if class_name in CLASS_NAME_TO_PROCNAME:
        return CLASS_NAME_TO_PROCNAME[class_name]

    # 3. 尝试获取进程名
    proc_name = get_process_name(hwnd)
    if proc_name:
        return proc_name

    # 4. 返回 class_name
    return class_name


def get_all_windows():
    """
    获取所有顶层窗口（包括隐藏的，但过滤掉后台进程窗口）
    Returns:
        list: 窗口信息列表
    """
    windows = []

    def enum_callback(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return True

        class_name = win32gui.GetClassName(hwnd)

        # 跳过已知的后台窗口 class（完全匹配）
        if class_name in SKIP_CLASS_NAMES:
            return True

        # 跳过前缀匹配的后台窗口（如 HwndWrapper[Listary.exe;;...]）
        skip_prefixes = [
            'HwndWrapper[', 'WavesGenericWindow_', 'WavesNotifications',
            '.NET-BroadcastEventWindow', 'Qt5', 'Qt6', 'RealtekAudio',
        ]
        for prefix in skip_prefixes:
            if class_name.startswith(prefix):
                return True

        # 跳过窗口标题很短的（通常是后台进程）
        if len(title.strip()) < 3:
            return True

        # 跳过包含后台关键词的标题
        for keyword in SKIP_TITLE_KEYWORDS:
            if keyword in title:
                return True

        # 使用 display_name 来显示（支持从标题和 class_name 推断）
        display_name = get_display_name(hwnd, class_name, title)
        windows.append({
            'hwnd': hwnd,
            'title': title,
            'class_name': class_name,
            'process_name': display_name
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

    # Windows Terminal 特殊处理
    title = win32gui.GetWindowText(hwnd)
    if 'Windows Terminal' in title:
        # 查找同进程的 CASCADIA_HOSTING_WINDOW_CLASS 窗口
        pid = win32process.GetWindowThreadProcessId(hwnd)[0]
        target = [hwnd]  # 默认用主窗口

        def find_cascadia(h, _):
            if h == hwnd:
                return True
            try:
                if win32process.GetWindowThreadProcessId(h)[0] != pid:
                    return True
            except:
                return True
            cls = win32gui.GetClassName(h)
            if cls == 'CASCADIA_HOSTING_WINDOW_CLASS':
                print(f"[toggle] Windows Terminal: found cascadia hwnd={h}")
                target[0] = h
                return False
            return True

        win32gui.EnumWindows(find_cascadia, None)

        hwnd_to_use = target[0]
        print(f"[toggle] Using hwnd={hwnd_to_use}")

        # 检查这个窗口的状态
        placement2 = win32gui.GetWindowPlacement(hwnd_to_use)
        show_cmd2 = placement2[1]
        minimized2 = (show_cmd2 == win32con.SW_SHOWMINIMIZED)
        print(f"[toggle] Target showCmd={show_cmd2}, minimized={minimized2}")

        if minimized2:
            win32gui.ShowWindow(hwnd_to_use, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd_to_use)
            print(f"[toggle] Restored cascadia window")
        else:
            win32gui.ShowWindow(hwnd_to_use, win32con.SW_MINIMIZE)
            print(f"[toggle] Minimized cascadia window")
        return True

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
