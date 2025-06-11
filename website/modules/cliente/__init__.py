from flask import Blueprint

# Crear el blueprint para el módulo de cliente
cliente_bp = Blueprint('cliente', __name__, 
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/cliente')

def init_app(app):
    """Inicializar la aplicación con el módulo de cliente"""
    # Importar rutas
    from . import routes
    
    return cliente_bp

# Exportar el blueprint para que esté disponible cuando se importe el módulo
__all__ = ['cliente_bp', 'init_app']
