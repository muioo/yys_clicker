"""
后台鼠标点击模块 - 使用 pywin32
修复：
1. 变量作用域错误（target_row/target_col 未定义）
2. 模块导入顺序错误（win32api 提前导入）
3. 坐标计算逻辑优化（适配窗口客户区）
4. 打印日志变量引用错误
5. 补充异常捕获和参数校验
"""
import time
import threading
import psutil
import win32gui
import win32con
import win32process
import win32api  # 修复：提前导入，避免函数内引用报错

class BackgroundClicker:
    """后台鼠标点击器（适配网易GL模拟器）"""

    def __init__(self, target_process: str = "GLEmulator.exe", clicks_per_second: int = 2, run_duration: float = None, log_callback=None):
        """
        初始化后台点击器

        Args:
            target_process: 目标进程名称（如 GLEmulator.exe）
            clicks_per_second: 每秒点击次数（默认2次）
            run_duration: 运行时长（秒），None表示无限运行
            log_callback: 日志回调函数，签名为 (level, message) -> None
        """
        # 基础配置
        self.target_process = target_process
        self.clicks_per_second = max(0.5, clicks_per_second)  # 限制最小间隔，避免卡死
        self.run_duration = run_duration
        self.interval = 1.0 / self.clicks_per_second
        # 运行状态
        self.running = False
        self.thread = None
        self.target_hwnd = None  # 目标窗口句柄
        self.start_time = None
        self.log_callback = log_callback
        self.click_count = 0

    def _log(self, level: str, message: str):
        """记录日志"""
        if self.log_callback:
            self.log_callback(level, message)
        else:
            print(f"[{level}] {message}")

    def find_target_window(self):
        """查找目标进程的主窗口（返回第一个可见窗口）"""
        def enum_callback(hwnd, windows):
            # 仅处理可见窗口
            if not win32gui.IsWindowVisible(hwnd):
                return True
            # 获取窗口所属进程ID（修复：改用win32process模块）
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                # 匹配进程名称
                process = psutil.Process(pid)
                if process.name() == self.target_process:
                    windows.append(hwnd)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            return True

        windows = []
        win32gui.EnumWindows(enum_callback, windows)
        return windows[0] if windows else None

    def get_target_position(self, rows: int = 2, cols: int = 3,
                           target_row: int = 1, target_col: int = 2) -> tuple:
        """
        计算目标窗口客户区的相对坐标（网格划分）
        Args:
            rows/cols: 窗口划分的行列数
            target_row/target_col: 目标行列（从0开始计数）
        Returns:
            (x, y): 客户区相对坐标
        """
        if not self.target_hwnd:
            raise RuntimeError("目标窗口未找到，请先确认进程运行")

        # 获取窗口客户区（内部区域，不含标题栏，坐标从(0,0)开始）
        client_rect = win32gui.GetClientRect(self.target_hwnd)
        client_width = client_rect[2] - client_rect[0]
        client_height = client_rect[3] - client_rect[1]

        # 校验行列参数（避免除以0）
        if rows <= 0 or cols <= 0:
            raise ValueError("行列数必须大于0")
        if target_row >= rows or target_col >= cols:
            raise ValueError(f"目标行列超出范围（最大行：{rows-1}，最大列：{cols-1}）")

        # 计算目标网格中心坐标（修复：简化逻辑，避免冗余）
        cell_width = client_width / cols
        cell_height = client_height / rows
        x = int(target_col * cell_width + cell_width / 2)
        y = int(target_row * cell_height + cell_height / 2)

        return x, y

    def get_challenge_button_position(self) -> tuple:
        """
        获取"挑战"按钮的坐标（右下角圆形按钮）
        根据图片分析：位于屏幕右下角区域
        Returns:
            (x, y): 客户区相对坐标
        """
        if not self.target_hwnd:
            raise RuntimeError("目标窗口未找到，请先确认进程运行")

        # 获取窗口客户区
        client_rect = win32gui.GetClientRect(self.target_hwnd)
        client_width = client_rect[2] - client_rect[0]
        client_height = client_rect[3] - client_rect[1]

        # 找到按钮位置：右下角（约90%宽度、90%高度位置）
        # 圆形按钮中心稍微偏上，避免点击到边缘
        x_percent = 0.90  # 右侧 90%
        y_percent = 0.88  # 底部 88%（圆形按钮中心）

        x = int(client_width * x_percent)
        y = int(client_height * y_percent)

        return x, y

    def send_click(self, x: int, y: int):
        """
        发送后台点击消息（虚拟输入绕过系统）

        发送完整的鼠标事件序列，确保后台窗口也能接收
        """
        if not self.target_hwnd:
            raise RuntimeError("目标窗口未找到")

        # 构造 lParam 参数
        l_param = win32api.MAKELONG(x, y)

        # 发送完整的鼠标事件序列（模拟真实点击）
        # 1. 鼠标移动到目标位置
        win32gui.PostMessage(self.target_hwnd, win32con.WM_MOUSEMOVE, 0, l_param)
        time.sleep(0.005)

        # 2. 鼠标按下
        win32gui.PostMessage(self.target_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l_param)
        time.sleep(0.01)

        # 3. 鼠标抬起
        win32gui.PostMessage(self.target_hwnd, win32con.WM_LBUTTONUP, 0, l_param)
        time.sleep(0.005)

        # 4. 鼠标移出（可选，模拟真实行为）
        win32gui.PostMessage(self.target_hwnd, win32con.WM_MOUSEMOVE, 0, win32api.MAKELONG(0, 0))

    def _click_loop(self):
        """后台点击循环（守护线程运行）"""
        self.start_time = time.time()
        self.click_count = 0
        while self.running:
            try:
                # 检查运行时长
                if self.run_duration and (time.time() - self.start_time) >= self.run_duration:
                    self._log("INFO", f"运行时长 {self.run_duration} 秒已到，自动停止")
                    self.running = False
                    break

                # 1. 查找目标窗口（每次循环检查，适配窗口重启）
                self.target_hwnd = self.find_target_window()
                if not self.target_hwnd:
                    self._log("WARN", f"未找到进程 {self.target_process}，1秒后重试...")
                    time.sleep(1)
                    continue

                # 2. 获取"挑战"按钮坐标（右下角圆形按钮）
                x, y = self.get_challenge_button_position()

                # 3. 发送点击
                self.send_click(x, y)
                self.click_count += 1

                # 4. 打印日志
                self._log("INFO", f"点击按钮: ({x}, {y}) - 总次数: {self.click_count}")

                # 5. 间隔等待
                time.sleep(self.interval)

            except Exception as e:
                self._log("ERROR", f"点击失败: {str(e)}，1秒后重试...")
                time.sleep(1)

    def start(self):
        """启动后台点击器"""
        if self.running:
            self._log("WARN", "点击器已在运行中，无需重复启动")
            return

        self.running = True
        # 启动守护线程（主进程退出时自动结束）
        self.thread = threading.Thread(target=self._click_loop, daemon=True)
        self.thread.start()
        self._log("INFO", f"后台点击器已启动 - 目标进程: {self.target_process} | 点击频率: {self.clicks_per_second}次/秒")

    def stop(self):
        """停止后台点击器"""
        if not self.running:
            self._log("WARN", "点击器未运行，无需停止")
            return

        self.running = False
        # 等待线程退出（超时1秒）
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        self._log("INFO", f"后台点击器已停止 - 总点击次数: {self.click_count}")

    def get_click_count(self) -> int:
        """获取点击次数"""
        return self.click_count

    def is_running(self) -> bool:
        """检查点击器是否运行"""
        return self.running

# ================ 测试示例 ================
if __name__ == "__main__":
    # 初始化点击器（替换为你的模拟器进程名）
    clicker = BackgroundClicker(
        target_process="GLEmulator.exe",
        clicks_per_second=1  # 降低频率，便于测试
    )

    try:
        # 启动点击器
        clicker.start()
        # 运行10秒后自动停止
        time.sleep(10)
        # 停止点击器
        clicker.stop()
    except KeyboardInterrupt:
        # 捕获Ctrl+C，手动停止
        clicker.stop()
        print("\n[手动停止] 点击器已退出")
    except Exception as e:
        clicker.stop()
        print(f"[异常退出] 原因：{str(e)}")