# 鼠标连点器

基于 Python 的鼠标自动点击工具，支持前台点击和后台点击两种模式。

## 功能特性

- **GUI 图形界面** - 友好的可视化操作面板
- **前台点击模式** - 直接点击屏幕指定位置
- **后台点击模式** - 点击指定应用窗口（不影响其他操作）
- **目标应用选择** - 支持从系统进程中选择目标应用
- **可配置参数**
  - 运行时长设置（支持无限运行）
  - 每秒点击次数自定义
- **快捷键支持**
  - `F6` - 启动/停止连点器
  - `ESC` - 停止连点器
- **详细日志** - 实时显示点击状态、次数和错误信息

## 环境要求

- Python 3.8+
- Windows 操作系统
- conda 虚拟环境 `yysscript`

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/muioo/yys_clicker.git
cd yys_clicker
```

### 2. 创建并激活虚拟环境

```bash
conda create -n yysscript python=3.12
conda activate yysscript
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 启动程序

```bash
python main.py
```

### GUI 操作说明

1. **选择连点器类型**
   - 前台点击：直接点击屏幕
   - 后台点击：点击指定应用窗口

2. **后台点击模式** - 点击"选择..."按钮选择目标应用

3. **设置参数**
   - 运行时长：单位为分钟，0 表示无限运行
   - 每秒点击次数：建议 1-5 次

4. **启动/停止**
   - 点击"启动连点器"按钮
   - 或使用快捷键 `F6`

5. **查看日志**
   - 日志区域实时显示点击信息
   - 点击"清空日志"可清除日志内容

### 快捷键

| 按键 | 功能 |
|------|------|
| F6   | 启动/停止连点器 |
| ESC  | 停止连点器 |

## 项目结构

```
yysScript/
├── main.py                      # 程序入口
├── gui/                         # GUI 界面
│   ├── clicker_gui.py          # 主界面
│   └── process_dialog.py       # 进程选择对话框
├── src/                         # 源代码
│   └── common/
│       ├── usual_clicker.py    # CLI 模式
│       └── clicker_controller.py # 控制器
├── core/                        # 核心模块
│   └── mouse_clicker/
│       ├── clicker.py          # 前台点击器
│       └── background_clicker.py # 后台点击器
└── utils/                       # 工具函数
    └── process_utils.py        # 进程工具
```

## 常见问题

### Q: 后台点击找不到目标进程？
A: 确保目标应用正在运行且具有可见窗口，然后点击"选择..."按钮重新选择。

### Q: 点击位置不准确？
A: 后台点击模式默认点击目标窗口右下角的"挑战"按钮区域，如需调整位置请修改代码。

### Q: 程序打包为 exe？
A: 使用 PyInstaller 打包，注意将相关依赖一并打包。

## 许可证

MIT License
