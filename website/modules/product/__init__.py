from flask import Blueprint

def create_module():
    from . import routes
    return routes.product_blueprint
