from __future__ import annotations

from typing import Any, Optional

from detector.debug_manager import debug_manager

from .db import create_database_connection

# SQL-urile pentru operatiile pe tabela users
CREATE_USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    nume VARCHAR(100) NOT NULL,
    prenume VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    numar_inmatriculare VARCHAR(20) NOT NULL UNIQUE,
    qr_path TEXT
)
"""

# SQL pentru selectarea unui user dupa un camp specific (email sau numar_inmatriculare)
USERS_SELECT_SQL = """
SELECT id, nume, prenume, email, password_hash, numar_inmatriculare, qr_path
FROM users
WHERE {field} = %s
"""

# SQL pentru selectarea unui user dupa id
USERS_SELECT_BY_ID_SQL = """
SELECT id, nume, prenume, email, password_hash, numar_inmatriculare, qr_path
FROM users
WHERE id = %s
"""


def ensure_users_table_exists() -> None:
    # Verificare daca tabela users exista, altfel o creeaza
    connection = create_database_connection()
    if not connection:
        raise RuntimeError("Nu s-a putut initializa tabela users")

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(CREATE_USERS_TABLE_SQL)
        connection.commit()
    except Exception as exc:
        connection.rollback()
        debug_manager.log(f"Eroare la crearea tabelului users: {exc}")
        raise
    finally:
        if cursor:
            cursor.close()
        connection.close()


def fetch_user_by_email(email: str) -> Optional[tuple[Any, ...]]:
    # Cauta un user dupa email
    connection = create_database_connection()
    if not connection:
        return None

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(USERS_SELECT_SQL.format(field="email"), (email,))
        return cursor.fetchone()
    except Exception as exc:
        debug_manager.log(f"Eroare la cautarea userului dupa email: {exc}")
        return None
    finally:
        if cursor:
            cursor.close()
        connection.close()


def fetch_user_by_id(user_id: int) -> Optional[tuple[Any, ...]]:
    # Cauta un user dupa id
    connection = create_database_connection()
    if not connection:
        return None

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(USERS_SELECT_BY_ID_SQL, (user_id,))
        return cursor.fetchone()
    except Exception as exc:
        debug_manager.log(f"Eroare la cautarea userului dupa id: {exc}")
        return None
    finally:
        if cursor:
            cursor.close()
        connection.close()


def fetch_user_by_plate(numar_inmatriculare: str) -> Optional[tuple[Any, ...]]:
    # Cauta un user dupa numar inmatriculare
    connection = create_database_connection()
    if not connection:
        return None

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(USERS_SELECT_SQL.format(field="numar_inmatriculare"), (numar_inmatriculare,))
        return cursor.fetchone()
    except Exception as exc:
        debug_manager.log(f"Eroare la cautarea userului dupa numar inmatriculare: {exc}")
        return None
    finally:
        if cursor:
            cursor.close()
        connection.close()


def insert_user(nume: str, prenume: str, email: str, password_hash: str, numar_inmatriculare: str) -> int:
    # Insereaza un nou user in baza de date si returneaza id-ul generat
    connection = create_database_connection()
    if not connection:
        raise RuntimeError("Nu s-a putut conecta la baza de date")

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO users (nume, prenume, email, password_hash, numar_inmatriculare, qr_path)
            VALUES (%s, %s, %s, %s, %s, NULL)
            RETURNING id
            """,
            (nume, prenume, email, password_hash, numar_inmatriculare),
        )
        user_id = cursor.fetchone()[0]
        connection.commit()
        return user_id
    except Exception as exc:
        connection.rollback()
        debug_manager.log(f"Eroare la inserarea userului: {exc}")
        raise
    finally:
        if cursor:
            cursor.close()
        connection.close()


def update_user(user_id: int, values: dict[str, Any]) -> None:
    # Actualizeaza un user cu valorile specificate in dict-ul values
    if not values:
        return

    connection = create_database_connection()
    if not connection:
        raise RuntimeError("Nu s-a putut conecta la baza de date")

    cursor = None
    try:
        cursor = connection.cursor()
        columns = []
        params = []
        for column, value in values.items():
            columns.append(f"{column} = %s")
            params.append(value)

        params.append(user_id)
        sql = f"UPDATE users SET {', '.join(columns)} WHERE id = %s"
        cursor.execute(sql, tuple(params))
        connection.commit()
    except Exception as exc:
        connection.rollback()
        debug_manager.log(f"Eroare la actualizarea userului: {exc}")
        raise
    finally:
        if cursor:
            cursor.close()
        connection.close()

def update_user_qr_path(user_id: int, qr_path: str) -> None:
    # Actualizeaza calea QR-ului pentru userul specificat
    update_user(user_id, {"qr_path": qr_path})
