import re

from django.db import models

USERNAME_ALLOWED_SYMBOLS = r'^[a-zA-Z0-9@.+-_]*$'


class PubDateIdOrder(models.Model):
    """Абстрактная модель.
    Добавляет дату создания и сортирует по полю id."""
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')

    class Meta:
        abstract = True
        ordering = ('-id', )


def check_username(value):
    """Проверка имени пользователя на символы [a-zA-Z0-9@.+-_] и не 'me'"""
    error_name_text = ''
    if value.strip().lower() == 'me':
        error_name_text = 'Имя пользователя "me" запрещено!'
    if not re.match(USERNAME_ALLOWED_SYMBOLS, value):
        error_name_text = ('В имени пользователя'
                           ' использованы запрещенные символы!')
    return error_name_text
