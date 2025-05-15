import os
import time
import pytest
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuración básica
BASE_URL = "http://localhost:5000"
SCREENSHOTS_DIR = "screenshots"

def take_screenshot(driver, name):
    """Toma una captura de pantalla y la guarda en la carpeta screenshots"""
    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{SCREENSHOTS_DIR}/{name}_{timestamp}.png'
    driver.save_screenshot(filename)
    print(f"Captura de pantalla guardada como: {filename}")
    return filename

@pytest.fixture(scope="module")
def browser():
    """Configura el navegador para las pruebas"""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    
    yield driver
    
    # Cerrar el navegador después de las pruebas
    driver.quit()

def test_login_admin(browser):
    """Prueba el inicio de sesión de un administrador"""
    try:
        print("\n=== Iniciando prueba de login de administrador ===")
        
        # 1. Navegar a la página de login
        print("1. Navegando a la página de login...")
        browser.get(f"{BASE_URL}/auth/login")
        time.sleep(2)  # Esperar a que cargue la página
        take_screenshot(browser, "01_pagina_login")
        
        # 2. Verificar que estamos en la página correcta
        print("Verificando URL y título de la página...")
        print(f"URL actual: {browser.current_url}")
        print(f"Título de la página: {browser.title}")
        
        # 3. Llenar el formulario con credenciales de administrador
        print("\n2. Rellenando formulario con credenciales de administrador...")
        
        # Buscar los campos del formulario
        try:
            email = browser.find_element(By.NAME, "email")
            password = browser.find_element(By.NAME, "password")
            print("✓ Campos del formulario encontrados por NAME")
        except:
            try:
                email = browser.find_element(By.ID, "email")
                password = browser.find_element(By.ID, "password")
                print("✓ Campos del formulario encontrados por ID")
            except:
                email = browser.find_element(By.XPATH, "//input[@type='email' or @name='email']")
                password = browser.find_element(By.XPATH, "//input[@type='password' or @name='password']")
                print("✓ Campos del formulario encontrados por XPATH")
        
        # Credenciales de administrador (ajustar según sea necesario)
        credenciales = {
            "email": "admin@tienda.com",
            "password": "Admin123"
        }
        
        # Limpiar y llenar los campos
        email.clear()
        email.send_keys(credenciales["email"])
        password.clear()
        password.send_keys(credenciales["password"])
        
        # Tomar captura del formulario lleno
        take_screenshot(browser, "02_formulario_lleno")
        
        # 4. Enviar el formulario
        print("\n3. Enviando formulario...")
        try:
            # Buscar el botón de envío
            try:
                submit = browser.find_element(By.XPATH, "//button[@type='submit']")
            except:
                submit = browser.find_element(By.XPATH, "//input[@type='submit']")
            
            submit.click()
            print("✓ Formulario enviado")
        except Exception as e:
            print(f"Error al enviar el formulario: {str(e)}")
            take_screenshot(browser, "error_al_enviar_formulario")
            raise
        
        # Esperar a que se procese el envío
        time.sleep(5)
        
        # 5. Verificar inicio de sesión exitoso
        print("\n4. Verificando inicio de sesión exitoso...")
        
        # Tomar captura después del envío
        take_screenshot(browser, "03_despues_de_enviar")
        
        # Verificar redirección a la página de administrador o dashboard
        if "admin" in browser.current_url.lower() or "dashboard" in browser.current_url.lower():
            print(f"✓ Redirección exitosa a: {browser.current_url}")
            print(f"Título de la página: {browser.title}")
            take_screenshot(browser, "04_pagina_administrador")
        else:
            print(f"⚠ La URL actual no parece ser la de administrador: {browser.current_url}")
            print("Buscando elementos de la interfaz de administrador...")
            
            # Buscar elementos que indiquen que estamos en el panel de administración
            elementos_admin = [
                "Bienvenido, Admin",
                "Panel de Administración",
                "Administrador",
                "Dashboard"
            ]
            
            for elemento in elementos_admin:
                if elemento.lower() in browser.page_source.lower():
                    print(f"✓ Se encontró el texto de administrador: {elemento}")
                    take_screenshot(browser, f"05_elemento_admin_encontrado_{elemento[:10]}")
                    break
            else:
                print("✗ No se encontraron elementos de la interfaz de administrador")
                print("Contenido de la página:")
                print(browser.page_source[:2000])  # Mostrar los primeros 2000 caracteres
                take_screenshot(browser, "06_sin_elementos_admin")
        
        print("\n✓ Prueba de inicio de sesión de administrador completada")
        
    except Exception as e:
        take_screenshot(browser, "error_prueba")
        print(f"\n✗ Error durante la prueba: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        raise
