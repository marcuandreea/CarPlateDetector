from typing import List, Tuple

from .core import create_database_connection, DB_CONNECTION_ERROR
from detector.debug_manager import debug_manager


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
