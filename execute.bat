@echo off

:: Install requirements
pip install -r requirements.txt

:: Run migrations and Django servers
python ExamenIngWeb\manage.py migrate
start cmd /k python ExamenIngWeb\manage.py runserver 8000
