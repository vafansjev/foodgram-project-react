___
## Описание:
Проект Foodgram (Продуктовый помощник) - онлайн сервис, которой позволяет создавать базу рецептов, подписываться на других авторов и распечатывать список ингридиентов для покупки своих любимых рецептов.
___
## Стек технологий:
- Python 3.7.8
- Django 2.2
- DjangoRestFramework 3.12
- PostgreSQL
- Docker
___
## Как запустить проект:
**Важно!** Перед запуском проекта требуется установить Docker!
Дистрибутив и документация доступны на официальном сайте - https://www.docker.com/products/docker-desktop

После установки Docker приступить к запуску проекта:

Клонировать репозиторий проекта командой
```
git clone <адрес проекта на GitHub>
```


В директории infra создать файл .env и наполнить содержимым:
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME= # имя базы данных
POSTGRES_USER= # логин для подключения к базе данных
POSTGRES_PASSWORD= # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT= # порт для подключения к БД
SECRET_KEY= #секретный ключ django
```

Не меняя дирректорию выполнить команду:
```
docker-compose up -d
```

В процессе развертывания будут автоматически выполнены команды:
```
python manage.py migrate --noinput
python manage.py collectstatic --no-input
gunicorn api_yamdb.wsgi:application --bind 0:8000
```

Создать суперпользователя (при необходимости):
```
docker-compose exec backend python manage.py createsuperuser
```
Загрузить тестовые данные ингридиенты и тэги (при необходимости):
```
docker-compose exec backend python manage.py load_data
```

В результате будут запущены контейнеры:
- frontend
- backend
- postgres
- nginx
Это обеспечит полноценную работу сервиса по его веб-адресу (при локальном подключении это localhost)

Также доступен полноценный api сервиса, с полным перечнем команд можно ознакомиться в документации:
```
http://localhost/api/docs/redoc.html
```

Для остановки работы проекта выполнить команду:
```
docker-compose down -v
```
___