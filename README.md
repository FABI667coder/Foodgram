Cайт Foodgram, «Продуктовый помощник».

## Проект доступен по: [ССЫЛКЕ](http://foodgramdipproject.ddns.net/recipes)

На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд..
### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:FABI667coder/foodgram-project-react.git
```

```
cd foodgram-project-react/infra
создать файл .env 
```

с данными переменнами 
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт
```


Чтобы развернуть проект выполните команду:

```
docker-compose up -d
```
Затем следует сделать миграции и собрать статику.
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --no-input
```
Остановка проекта осуществляется командой.
```
docker-compose stop


```
Доступ к админке -> login: admin@admin.ru password: admin
```

## Развёрнутый проект на сервере доступен по ссылке:
http://localhost:8000/recipes
