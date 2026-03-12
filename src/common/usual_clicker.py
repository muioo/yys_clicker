"""
鼠标自动点击脚本 - 命令行模式
按 F6 启动/停止自动点击
"""
import keyboard
from core.mouse_clicker import MouseClicker, BackgroundClicker


def main_cli():
    print("=" * 50)
    print("       鼠标自动点击脚本")
    print("=" * 50)
    print("模式选择：")
    print("  [1] 前台点击 - 直接点击屏幕")
    print("  [2] 后台点击 - 点击 GLEmulator.exe 窗口")
    print("=" * 50)

    choice = input("请选择模式 (1/2): ").strip()

    # 运行时长设置
    print("=" * 50)
    duration_input = input("是否设置运行时长限制？(y/n，默认n): ").strip().lower()
    run_duration = None

    if duration_input == 'y':
        minutes_input = input("请输入运行时长（分钟）: ").strip()
        try:
            minutes = float(minutes_input)
            if minutes > 0:
                run_duration = minutes * 60  # 转换为秒
                print(f"[设置] 将在 {minutes} 分钟后自动停止")
            else:
                print("[提示] 时长必须大于0，将无限运行")
        except ValueError:
            print("[错误] 输入格式错误，将无限运行")

    if choice == "2":
        # 后台点击模式
        clicker = BackgroundClicker(target_process="GLEmulator.exe", clicks_per_second=1, run_duration=run_duration)
        mode = "后台"
    else:
        # 前台点击模式
        clicker = MouseClicker(clicks_per_second=2, run_duration=run_duration)
        mode = "前台"

    print("=" * 50)
    print(f"当前模式: {mode}点击")
    if run_duration:
        print(f"运行时长: {run_duration / 60:.1f} 分钟后自动停止")
    else:
        print(f"运行时长: 无限运行（需手动停止）")
    print("操作说明：")
    print("  [F6]  - 启动/停止自动点击")
    print("  [ESC] - 退出程序")
    print("=" * 50)

    def toggle_clicker():
        if clicker.is_running():
            clicker.stop()
        else:
            clicker.start()

    # 注册快捷键
    keyboard.on_press_key("f6", lambda _: toggle_clicker())
    keyboard.wait("esc")

    # 确保停止点击器
    if clicker.is_running():
        clicker.stop()

    print("\n[退出] 程序已退出")


if __name__ == '__main__':
    main_cli()
