# 简易任务清单
# 环境安装
创建虚拟环境
```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
安装Django
```
pip install django
```
创建项目
```
django-admin startproject taskmanager
cd taskmanager
```
创建应用
```
python manage.py startapp todo
```
创建迁移文件
```
python manage.py makemigrations
```
应用迁移
```
python manage.py migrate
```
创建超级用户（管理员）
```
python manage.py createsuperuser
```
运行开发服务器
```
python manage.py runserver
```
## gui版本
![image](https://github.com/tomori133/tasklist/blob/master/images/img.png)
## web版本
![image](https://github.com/tomori133/tasklist/blob/master/images/img_1.png)

