#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
协议配置GUI工具 - 主程序入口
"""
import sys
import os

# 将脚本目录添加到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from gui_main_window import MainWindow


def main():
    app = MainWindow()
    app.mainloop()


if __name__ == '__main__':
    main()
