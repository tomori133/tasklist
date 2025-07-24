from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'date', 'priority', 'done']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'done': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': '任务标题',
            'description': '任务描述',
            'date': '截止日期',
            'priority': '优先级',
            'done': '是否完成',
        }

# 自定义登录表单以添加CSS类
class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '请输入用户名'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': '请输入密码'}))
