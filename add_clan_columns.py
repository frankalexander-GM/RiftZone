import sqlite3

db_path = r'c:\seguridad copy\plataforma web\RiftZone\app\riftzone_dev.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

columnas = [
    ("banner_url", "VARCHAR(255)"),
    ("privacidad", "VARCHAR(20) DEFAULT 'publico'"),
    ("nivel", "INTEGER DEFAULT 1"),
    ("xp", "INTEGER DEFAULT 0")
]

for col_name, col_type in columnas:
    try:
        cursor.execute(f"ALTER TABLE clanes ADD COLUMN {col_name} {col_type}")
        print(f"Columna {col_name} añadida con éxito.")
    except Exception as e:
        print(f"No se pudo añadir {col_name} (quizás ya existe): {e}")

conn.commit()
conn.close()
print("Cirugía completada.")
