from flask import Flask
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
import os

auth_bp = None
mail = Mail()
serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY', 'your-secret-key'))

def create_module(app=None):
    global auth_bp
    
    # Importar las rutas aquí para evitar importaciones circulares
    from . import routes
    
    # Configurar el blueprint
    auth_bp = routes.auth_bp
    
    # Inicializar Flask-Mail
    mail.init_app(app)
    
    return auth_bp
