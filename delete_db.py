import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'games_sphere_dev.db')
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"¡EXITO! Archivo eliminado exitosamente: {db_path}")
    except Exception as e:
        print(f"ERROR: No se pudo eliminar el archivo. {e}")
        print("Por favor, asegúrate de que tu servidor de Flask esté DETENIDO (Ctrl+C en la terminal).")
else:
    print(f"El archivo ya no existe (ya fue eliminado): {db_path}")
