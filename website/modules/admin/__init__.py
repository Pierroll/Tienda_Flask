from flask import Blueprint

def init_module(app):
    from . import routes
    admin_bp = routes.create_module()
    app.register_blueprint(admin_bp, url_prefix='/admin')
    return admin_bp
