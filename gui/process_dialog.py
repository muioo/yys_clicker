"""
进程选择对话框
用于选择目标应用进行后台点击
"""
import tkinter as tk
from tkinter import ttk, simpledialog
from utils.process_utils import get_windowed_processes, format_process_display


class ProcessDialog(simpledialog.Dialog):
    """进程选择对话框"""

    def __init__(self, parent, title="选择目标应用"):
        self.selected_process = None
        self.process_list = []
        self.filter_var = None
        self.tree = None
        super().__init__(parent, title=title)

    def body(self, master):
        """对话框主体"""
        # 过滤框
        filter_frame = ttk.Frame(master)
        filter_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        ttk.Label(filter_frame, text="搜索:").pack(side=tk.LEFT)
        self.filter_var = tk.StringVar()
        self.filter_var.trace("w", self._on_filter_change)
        filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var, width=30)
        filter_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 进程列表
        list_frame = ttk.Frame(master)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 树形列表
        columns = ("name", "title")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=12
        )
        self.tree.heading("name", text="进程名称")
        self.tree.heading("title", text="窗口标题")
        self.tree.column("name", width=150)
        self.tree.column("title", width=300)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        # 双击选择
        self.tree.bind("<Double-1>", lambda _: self.ok())

        # 加载进程列表
        self._load_processes()

        # 设置焦点
        self.filter_entry = filter_entry
        return filter_entry

    def _load_processes(self, filter_text: str = ""):
        """加载进程列表"""
        # 清空列表
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 获取进程列表
        self.process_list = get_windowed_processes()

        # 过滤
        filter_lower = filter_text.lower()
        for proc in self.process_list:
            display_text = format_process_display(proc).lower()
            if filter_lower in display_text:
                self.tree.insert("", tk.END, values=(proc["name"], proc["title"]))

    def _on_filter_change(self, *args):
        """过滤框变化事件"""
        self._load_processes(self.filter_var.get())

    def validate(self):
        """验证选择"""
        selection = self.tree.selection()
        if not selection:
            return False

        item = self.tree.item(selection[0])
        name = item["values"][0]

        # 查找对应的进程
        for proc in self.process_list:
            if proc["name"] == name:
                self.selected_process = proc
                return True

        return False

    def apply(self):
        """应用选择"""
        if self.selected_process:
            self.result = self.selected_process["name"]


def select_process(parent) -> str | None:
    """
    打开进程选择对话框

    Args:
        parent: 父窗口

    Returns:
        str | None: 选中的进程名称，取消返回 None
    """
    dialog = ProcessDialog(parent)
    return dialog.result
