"""
Módulos del sistema de tienda
Este paquete contiene los diferentes módulos que componen el sistema,
organizados según los estándares de calidad ISO/IEC 25010.
"""

from flask import Blueprint

def register_modules(app):
    """
    Registra todos los módulos de la aplicación.
    Cada módulo se registra como un Blueprint de Flask.
    """
    from .auth_module import auth_bp
    from .product_module import product_bp
    from .order_module import order_bp
    from .admin_module import admin_bp
    
    # Registrar los blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(product_bp, url_prefix='/products')
    app.register_blueprint(order_bp, url_prefix='/orders')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Configurar manejadores de error
    from .core.error_handlers import register_error_handlers
    register_error_handlers(app) 