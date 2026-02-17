# 进程图标显示实现计划

## 目标

在添加热键选择窗口时，显示窗口所属进程的图标，提高可识别性。

---

## 核心思路

### 第一步：获取窗口对应的进程

1. 窗口句柄 (hwnd) → 进程 ID (PID)
   - 使用 `GetWindowThreadProcessId` API

2. 进程 ID → 可执行文件路径
   - 使用 psutil 库获取进程信息

### 第二步：获取进程图标

1. 可执行文件路径 → HICON (图标句柄)
   - 使用 Windows API `SHGetFileInfo`

### 第三步：HICON 转换为 QIcon

1. HICON → BITMAP (位图句柄)
   - 使用 `GetIconInfo` API

2. BITMAP → 像素数据
   - 使用 `GetDIBits` API

3. 像素数据 → PIL Image
   - 使用 Pillow 库进行格式转换

4. PIL Image → QPixmap → QIcon
   - 使用 PyQt6 进行转换

---

## 实现步骤

### 阶段一：安装依赖

安装 Pillow 库：
```bash
pip install Pillow
```

### 阶段二：实现图标转换

#### 2.1 获取进程信息

```
输入: hwnd (窗口句柄)
输出: exe_path (可执行文件路径)

1. 调用 GetWindowThreadProcessId(hwnd) 获取 PID
2. 使用 psutil.Process(pid).exe() 获取 exe 路径
```

#### 2.2 获取 HICON

```
输入: exe_path (可执行文件路径)
输出: HICON (图标句柄)

1. 定义 SHFILEINFO 结构体
2. 调用 SHGetFileInfoW(exe_path, flags=SHGFI_ICON)
3. 返回 hIcon
```

#### 2.3 HICON 转 QIcon

```
输入: HICON (图标句柄)
输出: QIcon

1. 调用 GetIconInfo(hIcon) 获取 ICONINFO 结构体
   - 包含 hbmColor (颜色位图) 和 hbmMask (掩码位图)

2. 创建兼容的设备上下文 (DC)
3. 创建兼容位图
4. 使用 BitBlt 或 DrawIconEx 绘制图标到位图

5. 调用 GetDIBits 获取像素数据
   - 需要定义 BITMAPINFOHEADER 结构体
   - 输出格式: BGRA (每像素 4 字节)

6. 使用 Pillow 转换:
   - 将 BGRA 数组转换为 PIL Image
   - 可能需要通道重排 (BGR → RGB)

7. 转换为 PyQt6:
   - PIL Image → QImage
   - QImage → QPixmap
   - QPixmap → QIcon

8. 清理 GDI 资源
```

### 阶段三：集成到界面

```
修改 add_dialog.py 的 _load_windows 方法:

1. 获取窗口列表
2. 对每个窗口:
   a. 获取进程信息 (PID, exe_path)
   b. 获取进程图标 (调用 get_process_icon)
   c. 创建 QListWidgetItem
   d. 设置图标 (item.setIcon)
   e. 设置高度 (适应图标大小)
```

### 阶段四：测试与优化

1. 测试不同类型窗口
2. 处理获取失败的情况
3. 添加图标缓存提高性能
4. 清理 GDI 资源防止泄漏

---

## 关键 API 参考

| API | 作用 |
|---|---|
| GetWindowThreadProcessId | hwnd → PID |
| SHGetFileInfoW | exe → HICON |
| GetIconInfo | HICON → ICONINFO |
| GetDIBits | 位图句柄 → 像素数据 |
| CreateCompatibleDC | 创建内存 DC |
| BitBlt / DrawIconEx | 绘制图标到位图 |

---

## 效果预览

```
[图标] Chrome - Google
       chrome.exe | PID: 12345

[图标] Notepad - untitled
       notepad.exe | PID: 67890

[图标] 文件资源管理器
       explorer.exe | PID: 11111
```

---

## 测试清单

- [ ] 测试 Chrome 窗口显示 Chrome 图标
- [ ] 测试 Notepad 显示记事本图标
- [ ] 测试文件资源管理器显示文件夹图标
- [ ] 测试 VS Code 显示 Code 图标
- [ ] 测试系统窗口处理 (无图标时)
- [ ] 性能测试 (大量窗口时)
- [ ] 内存测试 (GDI 资源释放)
