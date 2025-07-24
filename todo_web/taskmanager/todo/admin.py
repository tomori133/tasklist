from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'priority', 'done', 'user', 'created_at')
    list_filter = ('done', 'priority', 'user')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
