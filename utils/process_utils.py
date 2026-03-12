"""
进程工具函数
获取系统中运行的进程信息
"""
import psutil
import win32gui
import win32process


def get_windowed_processes() -> list[dict]:
    """
    获取所有带窗口的用户进程（过滤系统进程）

    Returns:
        List[dict]: 进程信息列表，每个元素包含 {pid, name, title}
                    title 为窗口标题，可能为空
    """
    # 系统进程黑名单
    SYSTEM_PROCESSES = {
        "system", "system idle process", "registry", "smss.exe",
        "csrss.exe", "wininit.exe", "winlogon.exe", "services.exe",
        "lsass.exe", "svchost.exe", "dwm.exe",
        "conhost.exe", "taskhost.exe", "audiodg.exe",
    }

    processes = []
    seen_pids = set()

    # 遍历所有窗口，获取它们的 PID
    def enum_callback(hwnd, _):
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid and pid not in seen_pids:
                seen_pids.add(pid)
                try:
                    process = psutil.Process(pid)
                    proc_name = process.name().lower()

                    # 过滤系统进程
                    if proc_name in SYSTEM_PROCESSES:
                        return True

                    # 获取窗口标题
                    window_text = win32gui.GetWindowText(hwnd)

                    processes.append({
                        "pid": pid,
                        "name": process.name(),
                        "title": window_text or "(无标题)"
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass
        return True

    win32gui.EnumWindows(enum_callback, None)

    # 按进程名排序并返回列表
    processes.sort(key=lambda x: x["name"].lower())
    return processes


def get_process_by_name(process_name: str) -> dict | None:
    """
    根据进程名获取进程信息

    Args:
        process_name: 进程名称（如 "GLEmulator.exe"）

    Returns:
        dict | None: 进程信息 {pid, name, title}，未找到返回 None
    """
    processes = get_windowed_processes()
    for proc in processes:
        if proc["name"].lower() == process_name.lower():
            return proc
    return None


def format_process_display(proc: dict) -> str:
    """
    格式化进程信息用于显示

    Args:
        proc: 进程信息字典

    Returns:
        str: 格式化后的显示文本
    """
    title = proc["title"]
    if len(title) > 30:
        title = title[:27] + "..."
    return f"{proc['name']} - {title}"
