"""
点击器控制器 - 管理 GUI 和点击器之间的交互
"""
import time
from typing import Callable, Optional
from core.mouse_clicker import MouseClicker, BackgroundClicker


class ClickerController:
    """点击器控制器，统一管理前台/后台点击器"""

    def __init__(self, log_callback: Callable[[str, str], None]):
        """
        初始化控制器

        Args:
            log_callback: 日志回调函数，签名为 (level, message) -> None
        """
        self.log_callback = log_callback
        self.clicker: Optional[MouseClicker | BackgroundClicker] = None
        self.clicker_type = None
        self.target_process = "GLEmulator.exe"  # 默认目标进程

    def set_target_process(self, process_name: str):
        """
        设置后台点击的目标进程

        Args:
            process_name: 目标进程名称（如 "GLEmulator.exe"）
        """
        self.target_process = process_name

    def get_target_process(self) -> str:
        """获取当前目标进程名称"""
        return self.target_process

    def create_clicker(self, clicker_type: str, clicks_per_second: float, run_duration: Optional[float] = None):
        """
        创建点击器实例

        Args:
            clicker_type: 点击器类型 ("foreground" 或 "background")
            clicks_per_second: 每秒点击次数
            run_duration: 运行时长（秒），None 表示无限运行
        """
        # 如果已有点击器在运行，先停止
        if self.clicker and self.clicker.is_running():
            self.stop_clicker()

        self.clicker_type = clicker_type

        if clicker_type == "background":
            self.clicker = BackgroundClicker(
                target_process=self.target_process,
                clicks_per_second=clicks_per_second,
                run_duration=run_duration,
                log_callback=self.log_callback
            )
        else:  # foreground
            self.clicker = MouseClicker(
                clicks_per_second=clicks_per_second,
                run_duration=run_duration,
                log_callback=self.log_callback
            )

    def start_clicker(self) -> bool:
        """
        启动点击器

        Returns:
            bool: 是否成功启动
        """
        if not self.clicker:
            self.log_callback("ERROR", "请先创建点击器")
            return False

        if self.clicker.is_running():
            self.log_callback("WARN", "点击器已在运行中")
            return False

        try:
            self.clicker.start()
            return True
        except Exception as e:
            self.log_callback("ERROR", f"启动失败: {str(e)}")
            return False

    def stop_clicker(self) -> bool:
        """
        停止点击器

        Returns:
            bool: 是否成功停止
        """
        if not self.clicker:
            self.log_callback("WARN", "没有点击器在运行")
            return False

        try:
            self.clicker.stop()
            return True
        except Exception as e:
            self.log_callback("ERROR", f"停止失败: {str(e)}")
            return False

    def is_running(self) -> bool:
        """检查点击器是否正在运行"""
        return self.clicker is not None and self.clicker.is_running()

    def get_click_count(self) -> int:
        """获取当前点击次数"""
        if self.clicker:
            return self.clicker.get_click_count()
        return 0

    def get_clicker_type(self) -> str:
        """获取当前点击器类型"""
        return self.clicker_type or "未设置"
