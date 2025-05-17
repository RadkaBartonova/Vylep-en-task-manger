import pytest
import mysql.connector
from mysql.connector import Error
from config import TEST_DB_CONFIG

# Setup/teardown fixture
@pytest.fixture
def test_db():
    conn = mysql.connector.connect(**TEST_DB_CONFIG)
    cursor = conn.cursor()

    # Vytvoření testovací tabulky
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
    yield cursor
    cursor.execute("DELETE FROM ukoly")  # Vyčistit tabulku po testu
    conn.commit()
    conn.close()

def test_pridat_ukol_valid(test_db):
    test_db.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", ("Test Úkol", "Popis"))
    test_db.execute("SELECT * FROM ukoly WHERE nazev = %s", ("Test Úkol",))
    result = test_db.fetchone()
    assert result is not None
    assert result[1] == "Test Úkol"

def test_pridat_ukol_invalid(test_db):
    with pytest.raises(Error):
        test_db.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", (None, "Popis"))

def test_aktualizace_ukolu_valid(test_db):
    test_db.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", ("Aktualizuj", "Popis"))
    test_db.execute("UPDATE ukoly SET stav = %s WHERE nazev = %s", ("Hotovo", "Aktualizuj"))
    test_db.execute("SELECT stav FROM ukoly WHERE nazev = %s", ("Aktualizuj",))
    result = test_db.fetchone()
    assert result[0] == "Hotovo"

def test_aktualizace_ukolu_invalid(test_db):
    test_db.execute("UPDATE ukoly SET stav = %s WHERE id = %s", ("NeplatnýStav", 9999))
    test_db.execute("SELECT COUNT(*) FROM ukoly")
    count = test_db.fetchone()[0]
    assert count == 0

def test_odstranit_ukol_valid(test_db):
    test_db.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", ("Smazat", "Popis"))
    test_db.execute("SELECT id FROM ukoly WHERE nazev = %s", ("Smazat",))
    task_id = test_db.fetchone()[0]
    test_db.execute("DELETE FROM ukoly WHERE id = %s", (task_id,))
    test_db.execute("SELECT * FROM ukoly WHERE id = %s", (task_id,))
    result = test_db.fetchone()
    assert result is None

def test_odstranit_ukol_invalid(test_db):
    test_db.execute("DELETE FROM ukoly WHERE id = %s", (9999,))
    # Úkol s tímto ID neexistuje – nemělo by to nic změnit
    test_db.execute("SELECT COUNT(*) FROM ukoly")
    count = test_db.fetchone()[0]
    assert count == 0