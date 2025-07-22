# todo_app/cli/cli.py
import argparse
from .core import TaskManager


class TodoCLI:
    def __init__(self):
        self.manager = TaskManager(storage_type='json')  # 可改为'sqlite'
        self.parser = self._setup_parser()

    def _setup_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description='待办事项管理')
        subparsers = parser.add_subparsers(dest='command')

        # 添加任务
        add_parser = subparsers.add_parser('add', help='添加新任务')
        add_parser.add_argument('name', help='任务名称')
        add_parser.add_argument('-d', '--date', help='任务日期 (YYYY-MM-DD)')
        add_parser.add_argument('-c', '--category', help='任务分类')

        # 列出任务
        list_parser = subparsers.add_parser('list', help='列出任务')
        list_parser.add_argument('--done', action='store_true', help='只显示已完成')
        list_parser.add_argument('--pending', action='store_true', help='只显示未完成')
        list_parser.add_argument('--category', help='按分类筛选')

        return parser

    def run(self):
        args = self.parser.parse_args()

        if args.command == 'add':
            self._handle_add(args)
        elif args.command == 'list':
            self._handle_list(args)
        else:
            self.parser.print_help()

    def _handle_add(self, args):
        task = self.manager.add_task(args.name, args.date, args.category)
        print(f"✓ 已添加任务: {task['name']}")

    def _handle_list(self, args):
        filter_done = None
        if args.done:
            filter_done = True
        elif args.pending:
            filter_done = False

        tasks = self.manager.get_tasks(filter_done, args.category)

        if not tasks:
            print("没有任务")
            return

        for i, task in enumerate(tasks, 1):
            status = '✓' if task['done'] else '◻'
            print(f"{i}. {status} {task['name']} ({task['category']})")


if __name__ == '__main__':
    TodoCLI().run()