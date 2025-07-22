def load_tasks():
    """从文件加载任务列表"""
    try:
        with open("tasks.txt", "r") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []


def save_tasks(tasks):
    """保存任务列表到文件"""
    with open("tasks.txt", "w") as f:
        f.write("\n".join(tasks))


def show_tasks(tasks):
    """显示所有任务"""
    if not tasks:
        print("当前没有任务！")
    else:
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task}")


def add_task(tasks):
    """添加新任务"""
    task = input("请输入任务：")
    tasks.append(task)
    print(f'任务 "{task}" 已添加！')


def delete_task(tasks):
    """删除任务"""
    show_tasks(tasks)
    try:
        idx = int(input("请输入要删除的任务序号：")) - 1
        if 0 <= idx < len(tasks):
            removed_task = tasks.pop(idx)
            print(f'任务 "{removed_task}" 已删除！')
        else:
            print("无效的序号！")
    except ValueError:
        print("请输入数字！")


def main():
    tasks = load_tasks()
    while True:
        print("\n=== 待办事项清单 ===")
        print("1. 查看任务")
        print("2. 添加任务")
        print("3. 删除任务")
        print("4. 退出")
        choice = input("请选择操作：")

        if choice == "1":
            show_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
        elif choice == "3":
            delete_task(tasks)
        elif choice == "4":
            save_tasks(tasks)
            print("任务已保存，再见！")
            break
        else:
            print("无效选项，请重新输入！")


if __name__ == "__main__":
    main()