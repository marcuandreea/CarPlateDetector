from datetime import datetime
import random
import string

from .core import create_database_connection, _remove_qr_file, DB_CONNECTION_ERROR
from detector.debug_manager import debug_manager
from .user_subscriptions import fetch_active_subscription_plan_by_plate


def enter_parking(numar_inmatriculare: str) -> str | None:
    # Insereaza o noua inregistrare in `masini`.
    conn = create_database_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 1
            FROM masini
            WHERE numar_inmatriculare = %s
            LIMIT 1
            """,
            (numar_inmatriculare,),
        )
        if cursor.fetchone():
            raise ValueError("Mașina se afla in parcare")

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

        # Inseram o noua inregistrare in parcare
        cursor.execute("""
            INSERT INTO masini (numar_inmatriculare, cod, ora_intrare, ora_platire, status)
            VALUES (%s, %s, %s, NULL, %s)
        """, (numar_inmatriculare, cod, datetime.now(), status))

        conn.commit()
        return cod

    except ValueError:
        conn.rollback()
        raise
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
    # Inregistreaza plata pentru masina
    conn = create_database_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        
        # Inregistram plata 
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
    # Calculeaza durata si tariful 
    if bool(numar_inmatriculare) == bool(cod):
        raise ValueError("Furnizeaza exact un identificator pentru parcare")

    conn = create_database_connection()
    if not conn:
        raise RuntimeError(DB_CONNECTION_ERROR)

    cursor = None
    try:
        # Daca avem numar de inmatriculare, cautam masina dupa numar
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
            # Daca avem codul, cautam masina dupa cod
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
        # Selectam toate taxele disponibile, ordonate dupa durata
        cursor.execute(
            """
            SELECT durata, pret
            FROM taxe
            ORDER BY durata ASC
            """
        )

        # Extragerea tuturor taxelor disponibile
        taxe_rows = cursor.fetchall()
        if not taxe_rows:
            raise RuntimeError("Nu exista tarife configurate in sistem")

        # Calculam timpul parcarii
        now = datetime.now()
        parked_minutes = max(0, int((now - ora_intrare).total_seconds() / 60))
        billing_start = ora_platire if ora_platire is not None else ora_intrare
        billable_minutes = max(0, int((now - billing_start).total_seconds() / 60))

        # Determinarea tarifului corespunzator
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
    # Daca masina cu `cod` are `ora_platire` != NULL si timpul scurs < 5 minute, o sterge din baza de date
    
    conn = create_database_connection()
    if not conn:
        return (False, "error")

    # Verificam daca plata a fost efectuata
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
