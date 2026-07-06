import os

import glob

import psycopg2

from api.database import DB_CONFIG
from detector.debug_manager import debug_manager

DB_CONNECTION_ERROR = "Nu s-a putut conecta la baza de date"


def _remove_qr_file(numar_inmatriculare: str) -> None:
    # Sterge QR-ul din folderele users si visitors, daca exista
    base_folder = os.path.join(os.path.dirname(__file__), '..', '..', 'qrcodes')
    for subfolder in ('users', 'visitors'):
        pattern = os.path.join(base_folder, subfolder, f"qr_{numar_inmatriculare}*.png")
        for qr_file in glob.glob(pattern):
            try:
                os.remove(qr_file)
            except Exception:
                pass


def create_database_connection():
    # Creeaza o conexiune la baza de date PostgreSQL
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        debug_manager.log(f"Eroare la conectarea la baza de date: {e}")
        return None


def create_tables():
    # Creeaza tabelele in baza de date
    conn = create_database_connection()
    if not conn:
        return False

    cursor = None
    try:
        cursor = conn.cursor()
        # Tabelul abonamente
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS subscriptions (
                id SERIAL PRIMARY KEY,
                nume VARCHAR(100) NOT NULL UNIQUE,
                price DECIMAL(10,2) NOT NULL,
                duration INTEGER NOT NULL
            )
            """
        )

        # Tabelul abonamentelor utilizatorilor
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_subscriptions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP NOT NULL,
                plan_id INTEGER NOT NULL,
                active BOOLEAN NOT NULL DEFAULT TRUE,
                CONSTRAINT fk_user_subscriptions_user
                    FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                    CONSTRAINT fk_user_subscriptions_plan
                    FOREIGN KEY (plan_id)
                    REFERENCES subscriptions(id)
                    ON DELETE CASCADE
            )
            """
        )
        
        # Tabelul masini
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS masini (
                numar_inmatriculare VARCHAR(20) PRIMARY KEY,
                cod VARCHAR(20) UNIQUE,
                ora_intrare TIMESTAMP NOT NULL,
                ora_platire TIMESTAMP,
                status VARCHAR(20) NOT NULL DEFAULT 'Vizitator'
            )
            """
        )

        # Tabelul taxe
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS taxe (
                id SERIAL PRIMARY KEY,
                durata INTEGER NOT NULL,
                pret DECIMAL(10,2) NOT NULL
            )
            """
        )

        conn.commit()
        debug_manager.log("Tabelele au fost create cu succes!")
        return True
    except Exception as e:
        debug_manager.log(f"Eroare la crearea tabelelor: {e}")
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    create_tables()
