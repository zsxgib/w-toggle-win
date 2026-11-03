"""在 session 1 里验证：刷新解析 + 截图 + 徽章窗口。

由计划任务投递到 Console 会话执行（只有那里能访问桌面的窗口）。
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from corner_badge import badge, paths, resolver_backend as rb

BASE = r"C:\Users\Administrator\window-toggle-win\w-toggle-win-port"
L = []


def log(*a):
    s = " ".join(str(x) for x in a)
    L.append(s)
    print(s, flush=True)


app = QApplication(sys.argv)

log("=== 刷新解析（session 1）===")
b = json.load(open(paths.bindings_path(), encoding="utf-8"))
ctx = rb.build_context()
for k, e in sorted(b.items()):
    try:
        r = rb.resolve_for(e, ctx)
    except Exception as ex:
        log("  %-4s 异常 %r" % (k, ex))
        continue
    new = r.get("pi_pids") if r else None
    log("  %-4s match=%-6s 绑定表=%s  重新解析=%s  一致=%s"
        % (k, (r or {}).get("match"), e.get("pi_pids"), new, new == e.get("pi_pids")))

log("")
log("=== 徽章窗口 ===")
import psutil
import win32gui
import win32process

badge_pids = []
for p in psutil.process_iter(["pid", "cmdline"]):
    try:
        cl = " ".join(p.info.get("cmdline") or [])
    except Exception:
        continue
    if "corner_badge.badge" in cl:
        badge_pids.append(p.info["pid"])
log("  badge pids:", badge_pids)


def cb(hwnd, _):
    try:
        pid = win32process.GetWindowThreadProcessId(hwnd)[1]
    except Exception:
        return
    if pid in badge_pids:
        r = win32gui.GetWindowRect(hwnd)
        log("  hwnd=%s visible=%s rect=%s size=%dx%d"
            % (hwnd, bool(win32gui.IsWindowVisible(hwnd)), r, r[2] - r[0], r[3] - r[1]))


win32gui.EnumWindows(cb, None)

log("")
log("=== 截图 ===")
pix = QGuiApplication.primaryScreen().grabWindow(0)
pix.save(os.path.join(BASE, "verify.png"))
log("  saved", pix.width(), "x", pix.height())

with open(os.path.join(BASE, "verify_out.txt"), "w", encoding="utf-8", errors="replace") as f:
    f.write("\n".join(L))
