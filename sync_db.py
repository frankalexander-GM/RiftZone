import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'games_sphere_dev.db')
print(f"Sincronizando base de datos: {db_path}")

columns_to_add = [
    # Tabla publicaciones
    ("publicaciones", "promocionada", "BOOLEAN DEFAULT 0"),
    # Tabla usuarios
    ("usuarios", "foto_banner", "VARCHAR(255)"),
    ("usuarios", "banner", "VARCHAR(255)"),
    ("usuarios", "pais", "VARCHAR(50)"),
    ("usuarios", "estado_personalizado", "VARCHAR(100)"),
    ("usuarios", "twitch", "VARCHAR(100)"),
    ("usuarios", "kick", "VARCHAR(100)"),
    ("usuarios", "youtube", "VARCHAR(100)"),
    ("usuarios", "discord", "VARCHAR(100)"),
    ("usuarios", "steam", "VARCHAR(100)"),
    ("usuarios", "titulo_perfil", "VARCHAR(50) DEFAULT 'Gamer'"),
    # Tabla mensajes_privados
    ("mensajes_privados", "leido_en", "DATETIME"),
    ("mensajes_privados", "editado", "BOOLEAN DEFAULT 0")
]

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for table, column, col_def in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def};")
            print(f"Columna '{column}' añadida a la tabla '{table}'.")
        except sqlite3.OperationalError as e:
            # Error comun si la columna ya existe
            pass
    conn.commit()
    print("Sincronización de base de datos completada exitosamente.")
except Exception as e:
    print(f"Error general: {e}")
finally:
    conn.close()
