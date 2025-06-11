from . import routes

def create_module():
    # Importar las rutas para registrar los endpoints
    from . import routes
    # Retornar el blueprint ya configurado en routes.py
    bp = routes.category_blueprint
    return bp
