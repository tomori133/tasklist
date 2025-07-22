# todo_app/cli/core.py
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(self, storage_type: str = 'sqlite'):
        """初始化任务管理器

        Args:
            storage_type: 存储类型 ('json' 或 'sqlite')
        """
        self.storage_type = storage_type
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.data_dir.mkdir(exist_ok=True)

        if storage_type == 'sqlite':
            self.conn = sqlite3.connect(self.data_dir / 'taskstest.db')
            self._init_db()
        else:
            self.json_path = self.data_dir / 'taskstest.json'

    def _init_db(self):
        """初始化数据库表结构"""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    done INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 创建索引提高查询性能
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON tasks(category)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_done ON tasks(done)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON tasks(date)")

    def add_task(self, name: str, date: Optional[str] = None, category: Optional[str] = None) -> Optional[Dict]:
        """添加新任务

        Args:
            name: 任务名称
            date: 任务日期 (YYYY-MM-DD)
            category: 任务分类

        Returns:
            添加的任务字典 (包含生成的ID)，失败返回None
        """
        if not name or not name.strip():
            logger.warning("任务名称不能为空")
            return None

        task_date = date or datetime.now().strftime('%Y-%m-%d')
        task_category = category or '未分类'

        try:
            if self.storage_type == 'sqlite':
                with self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute(
                        """INSERT INTO tasks (name, date, category) 
                        VALUES (?, ?, ?) RETURNING id, name, date, category, done""",
                        (name.strip(), task_date, task_category))
                    result = cursor.fetchone()
                    return {
                        'id': result[0],
                        'name': result[1],
                        'date': result[2],
                        'category': result[3],
                        'done': bool(result[4])
                    }
            else:
                tasks = self._load_json()
                new_id = max([t.get('id', 0) for t in tasks] or [0]) + 1
                task = {
                    'id': new_id,
                    'name': name.strip(),
                    'date': task_date,
                    'category': task_category,
                    'done': False,
                    'created_at': datetime.now().isoformat()
                }
                tasks.append(task)
                self._save_json(tasks)
                return task
        except Exception as e:
            logger.error(f"添加任务失败: {str(e)}")
            return None

    def get_tasks(
            self,
            filter_done: Optional[bool] = None,
            category: Optional[str] = None,
            search_query: Optional[str] = None,
            limit: Optional[int] = None,
            offset: Optional[int] = None
    ) -> List[Dict]:
        """获取任务列表

        Args:
            filter_done: 是否筛选完成状态 (True/False/None)
            category: 按分类筛选
            search_query: 搜索关键词
            limit: 分页大小
            offset: 分页偏移量

        Returns:
            任务字典列表
        """
        try:
            if self.storage_type == 'sqlite':
                query = """SELECT id, name, date, category, done 
                          FROM tasks WHERE 1=1"""
                params = []

                if filter_done is not None:
                    query += " AND done = ?"
                    params.append(int(filter_done))

                if category:
                    query += " AND category = ?"
                    params.append(category)

                if search_query:
                    query += " AND name LIKE ?"
                    params.append(f"%{search_query}%")

                query += " ORDER BY date ASC, created_at ASC"

                if limit is not None:
                    query += " LIMIT ?"
                    params.append(limit)
                    if offset is not None:
                        query += " OFFSET ?"
                        params.append(offset)

                with self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute(query, params)
                    return [{
                        'id': row[0],
                        'name': row[1],
                        'date': row[2],
                        'category': row[3],
                        'done': bool(row[4])
                    } for row in cursor.fetchall()]
            else:
                tasks = self._load_json()

                # 应用筛选条件
                if filter_done is not None:
                    tasks = [t for t in tasks if t['done'] == filter_done]
                if category:
                    tasks = [t for t in tasks if t['category'] == category]
                if search_query:
                    search_lower = search_query.lower()
                    tasks = [t for t in tasks if search_lower in t['name'].lower()]

                # 排序
                tasks.sort(key=lambda x: (x['date'], x.get('created_at', '')))

                # 分页
                if limit is not None:
                    start = offset or 0
                    tasks = tasks[start:start + limit]

                return tasks
        except Exception as e:
            logger.error(f"获取任务列表失败: {str(e)}")
            return []

    def get_task_by_id(self, task_id: int) -> Optional[Dict]:
        """根据ID获取单个任务

        Args:
            task_id: 任务ID

        Returns:
            任务字典，找不到返回None
        """
        try:
            if self.storage_type == 'sqlite':
                with self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute(
                        """SELECT id, name, date, category, done 
                        FROM tasks WHERE id = ?""",
                        (task_id,)
                    )
                    result = cursor.fetchone()
                    if result:
                        return {
                            'id': result[0],
                            'name': result[1],
                            'date': result[2],
                            'category': result[3],
                            'done': bool(result[4])
                        }
            else:
                tasks = self._load_json()
                for task in tasks:
                    if task.get('id') == task_id:
                        return task
            return None
        except Exception as e:
            logger.error(f"获取任务失败: {str(e)}")
            return None

    def update_task(self, task_id: int, updates: Dict) -> bool:
        """更新任务

        Args:
            task_id: 要更新的任务ID
            updates: 更新字段字典 (可包含 name/date/category/done)

        Returns:
            是否更新成功
        """
        try:
            if self.storage_type == 'sqlite':
                set_clause = []
                params = []

                if 'name' in updates:
                    set_clause.append("name = ?")
                    params.append(updates['name'].strip())

                if 'date' in updates:
                    set_clause.append("date = ?")
                    params.append(updates['date'])

                if 'category' in updates:
                    set_clause.append("category = ?")
                    params.append(updates['category'])

                if 'done' in updates:
                    set_clause.append("done = ?")
                    params.append(int(updates['done']))

                if not set_clause:
                    return False

                set_clause.append("updated_at = CURRENT_TIMESTAMP")
                params.append(task_id)

                with self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute(
                        f"UPDATE tasks SET {', '.join(set_clause)} WHERE id = ?",
                        params
                    )
                    return cursor.rowcount > 0
            else:
                tasks = self._load_json()
                updated = False

                for task in tasks:
                    if task.get('id') == task_id:
                        if 'name' in updates:
                            task['name'] = updates['name'].strip()
                        if 'date' in updates:
                            task['date'] = updates['date']
                        if 'category' in updates:
                            task['category'] = updates['category']
                        if 'done' in updates:
                            task['done'] = updates['done']
                        task['updated_at'] = datetime.now().isoformat()
                        updated = True
                        break

                if updated:
                    self._save_json(tasks)
                    return True
                return False
        except Exception as e:
            logger.error(f"更新任务失败: {str(e)}")
            return False

    def delete_task(self, task_id: int) -> bool:
        """删除任务

        Args:
            task_id: 要删除的任务ID

        Returns:
            是否删除成功
        """
        try:
            if self.storage_type == 'sqlite':
                with self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                    return cursor.rowcount > 0
            else:
                tasks = self._load_json()
                original_count = len(tasks)
                tasks = [t for t in tasks if t.get('id') != task_id]

                if len(tasks) < original_count:
                    self._save_json(tasks)
                    return True
                return False
        except Exception as e:
            logger.error(f"删除任务失败: {str(e)}")
            return False

    def get_categories(self) -> List[str]:
        """获取所有分类列表

        Returns:
            分类字符串列表
        """
        try:
            if self.storage_type == 'sqlite':
                with self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT DISTINCT category FROM tasks ORDER BY category")
                    return [row[0] for row in cursor.fetchall()]
            else:
                tasks = self._load_json()
                categories = {t['category'] for t in tasks}
                return sorted(categories)
        except Exception as e:
            logger.error(f"获取分类列表失败: {str(e)}")
            return []

    def _load_json(self) -> List[Dict]:
        """从JSON文件加载任务 (内部方法)"""
        try:
            if self.json_path.exists():
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"加载JSON数据失败: {str(e)}")
            return []

    def _save_json(self, tasks: List[Dict]):
        """保存任务到JSON文件 (内部方法)"""
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存JSON数据失败: {str(e)}")

    def __del__(self):
        """析构函数，确保数据库连接关闭"""
        if hasattr(self, 'conn'):
            self.conn.close()