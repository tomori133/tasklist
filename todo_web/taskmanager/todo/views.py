from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .models import Task
from .forms import TaskForm


# 任务列表视图
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'todo/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        # 只显示当前用户的任务
        return Task.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 添加统计数据
        context['total_tasks'] = self.get_queryset().count()
        context['completed_tasks'] = self.get_queryset().filter(done=True).count()
        context['pending_tasks'] = self.get_queryset().filter(done=False).count()
        return context


# 任务详情视图
class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'todo/task_detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


# 创建任务视图
class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'todo/task_form.html'
    success_url = reverse_lazy('task-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


# 更新任务视图
class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'todo/task_form.html'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('task-detail', kwargs={'pk': self.object.pk})


# 删除任务视图
class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'todo/task_confirm_delete.html'
    success_url = reverse_lazy('task-list')

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


# 切换任务完成状态
@login_required
def toggle_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.done = not task.done
    task.save()
    return redirect('task-detail', pk=pk)


# 统计信息视图
@login_required
def task_stats(request):
    # 获取当前用户的所有任务
    tasks = Task.objects.filter(user=request.user)

    # 基本统计
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(done=True).count()
    pending_tasks = total_tasks - completed_tasks
    completion_rate = round((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    # 计算环形图角度（360度的百分比）
    completion_angle = completion_rate * 3.6  # 这里预先计算好角度

    # 优先级分布
    priority_counts = tasks.values('priority').annotate(count=Count('id')).order_by('priority')
    priority_data = {
        'High': 0,
        'Medium': 0,
        'Low': 0
    }
    for item in priority_counts:
        priority_data[item['priority']] = item['count']

    # 计算百分比
    priority_percentages = {}
    for priority, count in priority_data.items():
        priority_percentages[priority] = round((count / total_tasks) * 100) if total_tasks > 0 else 0

    # 最近任务
    recent_tasks = tasks.order_by('-created_at')[:5]

    # 周变化统计
    one_week_ago = timezone.now() - timedelta(days=7)
    last_week_tasks = tasks.filter(created_at__lte=one_week_ago)
    last_week_completed = last_week_tasks.filter(done=True).count()

    weekly_change = {
        'total_tasks': total_tasks - last_week_tasks.count(),
        'completed_tasks': completed_tasks - last_week_completed,
        'pending_tasks': pending_tasks - (last_week_tasks.count() - last_week_completed),
        'completion_rate': completion_rate - (
            round((last_week_completed / last_week_tasks.count()) * 100) if last_week_tasks.count() > 0 else 0)
    }

    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'completion_rate': completion_rate,
        'completion_angle': completion_angle,  # 将计算好的角度添加到上下文
        'priority_counts': priority_data,
        'priority_percentages': priority_percentages,
        'recent_tasks': recent_tasks,
        'weekly_change': weekly_change
    }

    return render(request, 'todo/task_stats.html', context)
