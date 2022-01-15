-- Подключение к базе данных
\c movies_database;

-- Создание отдельной схемы для контента
CREATE SCHEMA IF NOT EXISTS content;

-- Таблица с кинопроизведениями
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    certificate TEXT,
    file_path TEXT,
    rating FLOAT,
    type TEXT NOT NULL,
    created_at timestamptz,
    updated_at timestamptz
);

-- Жанры кинопроизведений:
CREATE TABLE IF NOT EXISTS content.genre(
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at timestamptz,
    updated_at timestamptz
);

-- Связующая таблица  фильмов и жанров фильма
CREATE TABLE IF NOT EXISTS content.genre_film_work(
    id uuid PRIMARY KEY,
    film_work_id uuid REFERENCES content.film_work(id) ,
    genre_id uuid REFERENCES content.genre(id),
    created_at timestamptz,
    UNIQUE (film_work_id, genre_id)
);

-- Таблица содержащая ФИО и дату рождения людей работающих над фильмом
CREATE TABLE IF NOT EXISTS content.person(
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    birth_date DATE,
    created_at timestamptz,
    updated_at timestamptz
);

-- Связующая таблица  фильмов и людей с описанием роли
CREATE TABLE IF NOT EXISTS content.person_film_work(
    id uuid PRIMARY KEY,
    film_work_id uuid REFERENCES content.film_work(id),
    person_id uuid REFERENCES content.person(id),
    role TEXT NOT NULL,
    created_at timestamptz,
    UNIQUE (film_work_id, person_id, role)
);

-- Создание индекса жанром фильмов по столбцам ИД фильма и ИД жанра
CREATE UNIQUE INDEX IF NOT EXISTS film_work_genre ON content.genre_film_work(
    film_work_id,
    genre_id
);

-- Создание индекса людей работающих над фильмом по столбцам ИД фильма, ИД человека и его роли
CREATE UNIQUE INDEX IF NOT EXISTS film_work_person_role ON content.person_film_work(
    film_work_id,
    person_id,
    role
);
