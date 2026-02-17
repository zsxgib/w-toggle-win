"""
添加快捷键对话框
两步流程：
1. 捕获按键
2. 选择窗口
"""
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QKeyEvent, QFont, QIcon
from PyQt6.QtWidgets import QListWidgetItem

from core import config, window as window_mgr

logger = logging.getLogger(__name__)


class AddDialog(QDialog):
    def __init__(self, parent, hotkey_manager):
        super().__init__(parent)
        self.hotkey_manager = hotkey_manager
        self.selected_window = None
        self.selected_hotkey = None
        self.pressed_modifiers = set()
        self.capture_mode = True

        self.setWindowTitle("添加快捷键")
        self.setGeometry(200, 200, 500, 450)

        self._setup_ui()

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)

        # 步骤说明
        self.step_label = QLabel("步骤 1: 请按下要使用的快捷键")
        self.step_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.step_label)

        # 快捷键显示
        self.hotkey_label = QLabel("等待按键...（按 ESC 取消）")
        self.hotkey_label.setStyleSheet("""
            QLabel {
                border: 2px solid #3b8ed0;
                border-radius: 5px;
                padding: 15px;
                font-size: 24px;
                font-weight: bold;
                background-color: #2b2b2b;
                color: gray;
                min-height: 50px;
            }
        """)
        self.hotkey_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.hotkey_label)

        # 说明
        info = QLabel("例如: F1, Ctrl+F1, Alt+F2, Ctrl+Shift+F3")
        info.setStyleSheet("color: #888;")
        layout.addWidget(info)

        # 窗口列表（初始隐藏）
        self.window_group = QGroupBox("步骤 2: 选择目标窗口")
        window_layout = QVBoxLayout()

        self.window_list = QListWidget()
        window_layout.addWidget(self.window_list)

        # 刷新按钮
        refresh_btn = QPushButton("刷新窗口列表")
        refresh_btn.clicked.connect(self._load_windows)
        window_layout.addWidget(refresh_btn)

        self.window_group.setLayout(window_layout)
        self.window_group.hide()
        layout.addWidget(self.window_group)

        # 按钮
        button_layout = QHBoxLayout()

        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self._on_ok)
        self.ok_button.setEnabled(False)

        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # 设置定时器让对话框获取焦点
        QTimer.singleShot(100, self.setFocus)

    def keyPressEvent(self, event):
        """捕获按键事件"""
        if not self.capture_mode:
            super().keyPressEvent(event)
            return

        key = event.key()

        # ESC 取消
        if key == Qt.Key.Key_Escape:
            self.reject()
            return

        # 修饰键 (PyQt6 只有 Key_Control, Key_Alt, Key_Shift)
        if key == Qt.Key.Key_Control:
            self.pressed_modifiers.add('Ctrl')
        elif key == Qt.Key.Key_Alt:
            self.pressed_modifiers.add('Alt')
        elif key == Qt.Key.Key_Shift:
            self.pressed_modifiers.add('Shift')
        elif key == Qt.Key.Key_Meta:  # Win key
            self.pressed_modifiers.add('Win')
        else:
            # 普通键
            key_name = self._get_key_name(key)
            if key_name:
                self._capture_hotkey(key_name)

        event.accept()

    def keyReleaseEvent(self, event):
        """按键释放事件"""
        if not self.capture_mode:
            super().keyReleaseEvent(event)
            return

        key = event.key()

        # 清除修饰键
        if key == Qt.Key.Key_Control:
            self.pressed_modifiers.discard('Ctrl')
        elif key == Qt.Key.Key_Alt:
            self.pressed_modifiers.discard('Alt')
        elif key == Qt.Key.Key_Shift:
            self.pressed_modifiers.discard('Shift')
        elif key == Qt.Key.Key_Meta:
            self.pressed_modifiers.discard('Win')

        event.accept()

    def _get_key_name(self, qt_key):
        """将 Qt 按键转换为字符串"""
        # 功能键
        if Qt.Key.Key_F1 <= qt_key <= Qt.Key.Key_F12:
            return f"f{qt_key - Qt.Key.Key_F1 + 1}"

        # 字母
        if Qt.Key.Key_A <= qt_key <= Qt.Key.Key_Z:
            return chr(qt_key - Qt.Key.Key_A + ord('a'))

        # 数字
        if Qt.Key.Key_0 <= qt_key <= Qt.Key.Key_9:
            return chr(qt_key - Qt.Key.Key_0 + ord('0'))

        # 特殊键
        key_map = {
            Qt.Key.Key_Space: "space",
            Qt.Key.Key_Return: "enter",
            Qt.Key.Key_Enter: "enter",
            Qt.Key.Key_Tab: "tab",
            Qt.Key.Key_Escape: "escape",
            Qt.Key.Key_Backspace: "backspace",
            Qt.Key.Key_Delete: "delete",
        }

        return key_map.get(qt_key)

    def _capture_hotkey(self, key_name):
        """捕获到快捷键"""
        # 排序修饰键
        mod_str = '+'.join(sorted(self.pressed_modifiers))

        if mod_str:
            hotkey_str = f"{mod_str}+{key_name}"
        else:
            hotkey_str = key_name

        self.selected_hotkey = {
            'modifiers': mod_str,
            'key': key_name
        }

        # 显示捕获的快捷键
        self.hotkey_label.setText(hotkey_str)
        self.hotkey_label.setStyleSheet("""
            QLabel {
                border: 2px solid #27ae60;
                border-radius: 5px;
                padding: 15px;
                font-size: 24px;
                font-weight: bold;
                background-color: #2b2b2b;
                color: #27ae60;
                min-height: 50px;
            }
        """)

        # 切换到窗口选择模式
        self.capture_mode = False
        self.step_label.setText("步骤 2: 选择目标窗口")
        self.window_group.show()
        self._load_windows()

    def _load_windows(self):
        """加载窗口列表"""
        import logging
        logger = logging.getLogger(__name__)

        logger.info("[add_dialog] === Step 1: Starting to load windows ===")
        try:
            self.window_list.clear()
            logger.info("[add_dialog] === Step 1.1: clear done ===")
            self.window_options = []
            logger.info("[add_dialog] === Step 1.2: options cleared ===")

            # 设置列表项高度
            self.window_list.setIconSize(QSize(24, 24))
            logger.info("[add_dialog] === Step 1.3: setIconSize done ===")
            self.window_list.setMinimumHeight(400)
            logger.info("[add_dialog] === Step 1.4: setMinimumHeight done ===")
        except Exception as e:
            logger.error(f"[add_dialog] ERROR in setup: {e}", exc_info=True)

        logger.info("[add_dialog] === Step 2: Before get_all_windows ===")
        try:
            windows = window_mgr.get_all_windows()
            logger.info(f"[add_dialog] === Step 3: Got {len(windows)} windows ===")
        except Exception as e:
            logger.error(f"[add_dialog] ERROR in get_all_windows: {e}", exc_info=True)
            windows = []

        # 过滤系统窗口并获取进程信息
        system_classes = {'Progman', 'Shell_TrayWnd', 'Windows.UI.Core.CoreWindow',
                         'WinUIDesktopWin32WindowClass', 'DV2ControlHost',
                         'Microsoft.CmdPal.UI.exe', 'TextInputHost.exe'}

        window_data = []
        for w in windows:
            if not w.get('title'):
                continue

            # 过滤系统窗口
            if w.get('class_name') in system_classes:
                logger.info(f"[add_dialog] Skipping system window: {w['title']} ({w.get('class_name')})")
                continue

            # 获取进程信息
            try:
                proc_info = window_mgr.get_window_process_info(w['hwnd'])
            except Exception as e:
                proc_info = None

            if proc_info:
                process_name = proc_info.get('process_name', 'Unknown')
            else:
                process_name = 'Unknown'

            window_data.append({
                'window': w,
                'proc_info': proc_info,
                'process_name': process_name
            })

        # 按进程名分组
        from collections import defaultdict
        groups = defaultdict(list)
        for data in window_data:
            groups[data['process_name']].append(data)

        logger.info(f"[add_dialog] Showing {len(groups)} groups")

        # 按进程名排序显示
        for process_name in sorted(groups.keys()):
            items = groups[process_name]

            # 添加分组标题
            group_item = QListWidgetItem(f"--- {process_name} ---")
            group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.window_list.addItem(group_item)

            for data in items:
                w = data['window']
                proc_info = data['proc_info']

                # 构建显示文本
                display_text = w['title']

                self.window_options.append(w)

                # 创建列表项
                item = QListWidgetItem(f"  {display_text}")

                # 加载图标
                try:
                    if proc_info and proc_info.get('exe_path'):
                        icon = window_mgr.get_process_icon(proc_info['exe_path'], 24)
                        if icon:
                            item.setIcon(icon)
                except Exception as e:
                    logger.warning(f"[add_dialog] Failed to get icon: {e}")

                self.window_list.addItem(item)

        logger.info("[add_dialog] Finished loading windows")
        # 绑定选择事件
        self.window_list.itemClicked.connect(self._on_window_selected)

    def _on_window_selected(self, item):
        """窗口被选中"""
        text = item.text()

        # 检查是否选中分组标题
        if text.startswith("---"):
            return

        # 计算实际窗口索引
        idx = self.window_list.row(item)
        window_idx = idx
        for i in range(idx):
            if self.window_list.item(i).text().startswith("---"):
                window_idx -= 1

        if 0 <= window_idx < len(self.window_options):
            self.selected_window = self.window_options[window_idx]
            self.ok_button.setEnabled(True)

    def _on_ok(self):
        """确定按钮点击"""
        if not self.selected_hotkey or not self.selected_window:
            return

        # 保存配置
        shortcut = {
            'modifiers': self.selected_hotkey['modifiers'],
            'key': self.selected_hotkey['key'],
            'window_title': self.selected_window['title'],
            'window_class': self.selected_window['class_name'],
            'hwnd': self.selected_window['hwnd']
        }

        saved = config.add_shortcut(shortcut)
        logger.info(f"Added: {self.selected_hotkey['modifiers']}+{self.selected_hotkey['key']} -> {self.selected_window['title']}")

        self.accept()
