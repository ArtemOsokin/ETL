def get_update_filmwork(up_state: str):
    SQL = f"""
    SELECT id, updated_at
    FROM film_work
    WHERE updated_at > '{up_state}'
    ORDER BY updated_at DESC ; 
    """
    return SQL

def get_update_person_filmwork_idx(up_state: str):
    SQL = f"""
    SELECT fw.id, fw.updated_at
    FROM film_work fw
    LEFT JOIN person_film_work pfw ON pfw.film_work_id = fw.id
    WHERE pfw.person_id IN (
        SELECT id
        FROM person
        WHERE updated_at > '{up_state}'
    )
    ORDER BY fw.updated_at DESC ;
    """
    return SQL

def get_update_genre_filmwork_idx(up_state: str):
    SQL = f"""
    SELECT fw.id, fw.updated_at
    FROM film_work fw
    LEFT JOIN genre_film_work gfw ON gfw.film_work_id = fw.id
    WHERE gfw.genre_id IN (
        SELECT id
        FROM genre
        WHERE updated_at > '{up_state}'
    )
    ORDER BY fw.updated_at DESC;
    """
    return SQL

def get_update_film_work_person_genre_by_idx(up_state: str):
    SQL = f"""
    SELECT fw.id
    FROM film_work fw
    LEFT JOIN genre_film_work gfw ON gfw.film_work_id = fw.id
    LEFT JOIN person_film_work pfw ON pfw.film_work_id = fw.id
    WHERE (gfw.genre_id IN (
        SELECT id
        FROM genre
        WHERE updated_at > '{up_state}')) AND (pfw.person_id IN (
        SELECT id
        FROM person
        WHERE updated_at > '{up_state}')) AND (fw.id IN (
        SELECT id
        FROM film_work
        WHERE updated_at > '{up_state}'))
    GROUP BY fw.id 
    ORDER BY fw.updated_at DESC;
    """
    return SQL

def get_update_film_work_by_idx(idx: str):
    SQL = f"""
    SELECT
    fw.id AS fw_id, 
    fw.title, 
    fw.description, 
    fw.rating, 
    fw.type, 
    fw.created_at, 
    fw.updated_at, 
    ARRAY_AGG(DISTINCT jsonb_build_object('id', g.id, 'name', g.name)) AS genres,
    ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) FILTER (WHERE pfw.role = 'director') AS directors,
    ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) FILTER (WHERE pfw.role = 'actor') AS actors,
    ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) FILTER (WHERE pfw.role = 'writer') AS writers
    FROM film_work fw
    LEFT JOIN genre_film_work AS gfw ON fw.id = gfw.film_work_id
    LEFT JOIN genre AS g ON gfw.genre_id = g.id
    LEFT JOIN person_film_work AS pfw ON fw.id = pfw.film_work_id
    LEFT JOIN person AS p ON pfw.person_id = p.id
    WHERE fw.id IN ({idx})
    GROUP BY fw_id
    ORDER BY fw.updated_at DESC;
    """
    return SQL