from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('High', '高'),
        ('Medium', '中'),
        ('Low', '低'),
    ]

    name = models.CharField(max_length=200, verbose_name="任务名称")
    description = models.TextField(blank=True, null=True, verbose_name="任务描述")
    date = models.DateField(verbose_name="截止日期")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium', verbose_name="优先级")
    done = models.BooleanField(default=False, verbose_name="是否完成")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', verbose_name="用户")

    class Meta:
        verbose_name = "任务"
        verbose_name_plural = "任务"
        ordering = ['-created_at']

    def __str__(self):
        return self.name
