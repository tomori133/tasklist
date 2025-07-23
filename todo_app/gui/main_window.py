# todo_app/gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from typing import Optional, Dict
from ..cli.core import TaskManager
import logging
import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TodoApp:
    def __init__(self, root):
        """初始化应用程序

        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.root.title("待办事项管理 v2.0")

        # 初始化核心管理器
        self.manager = TaskManager(storage_type='sqlite')

        # 初始化UI
        self._setup_ui()
        self._load_tasks()

        # 窗口设置
        self._center_window(1000, 700)
        self.root.minsize(800, 600)

    def _setup_styles(self):
        """设置应用程序样式"""
        style = ttk.Style()

        # 使用clam主题作为基础
        style.theme_use('clam')

        # 主窗口背景
        style.configure('.', background='#f5f5f5')

        # 按钮样式
        style.configure('TButton',
                        font=('Segoe UI', 10),
                        padding=6,
                        relief=tk.FLAT,
                        background='#e1e1e1',
                        foreground='#333333')
        style.map('TButton',
                  background=[('active', '#d5d5d5'), ('pressed', '#c9c9c9')],
                  relief=[('pressed', 'sunken'), ('!pressed', 'flat')])

        # 工具栏按钮特殊样式
        style.configure('Toolbutton.TButton',
                        font=('Segoe UI', 10, 'bold'),
                        padding=8)

        # 标签样式
        style.configure('TLabel',
                        font=('Segoe UI', 10),
                        background='#f5f5f5',
                        foreground='#333333')

        # 输入框样式
        style.configure('TEntry',
                        fieldbackground='white',
                        foreground='#333333',
                        padding=5)

        # 下拉框样式
        style.configure('TCombobox',
                        fieldbackground='white',
                        foreground='#333333',
                        padding=5)

        # 树状视图样式
        style.configure('Treeview',
                        font=('Segoe UI', 10),
                        rowheight=30,
                        background='white',
                        fieldbackground='white',
                        foreground='#333333',
                        bordercolor='#e1e1e1',
                        borderwidth=1)
        style.configure('Treeview.Heading',
                        font=('Segoe UI', 10, 'bold'),
                        background='#e1e1e1',
                        foreground='#333333',
                        relief=tk.FLAT)
        style.map('Treeview',
                  background=[('selected', '#4a98db')],
                  foreground=[('selected', 'white')])

        # 滚动条样式
        style.configure('Vertical.TScrollbar',
                        background='#e1e1e1',
                        troughcolor='#f5f5f5',
                        relief=tk.FLAT,
                        bordercolor='#e1e1e1',
                        arrowsize=12)
        style.configure('Horizontal.TScrollbar',
                        background='#e1e1e1',
                        troughcolor='#f5f5f5',
                        relief=tk.FLAT,
                        bordercolor='#e1e1e1',
                        arrowsize=12)

        # 状态栏样式
        style.configure('Status.TFrame',
                        background='#e1e1e1',
                        relief=tk.SUNKEN)
        style.configure('Status.TLabel',
                        font=('Segoe UI', 9),
                        background='#e1e1e1',
                        foreground='#555555',
                        padding=3,
                        anchor=tk.W)

        # 对话框样式
        style.configure('Dialog.TFrame',
                        background='#f5f5f5')

        # 标签样式
        self.tree.tag_configure('done', foreground='#888888')
        self.tree.tag_configure('pending', foreground='#333333')

    def _setup_ui(self):
        """设置用户界面"""
        # 主框架
        self.main_frame = ttk.Frame(self.root, style='Dialog.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 顶部工具栏
        self._setup_toolbar()

        # 筛选工具栏
        self._setup_filter_bar()

        # 任务列表
        self._setup_task_list()

        # 状态栏
        self._setup_status_bar()

        # 右键菜单
        self._setup_context_menu()

    def _setup_toolbar(self):
        """设置顶部工具栏"""
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        # 操作按钮
        ttk.Button(
            toolbar, text="➕ 添加任务",
            command=self._show_add_dialog,
            width=12,
            style = 'Toolbutton.TButton'
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            toolbar, text="🔄 刷新",
            command=self._reload_tasks,
            width=8,
            style='Toolbutton.TButton'
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            toolbar, text="🔍 搜索",
            command=self._show_search_dialog,
            width=8,
            style='Toolbutton.TButton'
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            toolbar, text="📊 统计",
            command=self._show_stats,
            width=8,
            style='Toolbutton.TButton'
        ).pack(side=tk.LEFT, padx=2)

        # 右侧按钮
        ttk.Button(
            toolbar, text="⚙️ 设置",
            command=self._show_settings,
            width=8,
            style='Toolbutton.TButton'
        ).pack(side=tk.RIGHT, padx=2)

    def _setup_filter_bar(self):
        """设置筛选工具栏"""
        filter_frame = ttk.Frame(self.main_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        # 分类筛选
        ttk.Label(filter_frame, text="分类:").pack(side=tk.LEFT)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            values=["全部"] + self.manager.get_categories(),
            state="readonly",
            width=15
        )
        self.category_combo.pack(side=tk.LEFT, padx=5)
        self.category_combo.set("全部")
        self.category_combo.bind("<<ComboboxSelected>>", self._apply_filters)

        # 状态筛选
        ttk.Label(filter_frame, text="状态:").pack(side=tk.LEFT, padx=(10, 0))
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.status_var,
            values=["全部", "未完成", "已完成"],
            state="readonly",
            width=10
        )
        self.status_combo.pack(side=tk.LEFT, padx=5)
        self.status_combo.set("全部")
        self.status_combo.bind("<<ComboboxSelected>>", self._apply_filters)

        # 日期筛选
        ttk.Label(filter_frame, text="日期:").pack(side=tk.LEFT, padx=(10, 0))
        self.date_var = tk.StringVar()
        self.date_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.date_var,
            values=["全部", "今天", "本周", "本月"],
            state="readonly",
            width=10
        )
        self.date_combo.pack(side=tk.LEFT, padx=5)
        self.date_combo.set("全部")
        self.date_combo.bind("<<ComboboxSelected>>", self._apply_filters)

    def _setup_task_list(self):
        """设置任务列表"""
        # 容器框架
        list_frame = ttk.Frame(self.main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 树状视图
        self.tree = ttk.Treeview(
            list_frame,
            columns=('id', 'status', 'name', 'date', 'category'),
            show='headings',
            selectmode='extended'
        )

        # 定义列
        columns = [
            ('id', 'ID', 50),
            ('status', '状态', 60),
            ('name', '任务名称', 300),
            ('date', '日期', 100),
            ('category', '分类', 100)
        ]

        for col_id, heading, width in columns:
            self.tree.heading(col_id, text=heading, anchor=tk.W)
            self.tree.column(col_id, width=width, stretch=False)

        # 垂直滚动条
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # 水平滚动条
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=hsb.set)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # 双击编辑
        self.tree.bind("<Double-1>", lambda e: self._edit_selected_task())

        # 样式配置
        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=('Arial', 10))
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        style.map("Treeview",
                  background=[('selected', '#0078d7')],
                  foreground=[('selected', 'white')])

        # 标签样式
        self.tree.tag_configure('done', foreground='gray')
        self.tree.tag_configure('pending', foreground='black')

    def _setup_status_bar(self):
        """设置状态栏"""
        self.status_var = tk.StringVar()
        self.status_var.set("就绪 | 总任务: 0")

        status_bar = ttk.Frame(self.main_frame, height=20, style='Status.TFrame')
        status_bar.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(
            status_bar,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        ).pack(fill=tk.X)

    def _setup_context_menu(self):
        """设置右键菜单"""
        self.context_menu = tk.Menu(self.root, tearoff=0,
                                  bg='white',
                                  fg='#333333',
                                  bd=1,
                                  activebackground='#4a98db',
                                  activeforeground='white',
                                  font=('Segoe UI', 10))
        self.context_menu.add_command(
            label="✅ 标记完成/未完成",
            command=self._toggle_selected_tasks
        )
        self.context_menu.add_command(
            label="✏️ 编辑任务",
            command=self._edit_selected_task
        )
        self.context_menu.add_command(
            label="🗑️ 删除任务",
            command=self._delete_selected_tasks
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="📋 复制任务名称",
            command=self._copy_task_name
        )

        self.tree.bind("<Button-3>", self._show_context_menu)

    def _load_tasks(self):
        """加载任务列表"""
        try:
            # 获取筛选条件
            category = None if self.category_var.get() == "全部" else self.category_var.get()

            # 处理状态筛选
            status = self.status_combo.get()
            # print(status)
            filter_done = None
            if status == "已完成":
                filter_done = True
            elif status == "未完成":
                filter_done = False

            # 处理日期筛选
            date_range = self.date_var.get()
            start_date = None
            end_date = None

            if date_range != "全部":
                today = datetime.date.today()
                if date_range == "今天":
                    start_date = today.strftime("%Y-%m-%d")
                    end_date = start_date
                elif date_range == "本周":
                    start_date = (today - datetime.timedelta(days=today.weekday())).strftime("%Y-%m-%d")
                    end_date = (today + datetime.timedelta(days=6 - today.weekday())).strftime("%Y-%m-%d")
                elif date_range == "本月":
                    start_date = today.replace(day=1).strftime("%Y-%m-%d")
                    next_month = today.replace(day=28) + datetime.timedelta(days=4)
                    end_date = (next_month - datetime.timedelta(days=next_month.day)).strftime("%Y-%m-%d")

            # 获取任务数据
            tasks = self.manager.get_tasks(
                filter_done=filter_done,
                category=category,
                start_date=start_date,
                end_date=end_date
            )

            # 更新UI
            self._update_task_list(tasks)

            # 更新状态栏
            total_tasks = len(tasks)
            done_tasks = sum(1 for t in tasks if t['done'])
            self.status_var.set(
                f"就绪 | 总任务: {total_tasks} | 已完成: {done_tasks} | "
                f"未完成: {total_tasks - done_tasks}"
            )

            # 更新分类下拉框
            current_category = self.category_var.get()
            self.category_combo['values'] = ["全部"] + self.manager.get_categories()
            if current_category in self.category_combo['values']:
                self.category_combo.set(current_category)
            else:
                self.category_combo.set("全部")

        except Exception as e:
            logger.error(f"加载任务失败: {str(e)}")
            messagebox.showerror("错误", f"加载任务失败: {str(e)}")

    def _update_task_list(self, tasks: list[Dict]):
        """更新任务列表显示"""
        self.tree.delete(*self.tree.get_children())

        for task in tasks:
            status = '✅' if task['done'] else '◻️'
            self.tree.insert(
                '', tk.END,
                values=(
                    task['id'],
                    status,
                    task['name'],
                    task['date'],
                    task['category']
                ),
                tags=('done' if task['done'] else 'pending')
            )

    def _apply_filters(self, event=None):
        """应用筛选条件"""
        self._load_tasks()

    def _reload_tasks(self):
        """重新加载任务"""
        self._load_tasks()
        messagebox.showinfo("刷新", "任务列表已刷新")

    def _show_add_dialog(self):
        """显示添加任务对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加新任务")
        dialog.transient(self.root)
        dialog.grab_set()
        self._center_window_on_parent(dialog, 400, 250)

        # 设置对话框样式
        dialog.configure(bg='#f5f5f5')

        # 表单元素
        ttk.Label(dialog, text="任务名称:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.E)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        name_entry.focus_set()

        ttk.Label(dialog, text="任务分类:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)
        category_combo = ttk.Combobox(dialog, values=self.manager.get_categories(), width=28)
        category_combo.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        if self.manager.get_categories():
            category_combo.set(self.manager.get_categories()[0])

        ttk.Label(dialog, text="任务日期:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.E)
        date_entry = DateEntry(dialog, width=27, date_pattern="yyyy-mm-dd")
        date_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

        # 按钮区域
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        def on_add():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("警告", "任务名称不能为空！")
                return

            task = self.manager.add_task(
                name=name,
                category=category_combo.get(),
                date=date_entry.get_date().strftime("%Y-%m-%d")
            )

            if task:
                self._load_tasks()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "添加任务失败！")

        ttk.Button(button_frame, text="添加", command=on_add).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

    def _show_search_dialog(self):
        """显示搜索对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("搜索任务")
        dialog.transient(self.root)
        dialog.grab_set()
        self._center_window_on_parent(dialog, 300, 150)

        ttk.Label(dialog, text="搜索关键词:").pack(pady=(10, 5))
        search_entry = ttk.Entry(dialog, width=30)
        search_entry.pack(pady=5)
        search_entry.focus_set()

        def on_search():
            keyword = search_entry.get().strip()
            if not keyword:
                return

            tasks = self.manager.get_tasks(search_query=keyword)
            self._update_task_list(tasks)
            dialog.destroy()

        ttk.Button(dialog, text="搜索", command=on_search).pack(pady=10)

    def _edit_selected_task(self):
        """编辑选中任务"""
        selected = self._get_selected_task()
        if not selected:
            messagebox.showwarning("警告", "请先选择要编辑的任务！")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("编辑任务")
        dialog.transient(self.root)
        dialog.grab_set()
        self._center_window_on_parent(dialog, 400, 300)

        # 表单元素
        ttk.Label(dialog, text="任务名称:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.E)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        name_entry.insert(0, selected['name'])
        name_entry.focus_set()

        ttk.Label(dialog, text="任务分类:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)
        category_combo = ttk.Combobox(dialog, values=self.manager.get_categories(), width=28)
        category_combo.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        category_combo.set(selected['category'])

        ttk.Label(dialog, text="任务日期:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.E)
        date_entry = DateEntry(dialog, width=27, date_pattern="yyyy-mm-dd")
        date_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        date_entry.set_date(selected['date'])

        # 完成状态
        done_var = tk.BooleanVar(value=selected['done'])
        ttk.Checkbutton(dialog, text="已完成", variable=done_var).grid(row=3, column=1, sticky=tk.W)

        # 按钮区域
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        def on_save():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("警告", "任务名称不能为空！")
                return

            updates = {
                'name': name,
                'category': category_combo.get(),
                'date': date_entry.get_date().strftime("%Y-%m-%d"),
                'done': done_var.get()
            }

            if self.manager.update_task(selected['id'], updates):
                self._load_tasks()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "更新任务失败！")

        ttk.Button(button_frame, text="保存", command=on_save).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

    def _toggle_selected_tasks(self):
        """切换选中任务的完成状态"""
        selected_tasks = self._get_selected_tasks()
        if not selected_tasks:
            return

        for task in selected_tasks:
            success = self.manager.update_task(task['id'], {'done': not task['done']})
            if not success:
                messagebox.showerror("错误", f"更新任务 {task['name']} 失败！")
                break

        self._load_tasks()

    def _delete_selected_tasks(self):
        """删除选中任务"""
        selected_tasks = self._get_selected_tasks()
        if not selected_tasks:
            return

        task_names = "\n".join([f"- {t['name']}" for t in selected_tasks])
        if not messagebox.askyesno(
                "确认删除",
                f"确定要删除以下 {len(selected_tasks)} 个任务吗？\n{task_names}"
        ):
            return

        failed_deletes = []
        for task in selected_tasks:
            if not self.manager.delete_task(task['id']):
                failed_deletes.append(task['name'])

        if failed_deletes:
            messagebox.showerror(
                "错误",
                f"以下任务删除失败:\n{', '.join(failed_deletes)}"
            )
        else:
            messagebox.showinfo("成功", f"已删除 {len(selected_tasks)} 个任务")

        self._load_tasks()

    def _copy_task_name(self):
        """复制选中任务名称到剪贴板"""
        selected = self._get_selected_task()
        if selected:
            self.root.clipboard_clear()
            self.root.clipboard_append(selected['name'])
            messagebox.showinfo("复制成功", "任务名称已复制到剪贴板")

    def _show_stats(self):
        """显示任务统计信息"""
        tasks = self.manager.get_tasks()
        if not tasks:
            messagebox.showinfo("统计", "当前没有任务")
            return

        total = len(tasks)
        done = sum(1 for t in tasks if t['done'])
        pending = total - done

        # 按分类统计
        categories = {}
        for t in tasks:
            if t['category'] not in categories:
                categories[t['category']] = {'total': 0, 'done': 0}
            categories[t['category']]['total'] += 1
            if t['done']:
                categories[t['category']]['done'] += 1

        # 构建统计信息
        stats = [
            f"📊 任务统计",
            f"-------------------------",
            f"总计: {total}",
            f"已完成: {done} ({done / total:.0%})",
            f"未完成: {pending} ({pending / total:.0%})",
            f"\n📂 按分类统计:"
        ]

        for cat, data in categories.items():
            stats.append(
                f"{cat}: {data['done']}/{data['total']} "
                f"({data['done'] / data['total']:.0%})"
            )

        messagebox.showinfo("任务统计", "\n".join(stats))

    def _show_settings(self):
        """显示设置对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("设置")
        dialog.transient(self.root)
        dialog.grab_set()
        self._center_window_on_parent(dialog, 300, 200)

        ttk.Label(dialog, text="存储类型:").pack(pady=(10, 5))

        storage_var = tk.StringVar(value=self.manager.storage_type)
        ttk.Radiobutton(
            dialog, text="SQLite数据库",
            variable=storage_var, value='sqlite'
        ).pack(anchor=tk.W)
        ttk.Radiobutton(
            dialog, text="JSON文件",
            variable=storage_var, value='json'
        ).pack(anchor=tk.W)

        def on_save():
            if storage_var.get() != self.manager.storage_type:
                if messagebox.askyesno(
                        "确认",
                        "更改存储类型需要重启应用，是否继续？"
                ):
                    # 在实际应用中，应该保存设置到配置文件
                    messagebox.showinfo(
                        "提示",
                        "存储类型将在应用重启后生效"
                    )
            dialog.destroy()

        ttk.Button(dialog, text="保存", command=on_save).pack(pady=10)

    def _get_selected_task(self) -> Optional[Dict]:
        """获取当前选中的单个任务"""
        selected = self.tree.selection()
        if not selected:
            return None

        item = selected[0]
        task_id = int(self.tree.item(item, 'values')[0])
        return self.manager.get_task_by_id(task_id)

    def _get_selected_tasks(self) -> list[Dict]:
        """获取当前选中的所有任务"""
        selected_items = self.tree.selection()
        if not selected_items:
            return []

        tasks = []
        for item in selected_items:
            task_id = int(self.tree.item(item, 'values')[0])
            task = self.manager.get_task_by_id(task_id)
            if task:
                tasks.append(task)

        return tasks

    def _show_context_menu(self, event):
        """显示右键菜单"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _center_window(self, width, height):
        """居中显示主窗口"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _center_window_on_parent(self, window, width, height):
        """相对于父窗口居中显示"""
        parent_x = self.root.winfo_x()
        parent_y = self.root.winfo_y()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()

        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2

        window.geometry(f"{width}x{height}+{x}+{y}")
        window.resizable(False, False)


def run():
    """运行应用程序"""
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()


if __name__ == '__main__':
    run()