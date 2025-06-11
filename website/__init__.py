from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from os import path
import os
import secrets
import string

# Importar modelos de cliente al nivel del módulo
# Los modelos se importarán cuando se inicialice la aplicación para evitar importaciones circulares


# Inicializar extensiones
db = SQLAlchemy()
DB_NAME = "database.sqlite3"
csrf = CSRFProtect()
mail = Mail()

# Configuración de SQLAlchemy
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Clave de seguridad para el administrador (debería estar en una variable de entorno)
ADMIN_SECURITY_KEY = os.environ.get('ADMIN_SECURITY_KEY', 'your-super-secret-key-here')


def generate_secure_password(length=12):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def create_super_admin():
    """Create a super admin user if none exists."""
    from .models import Customer
    super_admin = Customer.query.filter_by(role='super_admin').first()
    if not super_admin:
        password = "admin123"  # Contraseña fija
        super_admin = Customer(
            email='admin@tienda.com',
            username='super_admin',
            role='super_admin',
            force_password_change=True,
            is_first_login=True
        )
        super_admin.password = password
        db.session.add(super_admin)
        db.session.commit()
        print('='*50)
        print('DATOS DE ACCESO DEL SUPER ADMIN:')
        print('Email: admin@tienda.com')
        print('Usuario: super_admin')
        print('Contraseña: admin123')
        print('='*50)


def create_database(app):
    with app.app_context():
        # Solo crear las tablas si no existen
        db.create_all()
        
        # Verificar si ya existe un super admin
        from .models import Customer
        super_admin = Customer.query.filter_by(role='super_admin').first()
        if not super_admin:
            create_super_admin()
    print('Database initialized!')


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    # Usar una clave secreta fija para desarrollo
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, DB_NAME)}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'website/static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

    # Configuración para servir archivos estáticos desde media
    @app.route('/media/<path:filename>')
    def media(filename):
        return send_from_directory('../media', filename)

    # Configuración de Flask-Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@tutienda.com')

    # Crear la carpeta instance si no existe
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Inicializar extensiones
    db.init_app(app)
    # Inicializar CSRF después de crear la aplicación
    csrf = CSRFProtect()
    csrf.init_app(app)
    mail.init_app(app)
    
    # Configurar CSRF para ignorar rutas específicas
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False
    app.config['WTF_CSRF_ENABLED'] = True

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html')

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html'), 500

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Esta ruta ahora será /auth/login
    login_manager.init_app(app)

    from .models import Customer, Cart, Order, OrderItem
    from .modules.product.models import Product
    from .modules.category.models import Category

    @login_manager.user_loader
    def load_user(id):
        return Customer.query.get(int(id))

    # Importar rutas después de crear la aplicación para evitar importaciones circulares
    from .views import views
    from .admin import admin
    
    # Importar y registrar módulos
    from .modules.auth import create_module as create_auth_module
    from .modules.product import create_module as create_product_module
    from .modules.category import create_module as create_category_module
    from .modules.cliente import cliente_bp
    from .modules.admin import init_module as init_admin_module
    
    # Registrar blueprints con prefijos específicos para evitar conflictos
    app.register_blueprint(views, url_prefix='/')
    
    # Registrar módulo de autenticación
    auth_bp = create_auth_module(app)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Registrar módulo de administración
    admin_bp = init_admin_module(app)
    
    # Si necesitas mantener la ruta de administración antigua, usa un nombre diferente
    # from .admin import admin as old_admin
    # app.register_blueprint(old_admin, name='old_admin', url_prefix='/admin_old')
    
    # Registrar módulo de productos
    product_bp = create_product_module()
    app.register_blueprint(product_bp, url_prefix='/product')
    
    # Registrar módulo de categorías
    category_bp = create_category_module()
    app.register_blueprint(category_bp, url_prefix='/category')
    
    # Registrar módulo de cliente
    from .modules.cliente import init_app as init_cliente
    cliente_bp = init_cliente(app)
    app.register_blueprint(cliente_bp, url_prefix='/cliente')
    
    # Importar modelos después de inicializar la aplicación
    from .modules.cliente.models import DireccionEnvio, ListaDeseos, ProductoListaDeseos
    
    # Hacer los modelos disponibles en el paquete
    globals().update({
        'DireccionEnvio': DireccionEnvio,
        'ListaDeseos': ListaDeseos,
        'ProductoListaDeseos': ProductoListaDeseos
    })
    
    create_database(app)
    
    # Asegurar que el token CSRF esté disponible en todas las plantillas
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)

    return app

