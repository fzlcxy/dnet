"""
GUI主窗口实现
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
from typing import Dict, List, Optional

from dnet_parser import DnetParser, DnetFile, Protocol
from config_manager import ConfigManager, C2SConfig, C2SMapping, S2CResponse, OrderGroup


class ToolTip:
    """悬停提示组件"""

    def __init__(self, widget, text=""):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self._show_tip)
        self.widget.bind("<Leave>", self._hide_tip)

    def _show_tip(self, event=None):
        if not self.text or self.tip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Microsoft YaHei UI", 9))
        label.pack()

    def _hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

    def update_text(self, text):
        self.text = text


class ResponseEditDialog(tk.Toplevel):
    """编辑S2C响应对话框"""

    def __init__(self, parent, response: S2CResponse, existing_groups: list = None):
        super().__init__(parent)
        self.response = response
        self.existing_groups = existing_groups or []
        self.result = None

        self.title("编辑S2C响应")
        self.geometry("450x380")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._center_window()

    def _create_widgets(self):
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        row = 0
        # 顺序状态
        ttk.Label(frame, text="顺序状态:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ordered_frame = ttk.Frame(frame)
        ordered_frame.grid(row=row, column=1, sticky=tk.W, pady=5)
        self.ordered_var = tk.BooleanVar(value=self.response.ordered)
        ttk.Radiobutton(ordered_frame, text="顺序 (数字序号)", variable=self.ordered_var,
                        value=True).pack(side=tk.LEFT)
        ttk.Radiobutton(ordered_frame, text="无序 (x标记)", variable=self.ordered_var,
                        value=False).pack(side=tk.LEFT, padx=10)

        row += 1
        # 响应类型
        ttk.Label(frame, text="响应类型:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.type_var = tk.StringVar(value=self.response.type)
        type_combo = ttk.Combobox(frame, textvariable=self.type_var,
                                   values=["必然回包", "按条件回包"], state="readonly", width=15)
        type_combo.grid(row=row, column=1, sticky=tk.W, pady=5)

        row += 1
        # 回包次数
        ttk.Label(frame, text="回包次数:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.count_var = tk.StringVar(value=self.response.count)
        count_combo = ttk.Combobox(frame, textvariable=self.count_var,
                                    values=["一次", "多次"], state="readonly", width=15)
        count_combo.grid(row=row, column=1, sticky=tk.W, pady=5)

        row += 1
        # 顺序组
        ttk.Label(frame, text="顺序组:").grid(row=row, column=0, sticky=tk.W, pady=5)
        order_group_frame = ttk.Frame(frame)
        order_group_frame.grid(row=row, column=1, sticky=tk.W, pady=5)

        # 获取可用的组名选项（空 + 已有组名 + 新建提示）
        group_options = ["(无)"] + [g.name for g in self.existing_groups] + ["+ 新建组..."]
        current_group = self.response.order_group if self.response.order_group else "(无)"

        self.order_group_var = tk.StringVar(value=current_group)
        self.order_group_combo = ttk.Combobox(order_group_frame, textvariable=self.order_group_var,
                                               values=group_options, width=10)
        self.order_group_combo.pack(side=tk.LEFT)
        self.order_group_combo.bind("<<ComboboxSelected>>", self._on_group_selected)

        ttk.Label(order_group_frame, text="  (相同组名=顺序不确定)").pack(side=tk.LEFT)

        row += 1
        # 条件说明
        ttk.Label(frame, text="备注:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.condition_text = tk.Text(frame, width=35, height=5)
        self.condition_text.grid(row=row, column=1, sticky=tk.W, pady=5)
        self.condition_text.insert("1.0", self.response.condition)

        row += 1
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="确定", command=self._on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self._on_cancel).pack(side=tk.LEFT, padx=5)

    def _on_group_selected(self, event):
        """选择顺序组时"""
        if self.order_group_var.get() == "+ 新建组...":
            # 弹出输入框让用户输入新组名
            dialog = NewGroupDialog(self)
            self.wait_window(dialog)
            if dialog.result:
                self.order_group_var.set(dialog.result)
                # 更新下拉列表
                values = list(self.order_group_combo['values'])
                if dialog.result not in values:
                    values.insert(-1, dialog.result)  # 在"新建组"前插入
                    self.order_group_combo['values'] = values
            else:
                self.order_group_var.set("(无)")

    def _center_window(self):
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - self.winfo_width()) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _on_ok(self):
        group_value = self.order_group_var.get()
        if group_value == "(无)" or group_value == "+ 新建组...":
            group_value = ""

        self.result = {
            "type": self.type_var.get(),
            "condition": self.condition_text.get("1.0", tk.END).strip(),
            "count": self.count_var.get(),
            "order_group": group_value,
            "ordered": self.ordered_var.get()
        }
        self.destroy()

    def _on_cancel(self):
        self.destroy()


class NewGroupDialog(tk.Toplevel):
    """新建顺序组对话框"""

    def __init__(self, parent):
        super().__init__(parent)
        self.result = None

        self.title("新建顺序组")
        self.geometry("300x150")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._center_window()

    def _create_widgets(self):
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="组名 (如 A, B, C):").pack(anchor=tk.W, pady=5)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(frame, textvariable=self.name_var, width=20)
        name_entry.pack(anchor=tk.W, pady=5)
        name_entry.focus()

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="确定", command=self._on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self._on_cancel).pack(side=tk.LEFT, padx=5)

        self.bind("<Return>", lambda e: self._on_ok())
        self.bind("<Escape>", lambda e: self._on_cancel())

    def _center_window(self):
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - self.winfo_width()) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _on_ok(self):
        name = self.name_var.get().strip()
        if name:
            self.result = name
        self.destroy()

    def _on_cancel(self):
        self.destroy()


class OrderGroupEditDialog(tk.Toplevel):
    """编辑顺序组说明对话框"""

    def __init__(self, parent, group: OrderGroup):
        super().__init__(parent)
        self.group = group
        self.result = None

        self.title(f"编辑顺序组 [{group.name}]")
        self.geometry("400x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._center_window()

    def _create_widgets(self):
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=f"顺序组名称: {self.group.name}").pack(anchor=tk.W, pady=5)
        ttk.Label(frame, text="组说明 (描述该组内协议顺序不确定的原因):").pack(anchor=tk.W, pady=5)

        self.desc_text = tk.Text(frame, width=45, height=5)
        self.desc_text.pack(fill=tk.X, pady=5)
        self.desc_text.insert("1.0", self.group.description)
        self.desc_text.focus()

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="确定", command=self._on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self._on_cancel).pack(side=tk.LEFT, padx=5)

        self.bind("<Escape>", lambda e: self._on_cancel())

    def _center_window(self):
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - self.winfo_width()) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _on_ok(self):
        self.result = {
            "description": self.desc_text.get("1.0", tk.END).strip()
        }
        self.destroy()

    def _on_cancel(self):
        self.destroy()


# 保留旧名称以兼容
ConditionDialog = ResponseEditDialog


class SettingsDialog(tk.Toplevel):
    """设置目录对话框"""

    def __init__(self, parent, proto_dir: str, config_dir: str):
        super().__init__(parent)
        self.proto_dir = proto_dir
        self.config_dir = config_dir
        self.result = None

        self.title("设置目录")
        self.geometry("550x180")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._center_window()

    def _create_widgets(self):
        frame = ttk.Frame(self, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        # Proto目录
        ttk.Label(frame, text="Proto目录:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.proto_var = tk.StringVar(value=self.proto_dir)
        proto_entry = ttk.Entry(frame, textvariable=self.proto_var, width=50)
        proto_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=8)
        ttk.Button(frame, text="浏览...", command=self._browse_proto).grid(row=0, column=2, pady=8)

        # 配置输出目录
        ttk.Label(frame, text="配置输出目录:").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.config_var = tk.StringVar(value=self.config_dir)
        config_entry = ttk.Entry(frame, textvariable=self.config_var, width=50)
        config_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=8)
        ttk.Button(frame, text="浏览...", command=self._browse_config).grid(row=1, column=2, pady=8)

        frame.columnconfigure(1, weight=1)

        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=15)
        ttk.Button(btn_frame, text="确定", command=self._on_ok, width=10).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=self._on_cancel, width=10).pack(side=tk.LEFT, padx=10)

    def _browse_proto(self):
        path = filedialog.askdirectory(title="选择Proto目录", initialdir=self.proto_var.get())
        if path:
            self.proto_var.set(path)

    def _browse_config(self):
        path = filedialog.askdirectory(title="选择配置输出目录", initialdir=self.config_var.get())
        if path:
            self.config_var.set(path)

    def _center_window(self):
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - self.winfo_width()) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _on_ok(self):
        proto = self.proto_var.get().strip()
        config = self.config_var.get().strip()
        if not proto or not os.path.isdir(proto):
            messagebox.showerror("错误", "Proto目录不存在")
            return
        if not config:
            messagebox.showerror("错误", "请设置配置输出目录")
            return
        # 如果配置目录不存在，提示创建
        if not os.path.exists(config):
            if messagebox.askyesno("提示", f"目录不存在:\n{config}\n\n是否创建?"):
                try:
                    os.makedirs(config)
                except Exception as e:
                    messagebox.showerror("错误", f"创建目录失败: {e}")
                    return
            else:
                return

        self.result = {"proto_dir": proto, "config_dir": config}
        self.destroy()

    def _on_cancel(self):
        self.destroy()


class MainWindow(tk.Tk):
    """主窗口"""

    def __init__(self):
        super().__init__()

        self.title("协议配置GUI工具")
        self.geometry("1400x800")

        # 应用主题和样式
        self._setup_style()

        # 初始化路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.root_dir = os.path.dirname(script_dir)
        self.settings_file = os.path.join(script_dir, 'gui_settings.json')

        # 加载保存的设置或使用默认值
        settings = self._load_settings()
        self.proto_dir = settings.get('proto_dir', os.path.join(self.root_dir, 'proto'))
        self.config_dir = settings.get('config_dir', os.path.join(self.root_dir, 'clientconfig'))

        # 初始化解析器和配置管理器
        self.parser = DnetParser()
        self.config_manager = ConfigManager(self.proto_dir, self.config_dir)

        # 数据
        self.dnet_files: List[DnetFile] = []
        self.current_dnet: Optional[DnetFile] = None
        self.current_c2s: Optional[Protocol] = None
        self.current_config: Optional[C2SConfig] = None
        self.current_s2c_dnet: Optional[DnetFile] = None  # 当前选中的S2C dnet文件
        self.modified = False

        # 构建UI
        self._setup_menu()
        self._setup_main_frame()

        # 加载数据
        self._load_dnet_files()

        # 绑定快捷键
        self.bind("<Control-s>", lambda e: self._save_config())
        self.bind("<Control-z>", lambda e: self._undo())
        self.bind("<Control-y>", lambda e: self._redo())
        self.bind("<F5>", lambda e: self._refresh_dnet_files())

        # 关闭窗口时检查保存
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _load_settings(self) -> dict:
        """加载本地设置"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_settings(self):
        """保存设置到本地"""
        settings = {
            'proto_dir': self.proto_dir,
            'config_dir': self.config_dir
        }
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showwarning("警告", f"保存设置失败: {e}")

    def _setup_style(self):
        """设置主题和样式"""
        style = ttk.Style()
        # 使用clam主题（跨平台现代外观）
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')

        # 配置颜色方案
        self.colors = {
            'primary': '#4a90d9',
            'success': '#5cb85c',
            'warning': '#f0ad4e',
            'danger': '#d9534f',
            'bg_light': '#f5f5f5',
            'bg_alt': '#e9ecef',
            'text': '#333333'
        }

        # 配置Treeview样式
        style.configure("Treeview",
                        font=("Microsoft YaHei UI", 10),
                        rowheight=26)
        style.configure("Treeview.Heading",
                        font=("Microsoft YaHei UI", 10, "bold"))

        # 配置按钮样式
        style.configure("TButton",
                        font=("Microsoft YaHei UI", 9),
                        padding=5)

        # 工具栏按钮样式
        style.configure("Toolbar.TButton",
                        font=("Microsoft YaHei UI", 9),
                        padding=(10, 5))

        # 配置标签样式
        style.configure("TLabel",
                        font=("Microsoft YaHei UI", 10))
        style.configure("TLabelframe.Label",
                        font=("Microsoft YaHei UI", 10, "bold"))

        # 突出显示的面板样式（C2S列表和S2C配置）
        style.configure("Primary.TLabelframe.Label",
                        font=("Microsoft YaHei UI", 11, "bold"),
                        foreground="#2563eb")

        # 配置输入框样式
        style.configure("TEntry",
                        font=("Microsoft YaHei UI", 10))

    def _setup_menu(self):
        """设置菜单栏"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="保存配置 (Ctrl+S)", command=self._save_config)
        file_menu.add_separator()
        file_menu.add_command(label="设置目录...", command=self._show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_close)

        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="撤销 (Ctrl+Z)", command=self._undo)
        edit_menu.add_command(label="重做 (Ctrl+Y)", command=self._redo)

        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="验证所有配置", command=self._validate_all)
        tools_menu.add_command(label="刷新dnet文件列表", command=self._refresh_dnet_files)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)

    def _setup_main_frame(self):
        """设置主界面"""
        # 主分割面板
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 左侧面板 (S2C选择部分)
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=35)
        self._setup_left_panel(left_frame)

        # 右侧面板 (C2S和配置部分)
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=65)
        self._setup_right_panel(right_frame)

        # 状态栏
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # 左侧：主状态信息
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 中间：修改状态
        self.modified_var = tk.StringVar(value="")
        self.modified_label = ttk.Label(status_frame, textvariable=self.modified_var,
                                        relief=tk.SUNKEN, width=10, anchor=tk.CENTER)
        self.modified_label.pack(side=tk.LEFT, padx=1)

        # 右侧：统计信息
        self.stats_var = tk.StringVar(value="C2S: 0 | S2C: 0")
        stats_label = ttk.Label(status_frame, textvariable=self.stats_var,
                                relief=tk.SUNKEN, width=20, anchor=tk.CENTER)
        stats_label.pack(side=tk.LEFT, padx=1)

    def _setup_left_panel(self, parent):
        """设置左侧面板（C2S部分）"""
        # dnet文件选择面板（包含过滤栏）
        dnet_frame = ttk.LabelFrame(parent, text="选择C2S协议文件", padding=5)
        dnet_frame.pack(fill=tk.BOTH, padx=2, pady=2)

        # 过滤栏（在dnet文件面板内部顶部）
        filter_row = ttk.Frame(dnet_frame)
        filter_row.pack(fill=tk.X, pady=(0, 3))

        self.filter_var = tk.StringVar()
        self.filter_var.trace("w", lambda *args: self._filter_dnet_files())
        filter_entry = ttk.Entry(filter_row, textvariable=self.filter_var, width=15)
        filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.c2s_only_var = tk.BooleanVar(value=False)
        c2s_only_check = ttk.Checkbutton(filter_row, text="仅C2S",
                                          variable=self.c2s_only_var,
                                          command=self._filter_dnet_files)
        c2s_only_check.pack(side=tk.LEFT, padx=3)

        self.configured_only_var = tk.BooleanVar(value=False)
        configured_only_check = ttk.Checkbutton(filter_row, text="仅已配置",
                                                 variable=self.configured_only_var,
                                                 command=self._filter_dnet_files)
        configured_only_check.pack(side=tk.LEFT, padx=3)

        self.dnet_tree = ttk.Treeview(dnet_frame, selectmode="browse", show="tree", height=8)
        dnet_scroll = ttk.Scrollbar(dnet_frame, orient=tk.VERTICAL, command=self.dnet_tree.yview)
        self.dnet_tree.configure(yscrollcommand=dnet_scroll.set)
        self.dnet_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dnet_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.dnet_tree.bind("<<TreeviewSelect>>", self._on_dnet_selected)

        # 选择S2C协议面板（从右侧移到左侧）
        select_frame = ttk.LabelFrame(parent, text="选择S2C协议（双击添加到配置）", padding=5)
        select_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        select_paned = ttk.PanedWindow(select_frame, orient=tk.HORIZONTAL)
        select_paned.pack(fill=tk.BOTH, expand=True)

        # 左侧：包含S2C的dnet文件
        s2c_dnet_frame = ttk.Frame(select_paned)
        select_paned.add(s2c_dnet_frame, weight=35)

        ttk.Label(s2c_dnet_frame, text="包含S2C的dnet文件").pack(anchor=tk.W)
        self.s2c_dnet_list = tk.Listbox(s2c_dnet_frame, selectmode=tk.SINGLE)
        s2c_dnet_scroll = ttk.Scrollbar(s2c_dnet_frame, orient=tk.VERTICAL, command=self.s2c_dnet_list.yview)
        self.s2c_dnet_list.configure(yscrollcommand=s2c_dnet_scroll.set)
        self.s2c_dnet_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        s2c_dnet_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.s2c_dnet_list.bind("<<ListboxSelect>>", self._on_s2c_dnet_selected)

        # 右侧：S2C协议列表
        s2c_list_frame = ttk.Frame(select_paned)
        select_paned.add(s2c_list_frame, weight=65)

        ttk.Label(s2c_list_frame, text="S2C协议列表").pack(anchor=tk.W)
        self.s2c_list = tk.Listbox(s2c_list_frame, selectmode=tk.SINGLE)
        s2c_scroll = ttk.Scrollbar(s2c_list_frame, orient=tk.VERTICAL, command=self.s2c_list.yview)
        self.s2c_list.configure(yscrollcommand=s2c_scroll.set)
        self.s2c_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        s2c_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.s2c_list.bind("<Double-1>", self._on_s2c_double_click)
        self.s2c_list.bind("<<ListboxSelect>>", self._on_s2c_selected)

        # C2S详情面板（较小，固定高度）
        c2s_detail_frame = ttk.LabelFrame(parent, text="C2S详情", padding=5)
        c2s_detail_frame.pack(fill=tk.X, padx=2, pady=2)

        self.c2s_detail_text = tk.Text(c2s_detail_frame, height=6, state=tk.DISABLED,
                                       font=("Microsoft YaHei UI", 9))
        c2s_detail_scroll = ttk.Scrollbar(c2s_detail_frame, orient=tk.VERTICAL,
                                           command=self.c2s_detail_text.yview)
        self.c2s_detail_text.configure(yscrollcommand=c2s_detail_scroll.set)
        self.c2s_detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        c2s_detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _setup_right_panel(self, parent):
        """设置右侧面板（S2C配置部分）"""
        # C2S协议面板（从左侧移到右侧顶部，突出显示）
        c2s_frame = ttk.LabelFrame(parent, text="C2S协议列表", padding=5, style="Primary.TLabelframe")
        c2s_frame.pack(fill=tk.BOTH, padx=2, pady=2)

        self.c2s_list = tk.Listbox(c2s_frame, selectmode=tk.SINGLE, font=("Microsoft YaHei UI", 10), height=11)
        c2s_scroll = ttk.Scrollbar(c2s_frame, orient=tk.VERTICAL, command=self.c2s_list.yview)
        self.c2s_list.configure(yscrollcommand=c2s_scroll.set)
        self.c2s_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        c2s_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.c2s_list.bind("<<ListboxSelect>>", self._on_c2s_selected)

        # 配置的S2C面板（主要区域，突出显示）
        config_frame = ttk.LabelFrame(parent, text="S2C回包配置（双击编辑）", padding=5, style="Primary.TLabelframe")
        config_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # 配置列表容器（左边列表，右边按钮）
        config_container = ttk.Frame(config_frame)
        config_container.pack(fill=tk.BOTH, expand=True)

        # 配置列表
        columns = ("order", "protocol", "type", "count", "condition")
        self.config_tree = ttk.Treeview(config_container, columns=columns, show="headings", height=8)
        self.config_tree.heading("order", text="顺序")
        self.config_tree.heading("protocol", text="协议名称")
        self.config_tree.heading("type", text="类型")
        self.config_tree.heading("count", text="次数")
        self.config_tree.heading("condition", text="备注")
        self.config_tree.column("order", width=60)
        self.config_tree.column("protocol", width=180)
        self.config_tree.column("type", width=80)
        self.config_tree.column("count", width=50)
        self.config_tree.column("condition", width=200)

        config_scroll = ttk.Scrollbar(config_container, orient=tk.VERTICAL, command=self.config_tree.yview)
        self.config_tree.configure(yscrollcommand=config_scroll.set)
        self.config_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        config_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.config_tree.bind("<Double-1>", self._on_config_double_click)
        self.config_tree.bind("<Button-3>", self._on_config_right_click)
        self.config_tree.bind("<<TreeviewSelect>>", self._on_config_selected)

        # 右键菜单
        self.config_menu = tk.Menu(self, tearoff=0)
        self.config_menu.add_command(label="上移", command=self._move_up)
        self.config_menu.add_command(label="下移", command=self._move_down)
        self.config_menu.add_separator()
        self.config_menu.add_command(label="编辑", command=self._edit_selected_response)
        self.config_menu.add_command(label="编辑顺序组说明...", command=self._edit_order_group)
        self.config_menu.add_separator()
        self.config_menu.add_command(label="删除", command=self._remove_response)

        # 底部：S2C详情面板（较小，与左侧对称）
        s2c_detail_frame = ttk.LabelFrame(parent, text="S2C详情", padding=5)
        s2c_detail_frame.pack(fill=tk.X, padx=2, pady=2)

        self.s2c_detail_text = tk.Text(s2c_detail_frame, height=6, state=tk.DISABLED,
                                       font=("Microsoft YaHei UI", 9))
        s2c_detail_scroll = ttk.Scrollbar(s2c_detail_frame, orient=tk.VERTICAL,
                                           command=self.s2c_detail_text.yview)
        self.s2c_detail_text.configure(yscrollcommand=s2c_detail_scroll.set)
        self.s2c_detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        s2c_detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _update_modified_status(self):
        """更新修改状态显示"""
        if self.modified:
            self.modified_var.set("已修改")
        else:
            self.modified_var.set("")

    def _set_modified(self, value: bool):
        """设置修改状态并更新显示"""
        self.modified = value
        self._update_modified_status()

    def _update_stats(self):
        """更新统计信息"""
        if self.current_config:
            c2s_count = len([m for m in self.current_config.c2s_mappings.values() if m.responses])
            s2c_count = sum(len(m.responses) for m in self.current_config.c2s_mappings.values())
            self.stats_var.set(f"C2S: {c2s_count} | S2C: {s2c_count}")
        else:
            self.stats_var.set("C2S: 0 | S2C: 0")

    def _load_dnet_files(self):
        """加载所有.dnet文件"""
        self.dnet_files = self.parser.scan_directory(self.proto_dir)
        self._populate_dnet_tree()
        self._populate_s2c_dnet_list()
        self.status_var.set(f"已加载 {len(self.dnet_files)} 个dnet文件")

    def _has_config(self, dnet: DnetFile) -> bool:
        """检查dnet文件是否有配置"""
        config = self.config_manager.load_config(dnet.relative_path)
        if not config:
            return False
        for mapping in config.c2s_mappings.values():
            if mapping.responses:
                return True
        return False

    def _get_configured_c2s_names(self, dnet: DnetFile) -> set:
        """获取已配置的C2S协议名称集合"""
        config = self.config_manager.load_config(dnet.relative_path)
        if not config:
            return set()
        return {name for name, mapping in config.c2s_mappings.items() if mapping.responses}

    def _populate_dnet_tree(self):
        """填充dnet文件树"""
        self.dnet_tree.delete(*self.dnet_tree.get_children())

        filter_text = self.filter_var.get().lower()
        c2s_only = self.c2s_only_var.get()
        configured_only = self.configured_only_var.get()

        # 配置Treeview标签样式
        self.dnet_tree.tag_configure("configured", foreground="#228B22")

        # 构建目录树
        dirs: Dict[str, str] = {}  # path -> tree_id

        for dnet in self.dnet_files:
            # 应用过滤
            if filter_text and filter_text not in dnet.relative_path.lower():
                continue
            if c2s_only and not dnet.has_c2s():
                continue

            # 检查是否有配置
            has_config = self._has_config(dnet)
            if configured_only and not has_config:
                continue

            # 获取目录路径
            dir_path = os.path.dirname(dnet.relative_path)

            # 创建目录节点
            parent = ""
            if dir_path:
                parts = dir_path.replace("\\", "/").split("/")
                current_path = ""
                for part in parts:
                    current_path = os.path.join(current_path, part) if current_path else part
                    if current_path not in dirs:
                        dirs[current_path] = self.dnet_tree.insert(parent, "end", text=part, open=True)
                    parent = dirs[current_path]

            # 添加文件节点（已配置的显示绿色标记）
            if has_config:
                display_text = f"● {dnet.file_name} - {dnet.description}"
                self.dnet_tree.insert(parent, "end", text=display_text, values=(dnet.relative_path,), tags=("configured",))
            else:
                display_text = f"{dnet.file_name} - {dnet.description}"
                self.dnet_tree.insert(parent, "end", text=display_text, values=(dnet.relative_path,))

    def _populate_s2c_dnet_list(self):
        """填充包含S2C的dnet文件列表"""
        self.s2c_dnet_list.delete(0, tk.END)
        for dnet in self.dnet_files:
            if dnet.has_s2c():
                self.s2c_dnet_list.insert(tk.END, f"{dnet.relative_path} - {dnet.description}")

    def _filter_dnet_files(self):
        """过滤dnet文件列表"""
        self._populate_dnet_tree()

    def _refresh_dnet_files(self):
        """刷新dnet文件列表"""
        self._load_dnet_files()
        messagebox.showinfo("刷新", "dnet文件列表已刷新")

    def _on_dnet_selected(self, event):
        """选择dnet文件时"""
        selection = self.dnet_tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.dnet_tree.item(item, "values")
        if not values:
            return

        relative_path = values[0]
        dnet = next((d for d in self.dnet_files if d.relative_path == relative_path), None)
        if not dnet:
            return

        # 检查是否需要保存
        if self.modified:
            if messagebox.askyesno("保存", "当前配置已修改，是否保存？"):
                self._save_config()

        self.current_dnet = dnet
        self.current_c2s = None

        # 加载配置
        self.current_config = self.config_manager.load_config(dnet.relative_path)
        if not self.current_config:
            self.current_config = self.config_manager.create_empty_config(dnet)

        # 更新C2S列表（已配置的显示绿色标记）
        self.c2s_list.delete(0, tk.END)
        configured_c2s = self._get_configured_c2s_names(dnet)
        for c2s in dnet.c2s_list:
            if c2s.name in configured_c2s:
                self.c2s_list.insert(tk.END, f"● {c2s.name} - {c2s.description}")
                self.c2s_list.itemconfig(tk.END, fg="#228B22")
            else:
                self.c2s_list.insert(tk.END, f"{c2s.name} - {c2s.description}")

        # 清空详情和配置
        self._clear_c2s_detail()
        self._clear_config_tree()
        self._set_modified(False)

        # 如果有C2S协议，自动选中第一个
        if dnet.c2s_list:
            self.c2s_list.selection_set(0)
            self.current_c2s = dnet.c2s_list[0]
            self._show_c2s_detail(self.current_c2s)
            self._load_c2s_config()

        self.status_var.set(f"已选择: {dnet.relative_path}")

    def _refresh_c2s_list_marks(self):
        """刷新C2S列表的配置标记"""
        if not self.current_dnet:
            return

        # 保存当前选中项
        current_selection = self.c2s_list.curselection()

        # 重新获取已配置的C2S名称
        configured_c2s = {name for name, mapping in self.current_config.c2s_mappings.items()
                         if mapping.responses} if self.current_config else set()

        # 更新列表
        self.c2s_list.delete(0, tk.END)
        for c2s in self.current_dnet.c2s_list:
            if c2s.name in configured_c2s:
                self.c2s_list.insert(tk.END, f"● {c2s.name} - {c2s.description}")
                self.c2s_list.itemconfig(tk.END, fg="#228B22")
            else:
                self.c2s_list.insert(tk.END, f"{c2s.name} - {c2s.description}")

        # 恢复选中项
        if current_selection:
            self.c2s_list.selection_set(current_selection[0])

    def _on_c2s_selected(self, event):
        """选择C2S协议时"""
        selection = self.c2s_list.curselection()
        if not selection or not self.current_dnet:
            return

        index = selection[0]
        if index < len(self.current_dnet.c2s_list):
            self.current_c2s = self.current_dnet.c2s_list[index]
            self._show_c2s_detail(self.current_c2s)
            self._load_c2s_config()

    def _show_c2s_detail(self, protocol: Protocol):
        """显示C2S协议详情"""
        self.c2s_detail_text.config(state=tk.NORMAL)
        self.c2s_detail_text.delete("1.0", tk.END)

        text = f"协议名称: {protocol.name}\n"
        text += f"描述: {protocol.description}\n"
        text += f"\n字段列表:\n"
        for field in protocol.fields:
            text += f"  - {field.name} ({field.type_info}): {field.description}\n"

        self.c2s_detail_text.insert("1.0", text)
        self.c2s_detail_text.config(state=tk.DISABLED)

    def _clear_c2s_detail(self):
        """清空C2S详情"""
        self.c2s_detail_text.config(state=tk.NORMAL)
        self.c2s_detail_text.delete("1.0", tk.END)
        self.c2s_detail_text.config(state=tk.DISABLED)

    def _load_c2s_config(self):
        """加载当前C2S的配置"""
        self._clear_config_tree()

        if not self.current_c2s or not self.current_config:
            self._update_stats()
            return

        mapping = self.current_config.c2s_mappings.get(self.current_c2s.name)
        if not mapping:
            self._update_stats()
            return

        # 配置颜色标签用于区分不同的顺序组
        group_colors = {}
        color_palette = ["#d4edfc", "#fce8d4", "#d4fcd8", "#fcd4ed", "#e8d4fc", "#fcd4d4"]
        color_idx = 0

        # 配置交替行颜色
        self.config_tree.tag_configure("oddrow", background="#ffffff")
        self.config_tree.tag_configure("evenrow", background="#f5f5f5")

        for idx, resp in enumerate(mapping.responses):
            # 顺序显示：有序用数字，无序用x
            if resp.ordered:
                if resp.order_group:
                    order_display = f"{resp.order}[{resp.order_group}]"
                else:
                    order_display = str(resp.order)
            else:
                if resp.order_group:
                    order_display = f"x[{resp.order_group}]"
                else:
                    order_display = "x"

            # 分配顺序组颜色
            if resp.order_group and resp.order_group not in group_colors:
                group_colors[resp.order_group] = color_palette[color_idx % len(color_palette)]
                color_idx += 1

            item_id = self.config_tree.insert("", tk.END, values=(
                order_display, resp.protocol, resp.type, resp.count, resp.condition
            ))

            # 设置行标签（顺序组优先，否则用交替行）
            if resp.order_group and resp.order_group in group_colors:
                self.config_tree.tag_configure(f"group_{resp.order_group}",
                                                background=group_colors[resp.order_group])
                self.config_tree.item(item_id, tags=(f"group_{resp.order_group}",))
            else:
                row_tag = "oddrow" if idx % 2 == 0 else "evenrow"
                self.config_tree.item(item_id, tags=(row_tag,))

        self._update_stats()

    def _clear_config_tree(self):
        """清空配置树"""
        self.config_tree.delete(*self.config_tree.get_children())

    def _on_s2c_dnet_selected(self, event):
        """选择S2C的dnet文件时"""
        selection = self.s2c_dnet_list.curselection()
        if not selection:
            return

        index = selection[0]
        # 找到对应的dnet文件
        s2c_dnet_files = [d for d in self.dnet_files if d.has_s2c()]
        if index < len(s2c_dnet_files):
            dnet = s2c_dnet_files[index]
            self.current_s2c_dnet = dnet  # 保存当前选中的S2C dnet
            self._populate_s2c_list(dnet)

    def _populate_s2c_list(self, dnet: DnetFile):
        """填充S2C协议列表"""
        self.s2c_list.delete(0, tk.END)
        for s2c in dnet.s2c_list:
            self.s2c_list.insert(tk.END, f"{s2c.name} - {s2c.description}")

    def _on_s2c_selected(self, event):
        """选择S2C协议时"""
        if not self.current_s2c_dnet:
            return

        s2c_selection = self.s2c_list.curselection()
        if not s2c_selection:
            return

        s2c_index = s2c_selection[0]
        if s2c_index < len(self.current_s2c_dnet.s2c_list):
            self._show_s2c_detail(self.current_s2c_dnet.s2c_list[s2c_index])

    def _show_s2c_detail(self, protocol: Protocol):
        """显示S2C协议详情"""
        self.s2c_detail_text.config(state=tk.NORMAL)
        self.s2c_detail_text.delete("1.0", tk.END)

        text = f"协议名称: {protocol.name}\n"
        text += f"描述: {protocol.description}\n"
        text += f"\n字段列表:\n"
        for field in protocol.fields:
            text += f"  - {field.name} ({field.type_info}): {field.description}\n"

        self.s2c_detail_text.insert("1.0", text)
        self.s2c_detail_text.config(state=tk.DISABLED)

    def _on_s2c_double_click(self, event):
        """双击S2C协议添加到配置"""
        if not self.current_c2s or not self.current_config:
            messagebox.showwarning("提示", "请先选择一个C2S协议")
            return

        if not self.current_s2c_dnet:
            messagebox.showwarning("提示", "请先在左侧选择包含S2C的dnet文件")
            return

        # 通过双击位置获取选中项
        s2c_index = self.s2c_list.nearest(event.y)
        if s2c_index < 0 or s2c_index >= len(self.current_s2c_dnet.s2c_list):
            return

        s2c = self.current_s2c_dnet.s2c_list[s2c_index]
        self._add_response(s2c.name)

    def _add_response(self, protocol_name: str):
        """添加S2C响应"""
        if not self.current_c2s or not self.current_config:
            return

        c2s_name = self.current_c2s.name
        if c2s_name not in self.current_config.c2s_mappings:
            self.current_config.c2s_mappings[c2s_name] = C2SMapping(
                description=self.current_c2s.description
            )

        mapping = self.current_config.c2s_mappings[c2s_name]

        # 计算新的序号（只计算有序项）
        new_order = sum(1 for r in mapping.responses if r.ordered) + 1

        response = S2CResponse(
            protocol=protocol_name,
            order=new_order,
            type="必然回包",
            condition="",
            ordered=True  # 默认有序
        )
        mapping.responses.append(response)

        # 刷新显示
        self._load_c2s_config()

        self._set_modified(True)
        self.status_var.set(f"已添加响应: {protocol_name}")

    def _move_up(self):
        """上移选中的响应"""
        selection = self.config_tree.selection()
        if not selection or not self.current_c2s or not self.current_config:
            return

        item = selection[0]
        index = self.config_tree.index(item)
        if index == 0:
            return

        c2s_name = self.current_c2s.name
        mapping = self.current_config.c2s_mappings.get(c2s_name)
        if not mapping:
            return

        # 交换顺序
        mapping.responses[index], mapping.responses[index - 1] = \
            mapping.responses[index - 1], mapping.responses[index]

        # 更新顺序号
        self._update_response_orders(mapping)
        self._load_c2s_config()

        # 重新选中
        children = self.config_tree.get_children()
        if index - 1 < len(children):
            self.config_tree.selection_set(children[index - 1])

        self._set_modified(True)

    def _move_down(self):
        """下移选中的响应"""
        selection = self.config_tree.selection()
        if not selection or not self.current_c2s or not self.current_config:
            return

        item = selection[0]
        index = self.config_tree.index(item)

        c2s_name = self.current_c2s.name
        mapping = self.current_config.c2s_mappings.get(c2s_name)
        if not mapping or index >= len(mapping.responses) - 1:
            return

        # 交换顺序
        mapping.responses[index], mapping.responses[index + 1] = \
            mapping.responses[index + 1], mapping.responses[index]

        # 更新顺序号
        self._update_response_orders(mapping)
        self._load_c2s_config()

        # 重新选中
        children = self.config_tree.get_children()
        if index + 1 < len(children):
            self.config_tree.selection_set(children[index + 1])

        self._set_modified(True)

    def _update_response_orders(self, mapping: C2SMapping):
        """更新响应的顺序号（只更新有序项）"""
        order_num = 1
        for resp in mapping.responses:
            if resp.ordered:
                resp.order = order_num
                order_num += 1
            else:
                resp.order = 0

    def _on_config_right_click(self, event):
        """右键点击配置项，显示菜单"""
        item = self.config_tree.identify_row(event.y)
        if item:
            self.config_tree.selection_set(item)
            self.config_menu.post(event.x_root, event.y_root)

    def _edit_selected_response(self):
        """编辑选中的响应"""
        selection = self.config_tree.selection()
        if not selection or not self.current_c2s or not self.current_config:
            return

        item = selection[0]
        index = self.config_tree.index(item)

        c2s_name = self.current_c2s.name
        mapping = self.current_config.c2s_mappings.get(c2s_name)
        if not mapping or index >= len(mapping.responses):
            return

        response = mapping.responses[index]
        self._edit_condition(response)

    def _on_config_selected(self, event):
        """选中配置项时显示S2C详情"""
        selection = self.config_tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.config_tree.item(item, "values")
        if not values or len(values) < 2:
            return

        protocol_name = values[1]  # 协议名称在第二列

        # 在所有dnet文件中查找该协议
        for dnet in self.dnet_files:
            for s2c in dnet.s2c_list:
                if s2c.name == protocol_name:
                    self._show_s2c_detail(s2c)
                    return

    def _on_config_double_click(self, event):
        """双击配置项，弹出对话框编辑类型和条件"""
        item = self.config_tree.identify_row(event.y)

        if not item or not self.current_c2s or not self.current_config:
            return

        index = self.config_tree.index(item)
        c2s_name = self.current_c2s.name
        mapping = self.current_config.c2s_mappings.get(c2s_name)
        if not mapping or index >= len(mapping.responses):
            return

        response = mapping.responses[index]
        self._edit_condition(response)

    def _edit_condition(self, response):
        """编辑响应配置"""
        # 获取当前C2S的已有顺序组
        existing_groups = []
        if self.current_c2s and self.current_config:
            mapping = self.current_config.c2s_mappings.get(self.current_c2s.name)
            if mapping:
                existing_groups = mapping.order_groups

        dialog = ResponseEditDialog(self, response, existing_groups)
        self.wait_window(dialog)

        if dialog.result:
            response.type = dialog.result["type"]
            response.condition = dialog.result["condition"]
            response.count = dialog.result["count"]
            new_group = dialog.result["order_group"]
            response.order_group = new_group
            response.ordered = dialog.result["ordered"]

            # 如果是新组名，自动添加到order_groups
            if new_group and self.current_c2s and self.current_config:
                mapping = self.current_config.c2s_mappings.get(self.current_c2s.name)
                if mapping and not any(g.name == new_group for g in mapping.order_groups):
                    mapping.order_groups.append(OrderGroup(name=new_group, description=""))

            # 重新计算有序项的序号
            self._recalculate_orders()
            self._load_c2s_config()
            self._set_modified(True)

    def _recalculate_orders(self):
        """重新计算有序项的序号"""
        if not self.current_c2s or not self.current_config:
            return

        mapping = self.current_config.c2s_mappings.get(self.current_c2s.name)
        if not mapping:
            return

        # 只为有序项重新编号
        order_num = 1
        for resp in mapping.responses:
            if resp.ordered:
                resp.order = order_num
                order_num += 1
            else:
                resp.order = 0  # 无序项order为0

    def _edit_order_group(self):
        """编辑选中响应的顺序组说明"""
        selection = self.config_tree.selection()
        if not selection or not self.current_c2s or not self.current_config:
            return

        item = selection[0]
        index = self.config_tree.index(item)

        c2s_name = self.current_c2s.name
        mapping = self.current_config.c2s_mappings.get(c2s_name)
        if not mapping or index >= len(mapping.responses):
            return

        response = mapping.responses[index]
        if not response.order_group:
            messagebox.showinfo("提示", "该响应没有设置顺序组")
            return

        # 查找或创建顺序组
        group = next((g for g in mapping.order_groups if g.name == response.order_group), None)
        if not group:
            group = OrderGroup(name=response.order_group, description="")
            mapping.order_groups.append(group)

        dialog = OrderGroupEditDialog(self, group)
        self.wait_window(dialog)

        if dialog.result:
            group.description = dialog.result["description"]
            self._set_modified(True)
            self._load_c2s_config()  # 刷新显示
            self.status_var.set(f"已更新顺序组 [{group.name}] 的说明")

    def _set_condition(self):
        """设置响应条件（按钮方式，已废弃但保留兼容）"""
        selection = self.config_tree.selection()
        if not selection or not self.current_c2s or not self.current_config:
            return

        item = selection[0]
        index = self.config_tree.index(item)

        c2s_name = self.current_c2s.name
        mapping = self.current_config.c2s_mappings.get(c2s_name)
        if not mapping or index >= len(mapping.responses):
            return

        response = mapping.responses[index]
        self._edit_condition(response)

    def _remove_response(self):
        """删除选中的响应"""
        selection = self.config_tree.selection()
        if not selection or not self.current_c2s or not self.current_config:
            return

        if not messagebox.askyesno("确认", "确定要删除选中的响应吗？"):
            return

        item = selection[0]
        index = self.config_tree.index(item)

        c2s_name = self.current_c2s.name
        mapping = self.current_config.c2s_mappings.get(c2s_name)
        if not mapping or index >= len(mapping.responses):
            return

        del mapping.responses[index]
        self._update_response_orders(mapping)
        self._load_c2s_config()

        self._set_modified(True)
        self.status_var.set("已删除响应")

    def _save_config(self):
        """保存配置"""
        if not self.current_dnet or not self.current_config:
            messagebox.showwarning("提示", "没有可保存的配置")
            return

        # 验证配置
        warnings = self.config_manager.validate_config(
            self.current_config, self.current_dnet, self.dnet_files
        )
        if warnings:
            msg = "配置存在以下警告：\n\n" + "\n".join(warnings) + "\n\n是否继续保存？"
            if not messagebox.askyesno("验证警告", msg):
                return

        if self.config_manager.save_config(self.current_dnet.relative_path, self.current_config):
            self._set_modified(False)
            self.status_var.set("配置已保存")
            # 刷新标记显示
            self._refresh_c2s_list_marks()
            self._populate_dnet_tree()
            messagebox.showinfo("保存成功", "配置已成功保存")
        else:
            messagebox.showerror("保存失败", "配置保存失败，请检查文件权限")

    def _validate_all(self):
        """验证所有配置"""
        all_warnings = []

        for dnet in self.dnet_files:
            config = self.config_manager.load_config(dnet.relative_path)
            if config:
                warnings = self.config_manager.validate_config(config, dnet, self.dnet_files)
                for w in warnings:
                    all_warnings.append(f"[{dnet.relative_path}] {w}")

        if all_warnings:
            msg = "发现以下问题：\n\n" + "\n".join(all_warnings[:20])
            if len(all_warnings) > 20:
                msg += f"\n\n... 还有 {len(all_warnings) - 20} 条警告"
            messagebox.showwarning("验证结果", msg)
        else:
            messagebox.showinfo("验证结果", "所有配置验证通过")

    def _undo(self):
        """撤销（待实现）"""
        messagebox.showinfo("提示", "撤销功能尚未实现")

    def _redo(self):
        """重做（待实现）"""
        messagebox.showinfo("提示", "重做功能尚未实现")

    def _show_settings(self):
        """显示设置目录对话框"""
        dialog = SettingsDialog(self, self.proto_dir, self.config_dir)
        self.wait_window(dialog)

        if dialog.result:
            new_proto = dialog.result["proto_dir"]
            new_config = dialog.result["config_dir"]

            # 检查是否有变化
            if new_proto != self.proto_dir or new_config != self.config_dir:
                # 检查是否需要保存当前配置
                if self.modified:
                    if messagebox.askyesno("保存", "当前配置已修改，是否先保存？"):
                        self._save_config()

                # 更新目录
                self.proto_dir = new_proto
                self.config_dir = new_config
                self.config_manager = ConfigManager(self.proto_dir, self.config_dir)

                # 保存设置到本地
                self._save_settings()

                # 重新加载
                self.current_dnet = None
                self.current_c2s = None
                self.current_config = None
                self._load_dnet_files()
                self._clear_c2s_detail()
                self._clear_config_tree()
                self.c2s_list.delete(0, tk.END)
                self._set_modified(False)

                self.status_var.set(f"已切换目录: {self.proto_dir}")

    def _show_help(self):
        """显示帮助"""
        help_text = """协议配置GUI工具使用说明

1. 在左侧选择dnet文件和C2S协议
2. 在右侧下方选择包含S2C的dnet文件
3. 双击S2C协议添加到配置
4. 使用上移/下移按钮调整顺序
5. 使用设置条件按钮配置响应类型
6. 按Ctrl+S保存配置

快捷键:
- Ctrl+S: 保存配置
- Ctrl+Z: 撤销
- Ctrl+Y: 重做
"""
        messagebox.showinfo("使用说明", help_text)

    def _show_about(self):
        """显示关于"""
        messagebox.showinfo("关于", "协议配置GUI工具\n版本 1.0\n\n用于配置C2S到S2C的响应映射关系")

    def _on_close(self):
        """关闭窗口"""
        if self.modified:
            result = messagebox.askyesnocancel("保存", "当前配置已修改，是否保存？")
            if result is None:  # Cancel
                return
            if result:  # Yes
                self._save_config()

        self.destroy()


if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()
