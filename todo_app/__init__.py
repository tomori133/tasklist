# todo_app/__init__.py
from pathlib import Path
from importlib.metadata import version

__version__ = "0.1.0"

def get_data_dir() -> Path:
    """返回数据存储目录"""
    return Path(__file__).parent / 'data'