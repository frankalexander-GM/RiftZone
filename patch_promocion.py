import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'games_sphere_dev.db')
print(f"Patching db: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE publicaciones ADD COLUMN promocionada BOOLEAN DEFAULT 0;")
    conn.commit()
    print("Columna 'promocionada' añadida correctamente a la base de datos DEV.")
except sqlite3.OperationalError as e:
    print(f"Error (quizás ya existe): {e}")
finally:
    conn.close()

db_path_prod = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'games_sphere.db')
if os.path.exists(db_path_prod):
    try:
        conn = sqlite3.connect(db_path_prod)
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE publicaciones ADD COLUMN promocionada BOOLEAN DEFAULT 0;")
        conn.commit()
        print("Columna 'promocionada' añadida correctamente a la base de datos PROD.")
    except sqlite3.OperationalError as e:
        print(f"Error (quizás ya existe): {e}")
    finally:
        conn.close()
