"""
鼠标自动点击核心模块
"""
import time
import pyautogui
import threading


class MouseClicker:
    """鼠标自动点击器"""

    def __init__(self, clicks_per_second: int = 2, run_duration: float = None):
        """
        初始化点击器

        Args:
            clicks_per_second: 每秒点击次数，默认2次
            run_duration: 运行时长（秒），None表示无限运行
        """
        self.clicks_per_second = clicks_per_second
        self.run_duration = run_duration
        self.running = False
        self.thread = None
        self.start_time = None
        # 设置点击间隔（秒）
        self.interval = 1.0 / clicks_per_second

    def get_target_position(self, rows: int = 2, cols: int = 3,
                           target_row: int = 1, target_col: int = 2) -> tuple:
        """
        获取屏幕分区的目标位置坐标

        Args:
            rows: 行数，默认2
            cols: 列数，默认3
            target_row: 目标行（从0开始），默认1（第二行）
            target_col: 目标列（从0开始），默认2（第三列）

        Returns:
            目标区域的中心坐标 (x, y)
        """
        screen_width, screen_height = pyautogui.size()

        # 计算每个区域的宽高
        cell_width = screen_width / cols
        cell_height = screen_height / rows

        # 计算目标区域的中心坐标
        x = int((target_col + 0.5) * cell_width)
        y = int((target_row + 0.5) * cell_height)

        return x, y

    def _click_loop(self):
        """点击循环（在独立线程中运行）"""
        self.start_time = time.time()
        while self.running:
            # 检查运行时长
            if self.run_duration and (time.time() - self.start_time) >= self.run_duration:
                print(f"[时间到] 运行时长 {self.run_duration} 秒已到，自动停止")
                self.running = False
                break

            # 第二行第三列 (2行3列，索引从0开始)
            x, y = self.get_target_position(rows=2, cols=3, target_row=1, target_col=2)
            pyautogui.click(x, y)
            print(f"[点击] 第2行第3列: ({x}, {y}) - {time.strftime('%H:%M:%S')}")
            time.sleep(self.interval)

    def start(self):
        """启动自动点击"""
        if self.running:
            print("[警告] 点击器已在运行中")
            return

        self.running = True
        self.thread = threading.Thread(target=self._click_loop, daemon=True)
        self.thread.start()
        print(f"[启动] 自动点击器已启动 - 每秒 {self.clicks_per_second} 次")

    def stop(self):
        """停止自动点击"""
        if not self.running:
            print("[警告] 点击器未在运行")
            return

        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        print("[停止] 自动点击器已停止")

    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.running
