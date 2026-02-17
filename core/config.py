"""
配置管理模块
负责配置文件的读取、保存、添加和删除快捷键
"""
import json
import os

# 配置文件路径
CONFIG_DIR = os.path.join(os.getenv('APPDATA'), 'window-toggle-win')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')


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

    return shortcut


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
