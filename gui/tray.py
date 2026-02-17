"""
系统托盘模块
使用 PyQt6 QSystemTrayIcon
"""
import logging
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)


class TrayIcon(QSystemTrayIcon):
    def __init__(self, main_window):
        self.main_window = main_window

        # 创建图标
        icon = self._create_icon()
        super().__init__(icon)

        self.setToolTip("Window Toggle")
        self._create_menu()

        # 连接信号
        self.activated.connect(self._on_activated)

    def _create_icon(self):
        """创建托盘图标"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setBrush(QColor(59, 142, 208))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(2, 2, 12, 12)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRect(4, 4, 3, 3)
        painter.drawRect(9, 4, 3, 3)
        painter.drawRect(4, 9, 3, 3)
        painter.drawRect(9, 9, 3, 3)
        painter.end()

        return QIcon(pixmap)

    def _create_menu(self):
        """创建右键菜单"""
        # 不设置父窗口，避免窗口隐藏后菜单出问题
        menu = QMenu()

        show_action = menu.addAction("显示")
        show_action.triggered.connect(self._show_window)

        quit_action = menu.addAction("退出")
        quit_action.triggered.connect(self._quit)

        self.setContextMenu(menu)

    def _on_activated(self, reason):
        """托盘图标被点击"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # 单击 - 切换窗口显示
            if self.main_window.isVisible():
                self.main_window.hide()
            else:
                self._show_window()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # 双击 - 显示窗口
            self._show_window()

    def _show_window(self):
        """显示主窗口"""
        try:
            self.main_window.show()
            self.main_window.activateWindow()
            self.main_window.raise_()
        except Exception as e:
            logger.error(f"Failed to show window: {e}")

    def _quit(self):
        """退出程序"""
        try:
            # 注销所有热键
            self.main_window.hotkey_manager.unregister_all()
        except Exception as e:
            logger.error(f"Failed to unregister hotkeys: {e}")
        # 退出程序
        QApplication.exit(0)
