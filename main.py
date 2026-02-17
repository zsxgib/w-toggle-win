"""
Window Toggle 主程序
使用 PyQt6 + ctypes RegisterHotKey
"""
import sys
import logging
import ctypes
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QAbstractNativeEventFilter

from core.hotkey import HotkeyManager
from gui.main_window import MainWindow
from gui.tray import TrayIcon


def main():
    # 设置日志 - 同时输出到文件和控制台
    log_file = 'C:\\Users\\Administrator\\AppData\\Roaming\\window-toggle-win\\app.log'
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
    app.setApplicationVersion("1.0.0")

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
