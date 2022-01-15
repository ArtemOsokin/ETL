import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Genre(TimeStampedModel):
    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True
    )
    name = models.CharField(_('Наименование'), max_length=255)
    description = models.TextField(_('Описание'), blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Жанр')
        verbose_name_plural = _('Жанры')
        db_table = "content\".\"genre"


class Person(TimeStampedModel):
    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True
    )
    full_name = models.CharField(_('Имя'), max_length=255)
    birth_date = models.DateField(_('Дата рождения'), blank=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = _('Персонаж')
        verbose_name_plural = _('Персонажи')
        db_table = "content\".\"person"


class FilmworkGenre(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True
    )
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        constraints = [
            models.UniqueConstraint(
                fields=['film_work', 'genre'],
                name='unique_film_work_genre'
            ),
        ]


class PersonRoleType(models.TextChoices):
    ACTOR = 'actor', _('Актёр')
    WRITER = 'writer', _('Сценарист')
    DIRECTOR = 'director', _('Режисёр')


class FilmworkPerson(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True
    )
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(
        _('Роль'),
        max_length=20,
        blank=True,
        choices=PersonRoleType.choices
    )

    class Meta:
        db_table = "content\".\"person_film_work"
        constraints = [
            models.UniqueConstraint(
                fields=['person', 'role', 'film_work',],
                name='unique_film_work_person_role'
            ),
        ]


class FilmworkType(models.TextChoices):
    MOVIE = 'movie', _('Фильм')
    TV_SHOW = 'tv_show', _('ТВ шоу')


class Filmwork(TimeStampedModel):
    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True
    )
    title = models.CharField(_('Название'), max_length=255)
    description = models.TextField(_('Описание'), blank=True)
    creation_date = models.DateField(_('Дата создания'), blank=True)
    certificate = models.TextField(_('Сертификат'), blank=True)
    file_path = models.FileField(
        _('Файл'),
        upload_to='film_works/',
        blank=True
    )
    rating = models.FloatField(
        _('Рейтинг'),
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        blank=True
    )
    type = models.CharField(
        _('Тип'),
        max_length=20,
        choices=FilmworkType.choices
    )
    genres = models.ManyToManyField(Genre, through='FilmworkGenre')
    persons = models.ManyToManyField(Person, through='FilmworkPerson')
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Фильм')
        verbose_name_plural = _('Фильмы')
        db_table = "content\".\"film_work"
