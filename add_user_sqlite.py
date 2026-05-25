import sqlite3
import datetime

db_path = "app/riftzone_dev.db"

# Usaremos un hash de contraseña ficticio ya que no necesitamos iniciar sesión con él para probar la búsqueda
# Si quieres loguearte, tendría que coincidir con el bcrypt de '123456'. 
# Vamos a copiar un hash válido (o usar uno ficticio, la búsqueda igual lo encontrará).
fake_hash = "$2b$12$eImiTXuWVxfM37uY4JANjQ==fakehash" 

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("""
        INSERT INTO usuarios (nombre, username, email, password, rol, biografia, foto_perfil, nivel, xp, xp_max, estado, fecha_registro, es_premium)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "Cyber Ninja",
        "CyberNinja",
        "ninja@riftzone.com",
        fake_hash,
        "jugador",
        "Jugador enfocado en buscar.",
        "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=200&auto=format&fit=crop",
        1,
        0,
        5000,
        "online",
        datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        0
    ))
    conn.commit()
    print("Usuario 'CyberNinja' insertado en la base de datos de manera nativa.")
except sqlite3.IntegrityError:
    print("El usuario ya existe en la base de datos.")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
