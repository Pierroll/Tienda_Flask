"""
Manejadores de Error
Centraliza el manejo de errores HTTP y excepciones del sistema.

Características de Calidad ISO/IEC 25010:
- Fiabilidad: Manejo consistente de errores
- Usabilidad: Mensajes de error claros y útiles
- Seguridad: No exposición de información sensible en errores
"""

from flask import render_template
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """
    Registra los manejadores de error para la aplicación.
    
    Args:
        app: Instancia de Flask
    """
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Maneja errores 404 - Página no encontrada"""
        logger.info(f"404 Error: {error}")
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        """Maneja errores 403 - Acceso prohibido"""
        logger.warning(f"403 Error: {error}")
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores 500 - Error interno del servidor"""
        logger.error(f"500 Error: {error}")
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        """Maneja excepciones no controladas"""
        logger.critical(f"Unhandled Exception: {error}")
        return render_template('errors/500.html'), 500 