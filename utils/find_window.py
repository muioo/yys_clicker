"""
窗口查找模块 - 查找目标进程的窗口
"""
import psutil
import win32gui
import win32con
# 新增：导入win32process模块（关键修复）
import win32process


def get_window_info(hwnd):
    """
    获取窗口详细信息

    Args:
        hwnd: 窗口句柄

    Returns:
        窗口信息字典
    """
    return {
        "hwnd": hwnd,
        "title": win32gui.GetWindowText(hwnd),
        "class_name": win32gui.GetClassName(hwnd),
        "rect": win32gui.GetWindowRect(hwnd),
        "visible": win32gui.IsWindowVisible(hwnd),
    }


def find_window(process_name="GLEmulator.exe"):
    """
    查找目标进程的主窗口（返回第一个匹配的窗口）

    Args:
        process_name: 目标进程名称

    Returns:
        窗口句柄，未找到返回 None
    """
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            # 修复：从win32process调用GetWindowThreadProcessId
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                if process.name() == process_name:
                    windows.append(hwnd)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return True

    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows[0] if windows else None


def get_all_windows(process_name="GLEmulator.exe"):
    """
    获取目标进程的所有窗口

    Args:
        process_name: 目标进程名称

    Returns:
        窗口信息列表
    """
    windows = []

    def callback(hwnd, result):
        if win32gui.IsWindowVisible(hwnd):
            # 修复：从win32process调用GetWindowThreadProcessId
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                if process.name() == process_name:
                    result.append(get_window_info(hwnd))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return True

    win32gui.EnumWindows(callback, windows)
    return windows


def print_window_info(info):
    """打印窗口信息"""
    print(f"  句柄: {info['hwnd']}")
    print(f"  标题: {info['title'] or '(无标题)'}")
    print(f"  类名: {info['class_name']}")
    left, top, right, bottom = info['rect']
    print(f"  位置: ({left}, {top}, {right}, {bottom}) - 大小: {right-left}x{bottom-top}")
    print()


def main():
    """主函数 - 查找并显示目标窗口信息"""
    print("=" * 50)
    print("       窗口查找工具")
    print("=" * 50)

    target = "GLEmulator.exe"
    print(f"正在查找目标窗口: {target}\n")

    # 查找第一个窗口
    hwnd = find_window(target)
    if hwnd:
        print(f"[找到] 目标窗口主窗口:")
        info = get_window_info(hwnd)
        print_window_info(info)
    else:
        print(f"[未找到] 未找到 {target} 的窗口\n")

    # 查找所有窗口
    all_windows = get_all_windows(target)
    if all_windows:
        print(f"[所有窗口] 共找到 {len(all_windows)} 个窗口:\n")
        for i, info in enumerate(all_windows, 1):
            print(f"--- 窗口 {i} ---")
            print_window_info(info)
    else:
        print(f"[未找到] 未找到 {target} 的任何窗口")

    print("=" * 50)


if __name__ == '__main__':
    main()