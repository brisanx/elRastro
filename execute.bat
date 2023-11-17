@echo off

:: Install requirements
pip install -r requirements.txt

:: Run migrations and Django servers
python parcial2\manage.py migrate
start cmd /k python parcial2\manage.py runserver 8000
