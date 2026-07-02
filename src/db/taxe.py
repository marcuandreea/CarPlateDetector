from .core import create_database_connection
from detector.debug_manager import debug_manager


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
