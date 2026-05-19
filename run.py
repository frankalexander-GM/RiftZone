import os
from app.factories.app_factory import create_app

# Determinar el entorno de configuración
config_name = os.environ.get('FLASK_ENV', 'development')

# Crear la aplicación usando el factory pattern
app = create_app(config_name)

if __name__ == '__main__':
    # Configuración para desarrollo
    debug_mode = config_name == 'development'
    port = int(os.environ.get('PORT', 5050))
    
    print(f"GamesSphere Backend iniciando en modo {config_name}")
    print(f"Debug: {debug_mode}")
    print(f"Port: {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )
