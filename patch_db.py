import sqlite3
import os

try:
    # Ruta correcta a la base de datos de desarrollo
    db_path = os.path.join('app', 'games_sphere_dev.db')
    c = sqlite3.connect(db_path)
    cur = c.cursor()
    cur.execute("ALTER TABLE usuarios ADD COLUMN titulo_perfil VARCHAR(50) DEFAULT 'Gamer'")
    c.commit()
    print("¡Exito! La columna titulo_perfil ha sido agregada a games_sphere_dev.db")
    c.close()
except Exception as e:
    print("Error al agregar columna:", e)
