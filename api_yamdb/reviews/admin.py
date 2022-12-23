from django.contrib import admin

from .models import Title, Genre, Category, User


class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
    )
    search_fields = ('name', )
    empty_value_display = ('-пусто-')


class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
    )
    search_fields = ('name', )
    empty_value_display = ('-пусто-')


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
    )
    search_fields = ('name', )
    empty_value_display = ('-пусто-')


admin.site.register(Title, TitleAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User)
