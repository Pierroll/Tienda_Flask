from website import create_app, db
from website.models import Category

def create_sample_categories():
    app = create_app()
    with app.app_context():
        # Verificar si ya hay categorías
        if not Category.query.first():
            print("Creando categorías de ejemplo...")
            categories = [
                Category(name='Electrónica', description='Dispositivos electrónicos', icon='fa fa-laptop'),
                Category(name='Ropa', description='Ropa y accesorios', icon='fa fa-tshirt'),
                Category(name='Hogar', description='Artículos para el hogar', icon='fa fa-home'),
                Category(name='Deportes', description='Artículos deportivos', icon='fa fa-futbol'),
                Category(name='Juguetes', description='Juguetes y juegos', icon='fa fa-gamepad')
            ]
            
            try:
                for category in categories:
                    db.session.add(category)
                db.session.commit()
                print("Categorías de ejemplo creadas exitosamente.")
            except Exception as e:
                db.session.rollback()
                print(f"Error al crear categorías: {str(e)}")
        else:
            print("Ya existen categorías en la base de datos.")

if __name__ == '__main__':
    create_sample_categories()
