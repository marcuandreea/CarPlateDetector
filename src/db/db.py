import os

import psycopg2
from datetime import datetime, timedelta
import random
import string

from api.database import DB_CONFIG
from detector.debug_manager import debug_manager

DB_CONNECTION_ERROR = "Nu s-a putut conecta la baza de date"


def _remove_qr_file(numar_inmatriculare: str) -> None:
    # Sterge QR-ul din folderele users si visitors, daca exista
    base_folder = os.path.join(os.path.dirname(__file__), '..', '..', 'qrcodes')
    for subfolder in ('users', 'visitors'):
        qr_filename = os.path.join(base_folder, subfolder, f"qr_{numar_inmatriculare}.png")
        if os.path.exists(qr_filename):
            os.remove(qr_filename)

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

        # Tabelele abonamente noi
        cursor.execute(CREATE_SUBSCRIPTIONS_TABLE_SQL)
        cursor.execute(CREATE_USER_SUBSCRIPTIONS_TABLE_SQL)

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


def fetch_subscription_plans() -> list[tuple[int, str, float, int]]:
    # Returneaza planurile de abonament disponibile
    conn = create_database_connection()
    if not conn:
        return []

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, nume, price, duration
            FROM subscriptions
            ORDER BY id
            """
        )
        return cursor.fetchall()
    except Exception as exc:
        debug_manager.log(f"Eroare la citirea planurilor de abonament: {exc}")
        return []
    finally:
        if cursor:
            cursor.close()
        conn.close()


def create_subscription_plan(nume: str, price: float, duration: int) -> int:
    # Creeaza un plan nou de abonament
    conn = create_database_connection()
    if not conn:
        raise RuntimeError(DB_CONNECTION_ERROR)

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO subscriptions (nume, price, duration)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (nume, price, duration),
        )
        plan_id = cursor.fetchone()[0]
        conn.commit()
        return int(plan_id)
    except Exception as exc:
        conn.rollback()
        debug_manager.log(f"Eroare la crearea planului de abonament: {exc}")
        raise
    finally:
        if cursor:
            cursor.close()
        conn.close()


def update_subscription_plan(plan_id: int, nume: str, price: float, duration: int) -> bool:
    # Actualizeaza un plan de abonament
    conn = create_database_connection()
    if not conn:
        return False

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE subscriptions
            SET nume = %s, price = %s, duration = %s
            WHERE id = %s
            """,
            (nume, price, duration, plan_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as exc:
        conn.rollback()
        debug_manager.log(f"Eroare la update_subscription_plan: {exc}")
        return False
    finally:
        if cursor:
            cursor.close()
        conn.close()


def delete_subscription_plan(plan_id: int) -> bool:
    # Sterge un plan de abonament
    conn = create_database_connection()
    if not conn:
        return False

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subscriptions WHERE id = %s", (plan_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as exc:
        conn.rollback()
        debug_manager.log(f"Eroare la delete_subscription_plan: {exc}")
        return False
    finally:
        if cursor:
            cursor.close()
        conn.close()


def fetch_user_subscriptions() -> list[tuple]:
    # Returneaza abonamentele utilizatorilor
    conn = create_database_connection()
    if not conn:
        return []

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, start_date, end_date, plan_id, active
            FROM user_subscriptions
            ORDER BY start_date DESC, id DESC
            """
        )
        return cursor.fetchall()
    except Exception as exc:
        debug_manager.log(f"Eroare la citirea abonamentelor utilizatorilor: {exc}")
        return []
    finally:
        if cursor:
            cursor.close()
        conn.close()


def delete_user_subscription(user_subscription_id: int) -> bool:
    # Sterge un abonament al unui utilizator
    conn = create_database_connection()
    if not conn:
        return False

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_subscriptions WHERE id = %s", (user_subscription_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as exc:
        conn.rollback()
        debug_manager.log(f"Eroare la delete_user_subscription: {exc}")
        return False
    finally:
        if cursor:
            cursor.close()
        conn.close()


def activate_subscription(user_id: int, plan_id: int) -> int:
    # Dezactiveaza abonamentul vechi si creeaza unul nou in aceeasi tranzactie.
    conn = create_database_connection()
    if not conn:
        raise RuntimeError(DB_CONNECTION_ERROR)

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT duration FROM subscriptions WHERE id = %s", (plan_id,))
        plan_row = cursor.fetchone()
        if not plan_row:
            raise ValueError("Planul de abonament nu exista")

        plan_duration = int(plan_row[0])
        start_date = datetime.now()
        end_date = start_date + timedelta(days=plan_duration)
        cursor.execute(
            """
            UPDATE user_subscriptions
            SET active = FALSE
            WHERE user_id = %s AND active = TRUE
            """,
            (user_id,),
        )
        cursor.execute(
            """
            INSERT INTO user_subscriptions (user_id, start_date, end_date, plan_id, active)
            VALUES (%s, %s, %s, %s, TRUE)
            RETURNING id
            """,
            (user_id, start_date, end_date, plan_id),
        )
        subscription_id = cursor.fetchone()[0]
        conn.commit()
        return int(subscription_id)
    except Exception as exc:
        conn.rollback()
        debug_manager.log(f"Eroare la activarea abonamentului utilizatorului: {exc}")
        raise
    finally:
        if cursor:
            cursor.close()
        conn.close()


def fetch_active_subscription_plan_by_plate(numar_inmatriculare: str):
    # Returneaza abonamentul activ al utilizatorului pentru un numar de inmatriculare
    conn = create_database_connection()
    if not conn:
        return None

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT us.id, us.user_id, us.start_date, us.end_date, us.plan_id, us.active
            FROM users u
            JOIN user_subscriptions us ON us.user_id = u.id
            WHERE u.numar_inmatriculare = %s AND us.active = TRUE AND us.end_date >= %s
            ORDER BY us.end_date DESC, us.id DESC
            LIMIT 1
            """,
            (numar_inmatriculare, datetime.now()),
        )
        return cursor.fetchone()
    except Exception as exc:
        debug_manager.log(f"Eroare la citirea abonamentului activ: {exc}")
        return None
    finally:
        if cursor:
            cursor.close()
        conn.close()

def fetch_active_subscription_by_user_id(user_id: int):
    # Returneaza abonamentul activ al utilizatorului dupa id
    conn = create_database_connection()
    if not conn:
        return None

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT us.id, us.user_id, us.start_date, us.end_date, us.plan_id, us.active, s.nume, s.price, s.duration
            FROM user_subscriptions us
            JOIN subscriptions s ON s.id = us.plan_id
            WHERE us.user_id = %s AND us.active = TRUE AND us.end_date >= %s
            ORDER BY us.end_date DESC, us.id DESC
            LIMIT 1
            """,
            (user_id, datetime.now()),
        )
        return cursor.fetchone()
    except Exception as exc:
        debug_manager.log(f"Eroare la citirea abonamentului activ dupa id: {exc}")
        return None
    finally:
        if cursor:
            cursor.close()
        conn.close()


def fetch_users_for_admin() -> list[tuple]:
    # Returneaza utilizatorii pentru admin
    conn = create_database_connection()
    if not conn:
        return []

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, nume, prenume, email, numar_inmatriculare
            FROM users
            ORDER BY id
            """
        )
        return cursor.fetchall()
    except Exception as exc:
        debug_manager.log(f"Eroare la citirea userilor pentru admin: {exc}")
        return []
    finally:
        if cursor:
            cursor.close()
        conn.close()


def delete_user_by_id(user_id: int) -> bool:
    # Sterge un user si fisierul QR asociat
    conn = create_database_connection()
    if not conn:
        return False

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT numar_inmatriculare FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        if cursor.rowcount > 0 and row and row[0]:
            try:
                _remove_qr_file(row[0])
            except Exception as cleanup_error:
                debug_manager.log(f"Eroare la stergerea QR: {cleanup_error}")
            return True
        return False
    except Exception as exc:
        conn.rollback()
        debug_manager.log(f"Eroare la stergerea userului: {exc}")
        return False
    finally:
        if cursor:
            cursor.close()
        conn.close()


def enter_parking(numar_inmatriculare: str) -> str | None:
    #Insereaza o noua inregistrare in `masini`.
    # - genereaza un `cod` random de 10 litere
    # - seteaza `ora_intrare` la timpul curent
    # - `ora_platire` si `ora_plecare` raman NULL

    # Daca masina exista deja (s-a intors, sau are `ora_platire` nenull)
    # se actualizeaza ora la prezent si se sterge plata veche
    
    conn = create_database_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cod = ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
        cursor.execute(
            """
            SELECT 1
            FROM users
            WHERE numar_inmatriculare = %s
            LIMIT 1
            """,
            (numar_inmatriculare,),
        )
        status = "User" if cursor.fetchone() else "Vizitator"

        # Inseram sau actualizam daca exista deja, folosind ON CONFLICT
        cursor.execute("""
            INSERT INTO masini (numar_inmatriculare, cod, ora_intrare, ora_platire, status)
            VALUES (%s, %s, %s, NULL, %s)
            ON CONFLICT (numar_inmatriculare) DO UPDATE
            SET cod = EXCLUDED.cod,
                ora_intrare = EXCLUDED.ora_intrare,
                ora_platire = NULL,
                status = EXCLUDED.status
        """, (numar_inmatriculare, cod, datetime.now(), status))

        conn.commit()
        return cod

    except Exception as e:
        debug_manager.log(f"Eroare la enter_parking: {e}")
        conn.rollback()
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def pay_parking(cod: str) -> bool:
    # Inregistreaza plata pentru masina cu codul generat la intrare
    # Seteaza ora_platire = NOW() pentru codul specificat
    # Returneaza True daca plata a fost inregistrata cu succes
    
    conn = create_database_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        
        # Inregistram plata (actualizam ora_platire)
        cursor.execute("""
            UPDATE masini
            SET ora_platire = %s
            WHERE cod = %s
        """, (datetime.now(), cod))
        conn.commit()
        
        return cursor.rowcount > 0

    except Exception as e:
        debug_manager.log(f"Eroare la pay_parking: {e}")
        conn.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_parking_fee(
    *,
    numar_inmatriculare: str | None = None,
    cod: str | None = None,
) -> dict | None:
    # Calculeaza durata si tariful dupa numarul de inmatriculare sau codul parcarii.
    if bool(numar_inmatriculare) == bool(cod):
        raise ValueError("Furnizeaza exact un identificator pentru parcare")

    conn = create_database_connection()
    if not conn:
        raise RuntimeError(DB_CONNECTION_ERROR)

    cursor = None
    try:
        cursor = conn.cursor()
        if numar_inmatriculare:
            cursor.execute(
                """
                SELECT cod, numar_inmatriculare, ora_intrare, ora_platire
                FROM masini
                WHERE numar_inmatriculare = %s
                """,
                (numar_inmatriculare,),
            )
        else:
            cursor.execute(
                """
                SELECT cod, numar_inmatriculare, ora_intrare, ora_platire
                FROM masini
                WHERE cod = %s
                """,
                (cod,),
            )
        parking_row = cursor.fetchone()
        if not parking_row:
            return None

        parking_code, plate, ora_intrare, ora_platire = parking_row
        cursor.execute(
            """
            SELECT durata, pret
            FROM taxe
            ORDER BY durata ASC
            """
        )
        taxe_rows = cursor.fetchall()
        if not taxe_rows:
            raise RuntimeError("Nu exista tarife configurate in sistem")

        now = datetime.now()
        parked_minutes = max(0, int((now - ora_intrare).total_seconds() / 60))
        billing_start = ora_platire if ora_platire is not None else ora_intrare
        billable_minutes = max(0, int((now - billing_start).total_seconds() / 60))

        amount = float(taxe_rows[-1][1])
        for durata_minute, pret in taxe_rows:
            if billable_minutes <= durata_minute:
                amount = float(pret)
                break

        return {
            "parking_code": parking_code,
            "license_plate": plate,
            "parked_minutes": parked_minutes,
            "billable_minutes": billable_minutes,
            "amount": amount,
        }
    except Exception as exc:
        debug_manager.log(f"Eroare la calcularea tarifului parcarii: {exc}")
        raise
    finally:
        if cursor:
            cursor.close()
        conn.close()


def get_parking_status_by_plate(numar_inmatriculare: str) -> str:
    # Returneaza statusul parcarii pentru un numar de inmatriculare
    conn = create_database_connection()
    if not conn:
        return "invalid"

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ora_platire
            FROM masini
            WHERE numar_inmatriculare = %s
            """,
            (numar_inmatriculare,),
        )
        row = cursor.fetchone()
        if not row:
            return "invalid"

        # Daca userul are abonament activ, il consideram echivalent cu plata efectuata
        cursor.execute(
            """
            SELECT 1
            FROM users u
            JOIN user_subscriptions us ON us.user_id = u.id
            WHERE u.numar_inmatriculare = %s
              AND us.active = TRUE
              AND us.end_date >= %s
            LIMIT 1
            """,
            (numar_inmatriculare, datetime.now()),
        )
        if cursor.fetchone():
            return "paid"

        # Verifica starea parcarii in functie de ora_platire
        ora_platire = row[0]
        if ora_platire is None:
            return "waiting_payment"

        # Verifica daca plata a expirat
        elapsed_minutes = (datetime.now() - ora_platire).total_seconds() / 60
        if elapsed_minutes < 5:
            return "paid"

        return "payment_expired"
    except Exception as e:
        debug_manager.log(f"Eroare la get_parking_status_by_plate: {e}")
        return "invalid"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def _delete_parking_entry_and_cleanup(cursor, conn, cod: str) -> tuple[bool, str]:
    # Sterge inregistrarea din `masini` pentru codul specificat
    cursor.execute(
        """
        DELETE FROM masini
        WHERE cod = %s
        RETURNING numar_inmatriculare
        """,
        (cod,),
    )
    deleted_row = cursor.fetchone()
    if cursor.rowcount <= 0:
        return (False, "error")

    if deleted_row and deleted_row[0]:
        try:
            _remove_qr_file(deleted_row[0])
        except Exception as cleanup_error:
            debug_manager.log(f"Eroare la stergerea QR: {cleanup_error}")

    conn.commit()

    return (True, "success")


def leave_parking(cod: str) -> tuple[bool, str]:

     # Daca masina cu `cod` are `ora_platire` != NULL si timpul scurs < 5 minute, o sterge din baza de date.
    
    conn = create_database_connection()
    if not conn:
        return (False, "error")

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ora_platire, numar_inmatriculare
                       FROM masini 
                       WHERE cod = %s
        """, (cod,))
        row = cursor.fetchone()
        if not row:
            debug_manager.log("Eroare: Codul nu exista in baza de date.")
            return (False, "not_found")
        ora_platire = row[0]
        numar_inmatriculare = row[1]

        if fetch_active_subscription_plan_by_plate(numar_inmatriculare):
            return _delete_parking_entry_and_cleanup(cursor, conn, cod)

        if ora_platire is None:
            # Plata nu a fost facuta inca
            debug_manager.log("Eroare: Plata nu a fost efectuata.")
            return (False, "not_paid")

        # Verificam daca au trecut mai putin de 5 minute de la plata
        elapsed_minutes = (datetime.now() - ora_platire).total_seconds() / 60
        if elapsed_minutes >= 5:
            debug_manager.log(f"Eroare: Au trecut {elapsed_minutes:.1f} minute de la plata. Limita este de 5 minute.")
            return (False, "expired")

        return _delete_parking_entry_and_cleanup(cursor, conn, cod)

    except Exception as e:
        debug_manager.log(f"Eroare la leave_parking: {e}")
        conn.rollback()
        return (False, "error")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_taxa(id_taxa: int, durata_noua: int, pret_nou: float) -> bool:
    # Actualizeaza durata si pretul in tabelul Taxe pentru taxa cu id-ul specificat
    conn = create_database_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE taxe
            SET durata = %s, pret = %s
            WHERE id = %s
        """, (durata_noua, pret_nou, id_taxa))
        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        debug_manager.log(f"Eroare la update_taxa: {e}")
        conn.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def add_taxa(durata: int, pret: float) -> bool:
    # Adauga o noua taxa in tabelul Taxe
    conn = create_database_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO taxe (durata, pret)
            VALUES (%s, %s)
        """, (durata, pret))
        conn.commit()
        return True
    except Exception as e:
        debug_manager.log(f"Eroare la adaugarea taxei: {e}")
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def delete_taxa(id_taxa: int) -> bool:
    # Sterge o taxa din tabelul Taxe dupa ID
    conn = create_database_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM taxe WHERE id = %s", (id_taxa,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        debug_manager.log(f"Eroare la stergerea taxei: {e}")
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def delete_masina(numar_inmatriculare: str) -> bool:
    # Sterge o masina din tabelul Masini dupa numar de inmatriculare
    conn = create_database_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM masini WHERE numar_inmatriculare = %s", (numar_inmatriculare,))
        conn.commit()
        if cursor.rowcount > 0:
            try:
                _remove_qr_file(numar_inmatriculare)
            except Exception as cleanup_error:
                debug_manager.log(f"Eroare la stergerea QR: {cleanup_error}")
            return True
        return False
    except Exception as e:
        debug_manager.log(f"Eroare la stergerea masinii: {e}")
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def show_masini():
    # Selecteaza si afiseaza toate inregistrarile din tabelul Masini
    conn = create_database_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT numar_inmatriculare, cod, ora_intrare, ora_platire, status FROM masini ORDER BY ora_intrare DESC
        """)
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        debug_manager.log(f"Eroare la show_masini: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def show_taxe():
    # Selecteaza si afiseaza toate inregistrarile din tabelul Taxe dupa durata
    conn = create_database_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, durata, pret FROM taxe ORDER BY durata
        """)
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        debug_manager.log(f"Eroare la show_taxe: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def count_cars_in_parking() -> int:
    # Returneaza numarul total de masini din baza de date
    conn = create_database_connection()
    if not conn:
        return 0

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM masini
        """)
        row = cursor.fetchone()
        return int(row[0]) if row else 0

    except Exception as e:
        debug_manager.log(f"Eroare la count_cars_in_parking: {e}")
        return 0

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Initializare - creeaza tabelele doar cand fisierul este rulat direct
if __name__ == "__main__":
    create_tables()
