from website import create_app, db
from website.models import Product, Category

def check_database_structure():
    app = create_app()
    with app.app_context():
        # Verificar estructura de la tabla product
        print("\n=== Estructura de la tabla 'product' ===")
        columns = db.engine.execute("PRAGMA table_info(product)").fetchall()
        if not columns:
            print("La tabla 'product' no existe.")
        else:
            print("Columnas en la tabla 'product':")
            for col in columns:
                print(f"- {col[1]} ({col[2]})")
        
        # Verificar estructura de la tabla category
        print("\n=== Estructura de la tabla 'category' ===")
        columns = db.engine.execute("PRAGMA table_info(category)").fetchall()
        if not columns:
            print("La tabla 'category' no existe.")
        else:
            print("Columnas en la tabla 'category':")
            for col in columns:
                print(f"- {col[1]} ({col[2]})")

if __name__ == '__main__':
    check_database_structure()
