# Changelog

本文件记录 wtx（Window Toggle）各平台的版本变化。
Windows 与 Linux 形态共用同一版本序列、同一份 changelog、同名 tag。

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

## v0.5 (2026-11-03)

### 修复

- 调 corner-badge 回调时使用 `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`，
  回调不再依附 wt 的控制台。原先用 `CREATE_NO_WINDOW` 只保证不弹黑框，
  wt 退出时回调会被连带终止，表现为绑定表写了一半（时间戳更新、内容没更新）。
