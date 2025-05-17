import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG   # tell Radka to use config.py


def pripojeni_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print("Připojení k databázi bylo úspěšné.")
            return conn
    except Error as e:
        print(f"Chyba při připojování k databázi: {e}")
        return None

def vytvoreni_tabulky(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(255) NOT NULL,
                popis TEXT NOT NULL,
                stav ENUM('Nezahájeno', 'Hotovo', 'Probíhá') DEFAULT 'Nezahájeno',
                datum_vytvoreni DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Tabulka 'ukoly' byla ověřena/vytvořena.")
    except Error as e:
        print(f"Chyba při vytváření tabulky: {e}")


# Funkce pro přidání úkolu: volba 1
def pridat_ukol(conn):
    while True:
        nazev_ukolu = input("Zadejte název úkolu: ")
        popis_ukolu = input("Zadejte popis úkolu: ")

        if nazev_ukolu == "" or popis_ukolu == "":
            print("Název ani popis nesmí být prázdné. Zkuste to znovu prosím")
        else:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)",
                (nazev_ukolu, popis_ukolu)
            )
            conn.commit()
            print(f"Úkol '{nazev_ukolu}' byl úspěšně přidán")
            break

# Funkce pro zobrazení úkolu: volba 2
def zobrazit_ukoly(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, nazev, popis, stav FROM ukoly")
    ukoly = cursor.fetchall()

    if ukoly:
        print("Vaše úkoly v seznamu: ")
        for ukol in ukoly:
            print(f"ID: {ukol[0]}, Název: {ukol[1]}, Popis: {ukol[2]}, Stav: {ukol[3]}")
    else:
        print("Seznam úkolů je prázdný")

# Funkce pro zobrazení úkolů: volba 3
def odstranit_ukol(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, nazev FROM ukoly")
    ukoly = cursor.fetchall()

    if ukoly:
        for ukol in ukoly:
            print(f"ID: {ukol[0]}, Název: {ukol[1]}")
        try:
            smazani_ukolu = int(input("Jaký úkol chcete smazat? (zadejte ID): "))
            # add error if ukol with this ID does not exist
            cursor.execute("DELETE FROM ukoly WHERE id = %s", (smazani_ukolu,))
            conn.commit()
            print(f"Úkol s ID {smazani_ukolu} byl smazán.")
        except Exception:
            print("Zadali jste neplatné ID.")
    else:
        print("Seznam úkolů je prázdný")

def aktualizovat_ukol(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, nazev, stav FROM ukoly")
    ukoly = cursor.fetchall()

    if not ukoly:
        print("Seznam úkolů je prázdný.")
        return

    print("Seznam úkolů:")
    for ukol in ukoly:
        print(f"ID: {ukol[0]}, Název: {ukol[1]}, Stav: {ukol[2]}")

    try:
        vybrane_id = int(input("Zadejte ID úkolu, který chcete aktualizovat: "))
    except ValueError:
        print("Neplatné ID.")
        return

    # Ověření, že ID existuje
    if not any(ukol[0] == vybrane_id for ukol in ukoly):
        print("Úkol s tímto ID neexistuje.")
        return

    print("Možnosti nového stavu: Probíhá, Hotovo")
    novy_stav = input("Zadejte nový stav: ").capitalize()

    if novy_stav not in ["Probíhá", "Hotovo"]:
        print("Neplatný stav.")
        return

    cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", (novy_stav, vybrane_id))
    conn.commit()
    print("Stav úkolu byl úspěšně aktualizován.")

def hlavni_menu(conn):
    chybova_zprava = "Zadejte číslici z možností 1 až 5."
    while True:
        print("\nSprávce úkolů - Hlavní menu")
        print('''
    1 - Přidat úkol
    2 - Zobrazit úkoly
    3 - Aktualizovat úkol
    4 - Odstranit úkol
    5 - Ukončit program\n
    ''')

        try:
            cislo_ukolu = int(input("Vyberte možnost (1-4): "))
        except ValueError:
            print(chybova_zprava)
            continue

        print("\n")
        if cislo_ukolu == 1:
            pridat_ukol(conn)
        elif cislo_ukolu == 2:
            zobrazit_ukoly(conn)
        elif cislo_ukolu == 3:
            aktualizovat_ukol(conn)
        elif cislo_ukolu == 4:
            odstranit_ukol(conn)
        elif cislo_ukolu == 5:
            print("Konec programu.")
            break
        else:
            print(chybova_zprava)

if __name__ == "__main__":
    conn = pripojeni_db()
    if conn:
        vytvoreni_tabulky(conn)
        hlavni_menu(conn)
        conn.close()