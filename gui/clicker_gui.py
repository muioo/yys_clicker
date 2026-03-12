"""
鼠标连点器 GUI 界面
使用 tkinter 实现
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
import keyboard
from src.common.clicker_controller import ClickerController
from gui.process_dialog import select_process


class ClickerGUI:
    """连点器 GUI 界面"""

    # 点击器类型配置
    CLICKER_TYPES = {
        "前台点击": "foreground",
        "后台点击": "background",
    }

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("鼠标连点器控制面板")
        self.root.resizable(False, False)

        # 控制器
        self.controller = ClickerController(log_callback=self._log)

        # 界面变量
        self.clicker_type_var = tk.StringVar(value="前台点击")
        self.duration_var = tk.StringVar(value="0")
        self.clicks_per_second_var = tk.StringVar(value="2")
        self.status_var = tk.StringVar(value="未启动")
        self.target_process_var = tk.StringVar(value="GLEmulator.exe")
        self.is_running = False

        # 快捷键 hook
        self.hotkey_f6 = None
        self.hotkey_esc = None

        # UI 引用
        self.target_process_frame = None

        self._setup_ui()
        self._register_hotkeys()
        self._update_target_process_visibility()

        # 绑定点击器类型变化事件
        self.clicker_type_var.trace("w", lambda *_: self._update_target_process_visibility())

        # 窗口关闭时清理
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_ui(self):
        """设置界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="鼠标连点器控制面板", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # 连点器类型选择
        ttk.Label(main_frame, text="连点器类型:").grid(row=1, column=0, sticky=tk.W, pady=5)
        type_combo = ttk.Combobox(
            main_frame,
            textvariable=self.clicker_type_var,
            values=list(self.CLICKER_TYPES.keys()),
            state="readonly",
            width=25
        )
        type_combo.grid(row=1, column=1, pady=5)

        # 目标应用选择（仅后台点击显示）
        self.target_process_frame = ttk.Frame(main_frame)
        self.target_process_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)

        ttk.Label(self.target_process_frame, text="目标应用:").pack(side=tk.LEFT)

        target_entry = ttk.Entry(self.target_process_frame, textvariable=self.target_process_var, width=20, state="readonly")
        target_entry.pack(side=tk.LEFT, padx=5)

        select_button = ttk.Button(self.target_process_frame, text="选择...", command=self._select_process, width=8)
        select_button.pack(side=tk.LEFT)

        # 运行时长设置
        ttk.Label(main_frame, text="运行时长(分钟):").grid(row=3, column=0, sticky=tk.W, pady=5)
        duration_entry = ttk.Entry(main_frame, textvariable=self.duration_var, width=27)
        duration_entry.grid(row=3, column=1, pady=5)
        ttk.Label(main_frame, text="(0 = 无限运行)", font=("Arial", 8)).grid(row=4, column=1, sticky=tk.W, padx=5)

        # 每秒点击次数设置
        ttk.Label(main_frame, text="每秒点击次数:").grid(row=5, column=0, sticky=tk.W, pady=5)
        cps_entry = ttk.Entry(main_frame, textvariable=self.clicks_per_second_var, width=27)
        cps_entry.grid(row=5, column=1, pady=5)

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=15)

        self.start_button = ttk.Button(button_frame, text="启动连点器", command=self._start_clicker, width=12)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="停止连点器", command=self._stop_clicker, state=tk.DISABLED, width=12)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # 状态显示
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        ttk.Label(status_frame, text="状态:").pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=5)

        # 快捷键提示
        hotkey_frame = ttk.Frame(main_frame)
        hotkey_frame.grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        ttk.Label(hotkey_frame, text="快捷键:", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        ttk.Label(hotkey_frame, text="[F6] 启动/停止", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        ttk.Label(hotkey_frame, text="[ESC] 停止连点器", font=("Arial", 9)).pack(side=tk.LEFT, padx=5)

        # 日志区域
        ttk.Label(main_frame, text="日志输出:").grid(row=9, column=0, sticky=tk.W, pady=(5, 5))

        log_text = scrolledtext.ScrolledText(
            main_frame,
            width=50,
            height=15,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        log_text.grid(row=10, column=0, columnspan=2, pady=5)

        # 配置日志文本标签颜色
        log_text.tag_config("INFO", foreground="black")
        log_text.tag_config("WARN", foreground="orange")
        log_text.tag_config("ERROR", foreground="red")

        self.log_text = log_text

        # 清空日志按钮
        clear_button = ttk.Button(main_frame, text="清空日志", command=self._clear_log, width=10)
        clear_button.grid(row=11, column=1, sticky=tk.E, pady=(5, 0))

    def _log(self, level: str, message: str):
        """日志回调函数"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"

        # 在主线程中更新 GUI
        self.root.after(0, self._append_log, level, log_line)

    def _append_log(self, level: str, log_line: str):
        """追加日志到文本框"""
        self.log_text.insert(tk.END, log_line, level)
        self.log_text.see(tk.END)

    def _clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)

    def _update_target_process_visibility(self, *_):
        """根据点击器类型更新目标应用选择区域显示"""
        clicker_type_name = self.clicker_type_var.get()
        clicker_type = self.CLICKER_TYPES.get(clicker_type_name)

        if clicker_type == "background":
            # 显示目标应用选择
            self.target_process_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        else:
            # 隐藏目标应用选择
            self.target_process_frame.grid_forget()

    def _select_process(self):
        """选择目标应用"""
        process_name = select_process(self.root)
        if process_name:
            self.target_process_var.set(process_name)
            self.controller.set_target_process(process_name)
            self._log("INFO", f"目标应用已设置为: {process_name}")

    def _validate_inputs(self) -> tuple[bool, str, float, float | None]:
        """验证输入参数"""
        # 获取点击器类型
        clicker_type_name = self.clicker_type_var.get()
        clicker_type = self.CLICKER_TYPES.get(clicker_type_name)

        if not clicker_type:
            return False, "", None, None

        # 获取每秒点击次数
        try:
            clicks_per_second = float(self.clicks_per_second_var.get())
            if clicks_per_second <= 0:
                self._log("ERROR", "每秒点击次数必须大于0")
                return False, "", None, None
        except ValueError:
            self._log("ERROR", "每秒点击次数必须是数字")
            return False, "", None, None

        # 获取运行时长
        try:
            duration_minutes = float(self.duration_var.get())
            if duration_minutes < 0:
                self._log("ERROR", "运行时长不能为负数")
                return False, "", None, None
            run_duration = duration_minutes * 60 if duration_minutes > 0 else None
        except ValueError:
            self._log("ERROR", "运行时长必须是数字")
            return False, "", None, None

        return True, clicker_type, clicks_per_second, run_duration

    def _start_clicker(self):
        """启动连点器"""
        valid, clicker_type, cps, duration = self._validate_inputs()
        if not valid:
            return

        # 如果是后台点击，设置目标进程
        if clicker_type == "background":
            target_process = self.target_process_var.get()
            self.controller.set_target_process(target_process)

        # 创建点击器
        self.controller.create_clicker(clicker_type, cps, duration)

        # 启动
        if self.controller.start_clicker():
            self.is_running = True
            self._update_ui_state(True)

    def _stop_clicker(self):
        """停止连点器"""
        if self.controller.stop_clicker():
            self.is_running = False
            self._update_ui_state(False)

    def _update_ui_state(self, running: bool):
        """更新 UI 状态"""
        if running:
            self.status_var.set("运行中")
            self.status_label.configure(foreground="green")
            self.start_button.configure(state=tk.DISABLED)
            self.stop_button.configure(state=tk.NORMAL)
        else:
            self.status_var.set("已停止")
            self.status_label.configure(foreground="blue")
            self.start_button.configure(state=tk.NORMAL)
            self.stop_button.configure(state=tk.DISABLED)

    def _register_hotkeys(self):
        """注册快捷键"""
        # F6: 切换启动/停止
        self.hotkey_f6 = keyboard.on_press_key("f6", lambda _: self._toggle_clicker())
        # ESC: 停止连点器
        self.hotkey_esc = keyboard.on_press_key("esc", lambda _: self._stop_clicker_hotkey())

    def _unregister_hotkeys(self):
        """取消快捷键注册"""
        try:
            if self.hotkey_f6:
                keyboard.unhook_all_hotkeys()
            if self.hotkey_esc:
                keyboard.unhook_all_hotkeys()
        except Exception:
            pass

    def _toggle_clicker(self):
        """切换点击器启动/停止状态（快捷键回调）"""
        # 在主线程中执行
        self.root.after(0, self._toggle_clicker_impl)

    def _toggle_clicker_impl(self):
        """切换点击器启动/停止状态实现"""
        if self.is_running:
            self._stop_clicker()
        else:
            self._start_clicker()

    def _stop_clicker_hotkey(self):
        """停止连点器（快捷键回调）"""
        # 在主线程中执行
        self.root.after(0, self._stop_clicker)

    def _on_closing(self):
        """窗口关闭事件"""
        # 停止点击器
        if self.is_running:
            self.controller.stop_clicker()

        # 取消快捷键
        self._unregister_hotkeys()

        # 关闭窗口
        self.root.destroy()

    def run(self):
        """运行 GUI"""
        self.root.mainloop()


def main_gui():
    """GUI 入口"""
    gui = ClickerGUI()
    gui.run()


if __name__ == '__main__':
    main_gui()
