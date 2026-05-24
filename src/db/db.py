import psycopg2
from datetime import datetime
import random
import string

def create_database_connection():
    # Creeaza o conexiune la baza de date PostgreSQL
    try:
        conn = psycopg2.connect(database="parkingDB",
                              host="localhost",
                              user="postgres",
                              password="1234",
                              port="1234")
        return conn
    except Exception as e:
        print(f"Eroare la conectarea la baza de date: {e}")
        return None

def create_tables():
    # Creeaza tabelele in baza de date
    conn = create_database_connection()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        
        # Tabelul masini
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS masini (
                numar_inmatriculare VARCHAR(20) PRIMARY KEY,
                cod VARCHAR(20) UNIQUE,
                ora_intrare TIMESTAMP NOT NULL,
                ora_platire TIMESTAMP
            )
        """)
        
        # Tabelul taxe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS taxe (
                id SERIAL PRIMARY KEY,
                durata INTEGER NOT NULL,
                pret DECIMAL(10,2) NOT NULL
            )
        """)
        
        conn.commit()
        print("Tabelele au fost create cu succes!")
        
        return True
        
    except Exception as e:
        print(f"Eroare la crearea tabelelor: {e}")
        conn.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def _generate_cod(length: int = 10) -> str:
    # Genereaza un cod random
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))


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
        cod = _generate_cod(10)

        # Inseram sau actualizam daca exista deja, folosind ON CONFLICT
        cursor.execute("""
            INSERT INTO masini (numar_inmatriculare, cod, ora_intrare, ora_platire)
            VALUES (%s, %s, %s, NULL)
            ON CONFLICT (numar_inmatriculare) DO UPDATE
            SET cod = EXCLUDED.cod,
                ora_intrare = EXCLUDED.ora_intrare,
                ora_platire = NULL
        """, (numar_inmatriculare, cod, datetime.now()))

        conn.commit()
        return cod

    except Exception as e:
        print(f"Eroare la enter_parking: {e}")
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
        print(f"Eroare la pay_parking: {e}")
        conn.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def leave_parking(cod: str) -> tuple[bool, str]:

     # Daca masina cu `cod` are `ora_platire` != NULL si timpul scurs < 5 minute, o sterge din baza de date.
    
    conn = create_database_connection()
    if not conn:
        return (False, "error")

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ora_platire
                       FROM masini 
                       WHERE cod = %s
        """, (cod,))
        row = cursor.fetchone()
        if not row:
            print("Eroare: Codul nu exista in baza de date.")
            return (False, "not_found")

        ora_platire = row[0]
        if ora_platire is None:
            # Plata nu a fost facuta inca
            print("Eroare: Plata nu a fost efectuata.")
            return (False, "not_paid")

        # Verificam daca au trecut mai putin de 5 minute de la plata
        ora_actuala = datetime.now()
        diferenta = (ora_actuala - ora_platire).total_seconds() / 60  # convertim in minute
        
        if diferenta >= 5:
            print(f"Eroare: Au trecut {diferenta:.1f} minute de la plata. Limita este de 5 minute.")
            return (False, "expired")

        cursor.execute("""
            DELETE FROM masini
            WHERE cod = %s
            RETURNING numar_inmatriculare
        """, (cod,))
        deleted_row = cursor.fetchone()
        conn.commit()
        if cursor.rowcount > 0:
            if deleted_row and deleted_row[0]:
                try:
                    import os
                    qr_folder = os.path.join(os.path.dirname(__file__), '..', '..', 'qrcodes')
                    qr_filename = os.path.join(qr_folder, f"qr_{deleted_row[0]}.png")
                    if os.path.exists(qr_filename):
                        os.remove(qr_filename)
                except Exception as cleanup_error:
                    print(f"Eroare la stergerea QR: {cleanup_error}")
            return (True, "success")
        else:
            return (False, "error")

    except Exception as e:
        print(f"Eroare la leave_parking: {e}")
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
        print(f"Eroare la update_taxa: {e}")
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
        print(f"Eroare la adaugarea taxei: {e}")
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
        print(f"Eroare la stergerea taxei: {e}")
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
                import os
                qr_folder = os.path.join(os.path.dirname(__file__), '..', '..', 'qrcodes')
                qr_filename = os.path.join(qr_folder, f"qr_{numar_inmatriculare}.png")
                if os.path.exists(qr_filename):
                    os.remove(qr_filename)
            except Exception as cleanup_error:
                print(f"Eroare la stergerea QR: {cleanup_error}")
            return True
        return False
    except Exception as e:
        print(f"Eroare la stergerea masinii: {e}")
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
            SELECT numar_inmatriculare, cod, ora_intrare, ora_platire FROM masini ORDER BY ora_intrare DESC
        """)
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        print(f"Eroare la show_masini: {e}")
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
        print(f"Eroare la show_taxe: {e}")
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
        print(f"Eroare la count_cars_in_parking: {e}")
        return 0

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Initializare - creeaza tabelele doar cand fisierul este rulat direct
if __name__ == "__main__":
    create_tables()