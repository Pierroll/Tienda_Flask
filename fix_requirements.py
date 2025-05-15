import subprocess
import sys
import os

def run_command(command):
    print(f"Ejecutando: {command}")
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)
    return result.returncode == 0

def main():
    print("=== Solución de compatibilidad para Python 3.13 ===")
    
    # 1. Actualizar pip
    print("\n1. Actualizando pip...")
    run_command(f"{sys.executable} -m pip install --upgrade pip")
    
    # 2. Crear una copia de seguridad del requirements.txt actual
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            original_requirements = f.read()
        with open("requirements.txt.bak", "w") as f:
            f.write(original_requirements)
        print("\n2. Se creó una copia de seguridad: requirements.txt.bak")
    
    # 3. Instalar las versiones compatibles con Python 3.13
    print("\n3. Instalando versiones compatibles...")
    
    # Lista de paquetes con versiones compatibles
    packages = [
        "Flask==3.0.2",
        "Flask-SQLAlchemy==3.1.1",
        "Flask-Login==0.6.3",
        "Flask-WTF==1.2.1",
        "Werkzeug==3.0.1",
        "SQLAlchemy==2.0.40",  # Versión más reciente con soporte para Python 3.13
        "email-validator==2.1.0.post1",
        "Pillow==11.2.1",
        "python-dotenv==1.0.1",
        "WTForms==3.1.2",
        "Flask-Mail==0.9.1",
        "itsdangerous==2.1.2",
        "selenium==4.15.2",
        "pytest==8.0.0",
        "webdriver-manager==4.0.1",
        "greenlet>=3.0.0"  # Requerido por SQLAlchemy 2.0.40
    ]
    
    # Instalar cada paquete individualmente
    for package in packages:
        if not run_command(f"{sys.executable} -m pip install --upgrade {package}"):
            print(f"Error al instalar {package}")
    
    # 4. Actualizar el archivo requirements.txt
    with open("requirements.txt", "w") as f:
        f.write("\n".join(packages))
    
    print("\n4. Proceso completado. Intenta ejecutar tu aplicación nuevamente.")
    print("Si el problema persiste, considera usar Python 3.10 o 3.11.")

if __name__ == "__main__":
    main()
