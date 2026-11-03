"""
Window Toggle 主程序
使用 PyQt6 + ctypes RegisterHotKey
"""
import sys
import os
import logging
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QAbstractNativeEventFilter

from core import config
from core.hotkey import HotkeyManager
from gui.main_window import MainWindow
from gui.tray import TrayIcon
from version import VERSION


def show_version():
    """打印版本号与本次更新要点。"""
    print(f"Window Toggle v{VERSION}")
    print()
    print(f"v{VERSION} 主要更新：")
    print("  - 接入 corner-badge：绑定窗口右上角显示 pi 状态标签")
    print("    (未完成=绿 / 完成=红 / 等你确认=黄 / 未知=灰)")
    print("  - 配置目录改为 w-toggle-x，与旧版实例的 window-toggle-win 分开，")
    print("    两个版本可以同时运行")
    print("  - 版本号收敛到 version.py 单一来源")


def main():
    if '--version' in sys.argv:
        show_version()
        return 0

    # 设置日志 - 同时输出到文件和控制台
    log_file = config.LOG_FILE
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            file_handler,
            logging.StreamHandler()
        ]
    )

    # 创建应用
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # 设置应用信息
    app.setApplicationName("Window Toggle")
    app.setApplicationVersion(VERSION)

    # 创建热键管理器
    hotkey_manager = HotkeyManager()

    # 创建主窗口
    main_window = MainWindow(hotkey_manager)
    main_window.show()

    # 获取窗口句柄并设置热键
    hwnd = int(main_window.winId())
    hotkey_manager.set_hwnd(hwnd)

    # 加载并注册热键
    main_window.setup_hotkeys()

    # 安装原生事件过滤器处理 WM_HOTKEY
    class HotkeyFilter(QAbstractNativeEventFilter):
        def __init__(self, manager):
            super().__init__()
            self.manager = manager
            self.WM_HOTKEY = 0x0312

        def nativeEventFilter(self, eventType, message):
            if eventType == "windows_generic_MSG":
                msg = ctypes.wintypes.MSG.from_address(message.__int__())
                if msg.message == self.WM_HOTKEY:
                    shortcut_id = msg.wParam
                    self.manager.on_hotkey(shortcut_id)
                    return True, 0
            return False, 0

    filter = HotkeyFilter(hotkey_manager)
    app.installNativeEventFilter(filter)

    # 创建托盘图标
    tray = TrayIcon(main_window)
    tray.show()

    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
