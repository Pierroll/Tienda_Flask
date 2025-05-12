# Tienda Online con Flask

Una aplicación web de tienda online desarrollada con Flask, que incluye funcionalidades de autenticación, gestión de productos, carrito de compras y panel de administración.

## Características

- Autenticación de usuarios con roles (cliente, administrador, super administrador)
- Gestión de productos y categorías
- Carrito de compras
- Panel de administración
- Perfiles de usuario personalizables
- Seguridad mejorada con cambio de contraseña obligatorio
- Interfaz responsiva con Bootstrap 5

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Microsoft Visual C++ Build Tools (para Windows)

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd tienda_con_flask
```

2. Crear y activar un entorno virtual:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar la base de datos:
La base de datos se creará automáticamente al ejecutar la aplicación por primera vez.

## Uso

1. Iniciar la aplicación:
```bash
python run.py
```

2. Acceder a la aplicación en el navegador:
```
http://localhost:5000
```

3. Credenciales iniciales del super administrador:
- Email: admin@tienda.com
- Contraseña: Se generará automáticamente y se mostrará en la consola al crear la base de datos

## Estructura del Proyecto

```
tienda_con_flask/
├── website/
│   ├── static/
│   │   └── uploads/
│   │       └── products/
│   │   ├── templates/
│   │   │   ├── admin/
│   │   │   ├── auth/
│   │   │   └── ...
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── models.py
│   │   └── views.py
│   ├── instance/
│   │   └── database.db
│   ├── requirements.txt
│   └── run.py
```

## Seguridad

- Las contraseñas se almacenan de forma segura usando hash
- Implementación de autenticación de dos factores (opcional)
- Cambio de contraseña obligatorio en el primer inicio de sesión
- Protección contra CSRF
- Validación de formularios
- Límite de tamaño para archivos subidos

## Contribuir

1. Hacer fork del repositorio
2. Crear una rama para la nueva característica (`git checkout -b feature/nueva-caracteristica`)
3. Hacer commit de los cambios (`git commit -am 'Agregar nueva característica'`)
4. Hacer push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

