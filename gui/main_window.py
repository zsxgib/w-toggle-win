"""
主窗口模块
显示快捷键列表，提供添加/删除功能
"""
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt

from core import config, window as window_mgr

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, hotkey_manager):
        super().__init__()
        self.hotkey_manager = hotkey_manager
        self.registered_hotkeys = {}

        self.setWindowTitle("Window Toggle")
        self.setGeometry(100, 100, 500, 400)

        self._setup_ui()

    def closeEvent(self, event):
        """关闭窗口时隐藏到托盘，而不是退出程序"""
        event.ignore()
        self.hide()

    def setup_hotkeys(self):
        """设置热键"""
        self._load_shortcuts()

    def _setup_ui(self):
        """设置 UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 标题
        title = QLabel("Window Toggle")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 说明
        info = QLabel("按下配置的快捷键可切换窗口显示/隐藏")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        # 列表框
        self.listbox = QListWidget()
        layout.addWidget(self.listbox)

        # 按钮
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("+ 添加")
        self.add_button.clicked.connect(self._on_add_clicked)
        button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("- 删除")
        self.delete_button.clicked.connect(self._on_delete_clicked)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

    def _load_shortcuts(self):
        """加载快捷键列表"""
        # 先注销所有热键
        self.hotkey_manager.unregister_all()
        self.registered_hotkeys.clear()

        data = config.load()
        shortcuts = data.get('shortcuts', [])

        self.listbox.clear()

        if not shortcuts:
            self.listbox.addItem("暂无配置的快捷键")
            self.listbox.addItem("点击「添加」配置新快捷键")
        else:
            for s in shortcuts:
                mod = s.get('modifiers', '')
                key = s.get('key', '')
                title = s.get('window_title', '')

                if mod:
                    hotkey_str = f"{mod}+{key}"
                else:
                    hotkey_str = key

                self.listbox.addItem(f"{hotkey_str} → {title}")

            # 注册热键
            self._register_all_hotkeys()

    def _register_all_hotkeys(self):
        """注册所有热键"""
        data = config.load()
        shortcuts = data.get('shortcuts', [])

        for s in shortcuts:
            shortcut_id = s.get('id')
            modifiers = s.get('modifiers', '')
            key = s.get('key', '')
            window_title = s.get('window_title', '')
            window_class = s.get('window_class', '')
            hwnd = s.get('hwnd')

            if shortcut_id and key:
                self.registered_hotkeys[shortcut_id] = {
                    'modifiers': modifiers,
                    'key': key,
                    'window_title': window_title,
                    'window_class': window_class,
                    'hwnd': hwnd
                }

                if self.hotkey_manager.register(shortcut_id, modifiers, key):
                    self.hotkey_manager.set_callback(
                        shortcut_id,
                        lambda sid=shortcut_id: self._on_hotkey_triggered(sid)
                    )
                    print(f"[register] Registered {modifiers}+{key} as id={shortcut_id}")
                else:
                    print(f"[register] Failed to register {modifiers}+{key}, id={shortcut_id}")

    def _on_add_clicked(self):
        """添加按钮点击"""
        from gui.add_dialog import AddDialog

        dialog = AddDialog(self, self.hotkey_manager)
        dialog.accepted.connect(self.setup_hotkeys)
        dialog.exec()

    def _on_delete_clicked(self):
        """删除按钮点击"""
        row = self.listbox.currentRow()
        if row < 0:
            return

        data = config.load()
        shortcuts = data.get('shortcuts', [])

        if not shortcuts or row >= len(shortcuts):
            return

        # 使用 config 中实际的 ID
        shortcut = shortcuts[row]
        shortcut_id = shortcut.get('id')

        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这个快捷键吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.hotkey_manager.unregister(shortcut_id)
            if shortcut_id in self.registered_hotkeys:
                del self.registered_hotkeys[shortcut_id]

            config.remove_shortcut(shortcut_id)
            self.setup_hotkeys()

    def _on_hotkey_triggered(self, shortcut_id):
        """热键触发"""
        logger.info(f">>> ===== _on_hotkey_triggered called: id={shortcut_id} =====")
        logger.info(f">>> registered_hotkeys keys: {list(self.registered_hotkeys.keys())}")

        if shortcut_id not in self.registered_hotkeys:
            logger.warning(f">>> shortcut_id {shortcut_id} NOT FOUND in registered_hotkeys!")
            return

        shortcut_info = self.registered_hotkeys[shortcut_id]
        logger.info(f">>> shortcut_info: {shortcut_info}")

        # 优先使用保存的 hwnd
        hwnd = shortcut_info.get('hwnd')
        logger.info(f">>> Original hwnd: {hwnd}")

        # 如果 hwnd 无效，尝试用 window_class 查找
        if not hwnd or not window_mgr.is_valid_window(hwnd):
            logger.info(f">>> hwnd invalid, trying window_class...")
            window_class = shortcut_info.get('window_class', '')
            if window_class:
                hwnd = window_mgr.find_window_by_class(window_class)
                logger.info(f">>> Found hwnd by class: {hwnd}")

        if hwnd:
            logger.info(f">>> Calling toggle_window({hwnd})")
            window_mgr.toggle_window(hwnd)
        else:
            logger.warning("未找到窗口，可能需要重新配置")
