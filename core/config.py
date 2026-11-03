"""
配置管理模块
负责配置文件的读取、保存、添加和删除快捷键
"""
import json
import os
import subprocess


def _config_base_dir():
    """配置根目录（跨平台）。"""
    if os.name == 'nt':
        return os.getenv('APPDATA') or os.path.expanduser('~')
    return os.getenv('XDG_CONFIG_HOME') or os.path.join(os.path.expanduser('~'), '.config')


# 配置文件路径
# 目录名用 w-toggle-x，与旧版 window-toggle-win 分开 —— 旧版实例还在跑，
# 共用配置会互相覆盖绑定。两版可以同时运行、各自独立。
CONFIG_DIR = os.path.join(_config_base_dir(), 'w-toggle-x')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
LOG_FILE = os.path.join(CONFIG_DIR, 'app.log')

# corner-badge 回调命令（不存在就静默跳过，它是可选的）
BADGE_CMD = 'wt-badge-cb'


def ensure_config_dir():
    """确保配置目录存在"""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)


def load():
    """
    加载配置文件
    Returns:
        dict: 配置数据，包含 shortcuts 列表
    """
    ensure_config_dir()
    if not os.path.exists(CONFIG_FILE):
        return {"shortcuts": []}

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save(data):
    """
    保存配置数据到文件
    Args:
        data: 配置字典
    """
    ensure_config_dir()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_shortcut(shortcut):
    """
    添加一个新的快捷键配置
    Args:
        shortcut: 快捷键字典，包含 key, modifiers, window_title, window_class, hwnd
    Returns:
        dict: 添加后的完整快捷键数据（包含 ID）
    """
    data = load()

    # 生成新 ID
    existing_ids = [s.get('id', 0) for s in data['shortcuts']]
    new_id = max(existing_ids) + 1 if existing_ids else 1

    shortcut['id'] = new_id
    data['shortcuts'].append(shortcut)
    save(data)

    # 通知 corner-badge：登记这个绑定，右上角就能显示它的状态标签
    notify_badge(shortcut)

    return shortcut


def _badge_cmd(args):
    """构造调用 corner-badge 回调的命令。

    Windows 的 CreateProcess 只会自动补 .exe 后缀，**找不到 .cmd**，
    所以 Windows 上统一走 cmd /c，并优先用绝对路径（不依赖 PATH）。
    """
    args = [str(a) for a in args]
    if os.name == 'nt':
        wrapper = os.path.join(os.path.expanduser('~'), 'corner-badge', 'wt-badge-cb.cmd')
        if os.path.exists(wrapper):
            return ['cmd', '/c', wrapper] + args
        return ['cmd', '/c', BADGE_CMD] + args
    return [BADGE_CMD] + args


def _run_badge(args):
    """后台调用 corner-badge 回调。

    失败一律静默：徽章工具是可选的，绝不能影响快捷键配置的正常流程。
    """
    try:
        kwargs = dict(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                      stdin=subprocess.DEVNULL)
        if os.name == 'nt':
            # CREATE_NO_WINDOW：不弹黑框，且不和 CREATE_NEW_PROCESS_GROUP 冲突
            # （两者同时用会让 CreateProcess 直接失败）
            kwargs['creationflags'] = 0x08000000
        else:
            kwargs['start_new_session'] = True
        subprocess.Popen(_badge_cmd(args), **kwargs)
        return True
    except Exception:
        return False


def notify_badge(shortcut):
    """把单个绑定登记给 corner-badge。"""
    if not isinstance(shortcut, dict):
        return False
    key = shortcut.get('key', '')
    hwnd = shortcut.get('hwnd')
    if not key or not hwnd:
        return False
    modifiers = shortcut.get('modifiers', '')
    shortcut_str = f"{modifiers}+{key}" if modifiers else key
    return _run_badge([shortcut_str, str(hwnd)])


def notify_badge_all():
    """把已有绑定全部登记给 corner-badge（启动时调用）。"""
    try:
        data = load()
    except Exception:
        return False
    if not data.get('shortcuts'):
        return False
    return _run_badge(['--all'])


def remove_shortcut(shortcut_id):
    """
    删除指定 ID 的快捷键配置
    Args:
        shortcut_id: 要删除的快捷键 ID
    Returns:
        bool: 是否删除成功
    """
    data = load()
    original_count = len(data['shortcuts'])
    data['shortcuts'] = [s for s in data['shortcuts'] if s.get('id') != shortcut_id]

    if len(data['shortcuts']) < original_count:
        save(data)
        return True
    return False


def get_shortcut_by_id(shortcut_id):
    """
    根据 ID 获取快捷键配置
    Args:
        shortcut_id: 快捷键 ID
    Returns:
        dict or None: 快捷键配置
    """
    data = load()
    for s in data['shortcuts']:
        if s.get('id') == shortcut_id:
            return s
    return None
