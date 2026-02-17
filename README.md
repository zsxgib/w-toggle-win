# Window Toggle

[English](#english) | [中文](#中文)

---

## English

A Windows utility to toggle window visibility with global hotkeys.

### Features

- Toggle window visibility using global hotkeys
- Support for F1-F12 and modifier keys (Ctrl, Alt, Shift, Win)
- System tray running, no taskbar占用
- Right-click tray icon menu: Show Window / Quit
- Close window to hide to tray

### Requirements

- Windows 10/11
- Python 3.8+

### Installation

```bash
# Clone the repository
git clone https://github.com/zsxgib/w-toggle-win.git
cd w-toggle-win

# Install dependencies
pip install -r requirements.txt
```

### Build Executable

```bash
pyinstaller --onefile --name window-toggle main.py
```

The executable will be in `dist/window-toggle.exe`

### Usage

1. Run `window-toggle.exe`
2. Click "+ Add" to add a new hotkey
3. Press the key combination you want to use
4. Select the target window from the list
5. Press the configured hotkey to toggle that window's visibility

### Configuration

Configuration is saved in: `%APPDATA%\window-toggle-win\config.json`

---

## 中文

使用全局热键切换窗口显示/隐藏的 Windows 工具。

### 功能

- 使用全局热键切换窗口显示/隐藏
- 支持 F1-F12 及修饰键 (Ctrl, Alt, Shift, Win)
- 系统托盘运行，不占用任务栏
- 右键托盘菜单：显示窗口 / 退出
- 关闭窗口自动隐藏到托盘

### 环境要求

- Windows 10/11
- Python 3.8+

### 安装

```bash
# 克隆仓库
git clone https://github.com/zsxgib/w-toggle-win.git
cd w-toggle-win

# 安装依赖
pip install -r requirements.txt
```

### 构建可执行文件

```bash
pyinstaller --onefile --name window-toggle main.py
```

可执行文件位于 `dist/window-toggle.exe`

### 使用方法

1. 运行 `window-toggle.exe`
2. 点击 "+ 添加" 添加新热键
3. 按下你想使用的按键组合
4. 从列表中选择目标窗口
5. 按下配置的热键即可切换该窗口的显示/隐藏

### 配置

配置文件保存在: `%APPDATA%\window-toggle-win\config.json`
