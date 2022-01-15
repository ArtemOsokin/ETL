from django.contrib import admin

from .models import Filmwork, FilmworkGenre, FilmworkPerson, Genre, Person


class PersonRoleInline(admin.TabularInline):
    model = FilmworkPerson
    extra = 0


class GenreInline(admin.TabularInline):
    model = FilmworkGenre
    extra = 0


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    # отображение полей в списке
    list_display = ('title', 'type', 'creation_date', 'rating',)

    # фильтрация в списке
    list_filter = ('type',)

    # поиск по полям
    search_fields = ('title', 'description', 'id',)

    # порядок следования полей в форме создания/редактирования
    fields = (
        'title', 'type', 'description', 'creation_date', 'certificate',
        'file_path', 'rating',
    )

    inlines = [
        PersonRoleInline,
        GenreInline
    ]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    # отображение полей в списке
    list_display = ('name', 'description',)

    # поиск по полям
    search_fields = ('name', 'description', 'id',)

    # порядок следования полей в форме создания/редактирования
    fields = (
        'name', 'description',
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    # отображение полей в списке
    list_display = ('full_name', 'birth_date',)

    # поиск по полям
    search_fields = ('full_name', 'id',)

    # порядок следования полей в форме создания/редактирования
    fields = (
        'full_name', 'birth_date',
    )
