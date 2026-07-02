from datetime import datetime, timedelta

from .core import create_database_connection, DB_CONNECTION_ERROR
from detector.debug_manager import debug_manager


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
