# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['hutuzudui\\main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'win32timezone',
        'win32cred',
        'win32crypt',
        'win32file',
        'win32gui',
        'win32con',
        'win32process',
        'win32api',
        'psutil',
        'keyboard',
        'pyautogui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MouseClicker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加 .ico 图标文件路径
)
