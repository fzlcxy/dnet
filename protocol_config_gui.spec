# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for 协议配置GUI工具
"""

import os
import sys

block_cipher = None

# 源代码目录
script_dir = os.path.join(os.path.dirname(os.path.abspath(SPEC)), 'clientscript')

a = Analysis(
    [os.path.join(script_dir, 'main.py')],
    pathex=[script_dir],
    binaries=[],
    datas=[],
    hiddenimports=[],
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

# 单文件模式 - 所有依赖打包到一个exe中
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='协议配置工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
