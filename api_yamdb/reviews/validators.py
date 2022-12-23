# reviews/validators.py
import datetime as dt

from django.core import validators

from .utils import check_username


def validate_username(value):
    """Проверяем значение имени пользователя на коректность"""
    error_string = check_username(value)
    if error_string:
        raise ValueError(error_string)


def validate_year(value):
    if value > dt.datetime.now().year:
        raise validators.ValidationError(
            "Год выпуска не может быть больше текущего!")
    return value
