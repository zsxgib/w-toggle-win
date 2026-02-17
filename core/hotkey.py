"""
热键管理模块
使用 ctypes + Windows RegisterHotKey
"""
import logging
import ctypes
from ctypes import wintypes

logger = logging.getLogger(__name__)

# Windows API
user32 = ctypes.windll.user32

# 定义常量
MOD_CONTROL = 0x0002
MOD_ALT = 0x0001
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008

# 定义 RegisterHotKey 和 UnregisterHotKey 函数
RegisterHotKey = user32.RegisterHotKey
RegisterHotKey.argtypes = [wintypes.HWND, wintypes.INT, wintypes.UINT, wintypes.UINT]
RegisterHotKey.restype = wintypes.BOOL

UnregisterHotKey = user32.UnregisterHotKey
UnregisterHotKey.argtypes = [wintypes.HWND, wintypes.INT]
UnregisterHotKey.restype = wintypes.BOOL

# 修饰键映射
MODIFIER_MAP = {
    'Ctrl': MOD_CONTROL,
    'Alt': MOD_ALT,
    'Shift': MOD_SHIFT,
    'Win': MOD_WIN,
}


class HotkeyManager:
    """热键管理器"""

    def __init__(self):
        self._hwnd = None
        self._hotkeys = {}  # shortcut_id -> key_data
        self._callbacks = {}

    def set_hwnd(self, hwnd):
        """设置窗口句柄"""
        self._hwnd = hwnd

    def register(self, shortcut_id, modifiers_str, key_str):
        """
        注册全局热键
        """
        if not self._hwnd:
            logger.error("No hwnd set")
            return False

        try:
            # 计算修饰键标志
            mod_flags = 0
            if modifiers_str:
                for mod in modifiers_str.split('+'):
                    if mod in MODIFIER_MAP:
                        mod_flags |= MODIFIER_MAP[mod]

            # 转换键名
            key_code = self._get_virtual_key_code(key_str)
            if key_code is None:
                logger.error(f"Failed to get key code for: {key_str}")
                return False

            # 注册热键
            result = RegisterHotKey(self._hwnd, shortcut_id, mod_flags, key_code)

            if result:
                self._hotkeys[shortcut_id] = {
                    'modifiers': modifiers_str,
                    'key': key_str,
                    'mod_flags': mod_flags,
                    'key_code': key_code
                }
                logger.info(f"Registered: {modifiers_str}+{key_str}, id={shortcut_id}")
                return True
            else:
                logger.error(f"Failed to register: {modifiers_str}+{key_str} (in use?)")
                return False

        except Exception as e:
            logger.error(f"Register error: {e}")
            return False

    def _get_virtual_key_code(self, key_str):
        """将键名转换为虚拟键码"""
        # 功能键: VK_F1 = 0x70 = 112
        if key_str.lower().startswith('f') and key_str[1:].isdigit():
            return 0x70 + int(key_str[1:]) - 1

        # 数字和字母
        if len(key_str) == 1:
            if key_str.isdigit() or key_str.isalpha():
                return ord(key_str.upper())

        # 特殊键
        key_map = {
            'space': 0x20,
            'enter': 0x0D,
            'return': 0x0D,
            'tab': 0x09,
            'escape': 0x1B,
            'esc': 0x1B,
            'backspace': 0x08,
            'delete': 0x2E,
            'insert': 0x2D,
            'home': 0x24,
            'end': 0x23,
            'pageup': 0x21,
            'pagedown': 0x22,
            'up': 0x26,
            'down': 0x28,
            'left': 0x25,
            'right': 0x27,
        }

        return key_map.get(key_str.lower())

    def on_hotkey(self, shortcut_id):
        """热键触发"""
        logger.info(f">>> ====== Hotkey triggered: id={shortcut_id} ======")
        logger.info(f">>> All registered hotkeys: {list(self._hotkeys.keys())}")

        if shortcut_id in self._callbacks:
            self._callbacks[shortcut_id]()

    def set_callback(self, shortcut_id, callback):
        """设置回调"""
        self._callbacks[shortcut_id] = callback

    def unregister(self, shortcut_id):
        """注销热键"""
        if shortcut_id in self._hotkeys:
            try:
                UnregisterHotKey(self._hwnd, shortcut_id)
            except:
                pass
            del self._hotkeys[shortcut_id]

        if shortcut_id in self._callbacks:
            del self._callbacks[shortcut_id]

    def unregister_all(self):
        """注销所有热键"""
        for shortcut_id in list(self._hotkeys.keys()):
            try:
                UnregisterHotKey(self._hwnd, shortcut_id)
            except:
                pass

        self._hotkeys.clear()
        self._callbacks.clear()
