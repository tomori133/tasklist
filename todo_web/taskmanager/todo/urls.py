from django.urls import path
from .views import (
    TaskListView, TaskDetailView, TaskCreateView,
    TaskUpdateView, TaskDeleteView, toggle_task_status,
    task_stats
)

urlpatterns = [
    # 任务列表
    path('', TaskListView.as_view(), name='task-list'),
    # 任务详情
    path('task/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    # 创建任务
    path('task/new/', TaskCreateView.as_view(), name='task-create'),
    # 更新任务
    path('task/<int:pk>/update/', TaskUpdateView.as_view(), name='task-update'),
    # 删除任务
    path('task/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),
    # 切换任务状态
    path('task/<int:pk>/toggle/', toggle_task_status, name='task-toggle'),
    # 统计信息
    path('stats/', task_stats, name='task-stats'),
]
