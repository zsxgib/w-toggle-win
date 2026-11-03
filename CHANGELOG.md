# Changelog

本文件记录 wtx（Window Toggle）各平台的版本变化。
Windows 与 Linux 形态共用同一版本序列、同一份 changelog、同名 tag。

## v0.8 (2026-11-03)

### 变更

- **登记绑定时把窗口标题一起传给 corner-badge**（`core/config.py`）
  - corner-badge 用这个**冻结的标题**来定位终端，而不是读当前窗口标题
  - Windows Terminal 分屏 / 切 tab 时，当前标题只反映激活的那个 pane
    （甚至可能变成空字符串），用当前标题会让徽章串台或直接变灰

### 修复

- corner-badge 的解析原本跑在 wt 的主线程里（Windows 上是秒级的全进程扫描），
  会把快捷键响应和界面一起卡住 —— 已改为后台线程

## v0.7 (2026-11-03)

### 变更

- **corner-badge 改为同进程集成**（Windows）
  - 标签窗口就是本进程的一个 QWidget，共用同一个 QApplication：
    **启动 wt → 标签出现，关闭 wt → 标签自动消失**
  - 不再有「wt → wt-badge-cb → badge」三层进程，也不再有 pid 文件、
    PATH 查找、job object 连坐这三类问题
  - 绑定登记改为进程内调用 `corner_badge.cli.register()`，
    不可用时仍回退到子进程方式
- `window-toggle.spec`：显式列入 `PyQt6.*`（corner-badge 用 importlib 动态选
  Qt 绑定，静态分析看不到），并排除 `PySide6`（PyInstaller 不允许同时打包
  两种 Qt 绑定）
- `requirements.txt`：加 `corner-badge>=0.9.0`

### 修复

- corner-badge 的 pid 文件里的进程号会被系统复用，导致 cb 误判「badge 还活着」
  而永远不启动新进程 —— 同进程集成后该机制彻底消失

## v0.4 (2026-11-03)

### 新增

- **接入 corner-badge**：绑定窗口在屏幕右上角显示 pi 状态标签
  - 标签文字 = 快捷键（如 `F1`）
  - 颜色 = 该窗口内 pi 的状态：**未完成绿 / 完成红 / 等你确认黄 / 未知灰**
  - 一个窗口有多个 pi 时按聚合规则取色（任一完成即算完成；都还在跑才算未完成）
- `--version` 命令：输出版本号与本次更新要点
- 配置文件目录改为 `%APPDATA%\w-toggle-x\`，**与旧版 `window-toggle-win` 分开**——
  两个版本可以同时运行，互不覆盖绑定
- 版本号收敛到 `version.py` 单一来源，`main.py` 不再散落硬编码

### 变更

- 新增/删除快捷键后自动通知 corner-badge 登记绑定
- 程序启动时把已有绑定全部登记，标签直接显示

### 修复

- Windows 上 `CreateProcess` 找不到 `.cmd`：改用 `cmd /c` + 绝对路径调用回调
- Windows 上 `creationflags` 不能同时用 `CREATE_NEW_PROCESS_GROUP` 与
  `DETACHED_PROCESS`：改用 `CREATE_NO_WINDOW`
- Windows Terminal 多标签无法区分：改用「窗口标题末段 ↔ pi 的 cwd 目录名」匹配归属

## v0.6 (2026-11-03)

### 修复

- 调 corner-badge 回调改为直接执行 `wt-badge-cb`（pip 装的 console_script，
  Windows 上是 .exe），不再经 `cmd /c` 也不用绝对路径。
  `CreateProcess` 只会自动补 `.exe` 后缀，原来找不到 `.cmd`；
  `cmd /c` 退出还会连带终止回调。命令在 PATH 里查找，pip 装完即可用。


## v0.5 (2026-11-03)

### 修复

- 调 corner-badge 回调时使用 `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`，
  回调不再依附 wt 的控制台。原先用 `CREATE_NO_WINDOW` 只保证不弹黑框，
  wt 退出时回调会被连带终止，表现为绑定表写了一半（时间戳更新、内容没更新）。
