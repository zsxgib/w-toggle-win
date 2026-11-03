# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        # corner-badge 用 importlib 动态选 Qt 绑定，静态分析看不到，
        # 这里显式列出（Windows 上装的是 PyQt6）。
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # PyInstaller 不允许同时打包两种 Qt 绑定，corner-badge 在 Windows 上
        # 用 PyQt6，把 PySide6 排除掉。
        'PySide6',
        # corner-badge 不打进 exe：它自己就是 pip 包，运行时从用户
        # site-packages 导入（见 main.py 的 _add_pip_site_packages）。
        # 这样升级 corner-badge 只需要 pip install -U，不用重新打包。
        'corner_badge',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='window-toggle',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
