# api_yamdb
## Реализация API на базе Django REST Framework

Позволяет работать с моделями базы:
- User (пользователи)
- Genre (жанр)
- Category (категория)
- Title (название произведения)
- Rewiev (комментарий)

## Технологии в проекте
- Django, DRF, Docker, PostrgeSQL


## Шаблон наполнения файла .env:
Создайте файл .env в папке infra/.env и заполните по шаблону с
указанием своего секретного ключа и пароля к БД:
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=secret # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
SECRET_KEY = 'secretkey' # секретный ключ (установите свой)
```
## Команды для установки и запуска проекта в контейнерах
Чтобы развернуть проект нужно зайти в корневую папку проекта запустить
коммандой:
```
    docker-compose up -d --build
```
Для управления используйте команды (остановить/запустить/удалить):
```
docker-compose stop
docker-compose start
docker-compose down -v
```
## Сделать миграции
```
docker-compose exec web python manage.py migrate
```
## При необходимости создать Суперюзера
```
docker-compose exec web python manage.py createsuperuser
```
## Команда для заполнения базы данными
Для заполнения базы данными используйте команду:
```
docker-compose exec web python manage.py loaddata fixtures.json
```

Приложение будет работать на localhost (http://127.0.0.1/) по адресам:
http://localhost/admin/ - администрирвоание моделей
http://localhost/api/v1/ - API интерфейс


## Подробная документация
```
http://localhost/redoc/
```
## Примеры запросов к API
Регистрация нового пользователя. необходимо отправить отправить POST-запрос в JSON-формате:
```
{
"email": "string",
"username": "string"
}
```
на эндпоинт
```
http://127.0.0.1/api/v1/auth/signup/
```
Для получения JWT-токена необходимо отправить POST-запрос в JSON-формате
(где confirmation_code - буквенно-цифровая последовательность, пришедшая на
указанный до этого email):
```
{
  "username": "string",
  "confirmation_code": "string"
}
```
на эндпоинт:
```
http://127.0.0.1/api/v1/auth/token/
```
в ответе на запрос приходит token (jwt-token).
Все небезопасные запросы делаются с его использованием.
Примеры запросов приведены в подробной документации
```
http://127.0.0.1/redoc/
```

Для неавторизованных пользователей все записи достпупны только для чтения. Получение списка всех категорий - GET-запрос на эндпоинт: 
```
http://127.0.0.1/api/v1/categories/
```
Получение списка жанров:
```
http://127.0.0.1/api/v1/genres/
```
Получение списка произведений
```
http://127.0.0.1/api/v1/titles/
```
Получение одного произведения, titles_id - номер произведения:
```
http://127.0.0.1/api/v1/titles/{titles_id}/
```
Получение списка всех отзывов по произведенияю titles_id:
```
http://127.0.0.1/api/v1/titles/{title_id}/reviews/
```
Получение одного отзыва по произведению titles_id, номмер отзыва
review_id:
```
http://127.0.0.1/api/v1/titles/{title_id}/reviews/{review_id}/
```
### Автор проекта
Сергей Самойлов, 2022.
