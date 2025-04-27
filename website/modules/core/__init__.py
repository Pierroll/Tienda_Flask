"""
Módulo Core
Contiene la funcionalidad central y configuración base del sistema.

Características de Calidad ISO/IEC 25010:
- Portabilidad: Configuración centralizada para facilitar la adaptación
- Mantenibilidad: Estructura modular y documentada
- Seguridad: Configuración de seguridad centralizada
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()

def init_core(app):
    """
    Inicializa los componentes core de la aplicación.
    
    Args:
        app: Instancia de Flask
    """
    # Configuración de la base de datos
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    # Configuración de seguridad
    csrf.init_app(app)
    
    # Configuración de autenticación
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Registro de módulos
    from ..modules import register_modules
    register_modules(app) 