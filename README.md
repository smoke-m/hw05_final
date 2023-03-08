# backend_community_homework

[![CI](https://github.com/yandex-praktikum/hw02_community/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw02_community/actions/workflows/python-app.yml)

# yatube_project
Социальная сеть блогеров
### Описание
Благодаря этому проекту можно будет находить друзей из разных городов.
### Технологии
Python 3.9
Django 2.2.19
### Запуск проекта в dev-режиме
- Установите и активируйте виртуальное окружение
```
python -m venv venv
source venv/Scripts/activate
source venv/bin/activate

- Установите зависимости из файла requirements.txt
```
python -m pip install --upgrade pip
pip install -r requirements.txt
``` 
- В папке с файлом manage.py выполните команду:
```
python manage.py runserver
python manage.py shell
python manage.py startapp users
python manage.py test
# Запустит только тесты из файла test_urls.py в приложении posts в папке tests
python manage.py test posts.tests.test_urls
```
- Запустите команду создания скрипта миграций:
```
python manage.py makemigrations
```
- Нужно запустить все миграции. Выполните команду:
```
python manage.py migrate
```
- Команды тестов
```
coverage run --source='posts,users' manage.py test -v 2
coverage report
coverage html
python manage.py test
```
### Автор
puzzzo