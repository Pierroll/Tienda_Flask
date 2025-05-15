import os
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
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    yield driver
    
    # Cerrar el navegador después de las pruebas
    driver.quit()

def test_login_exitoso(browser):
    """Prueba el inicio de sesión exitoso"""
    try:
        print("\n=== Iniciando prueba de inicio de sesión exitoso ===")
        
        # 1. Navegar a la página de login
        print("1. Navegando a la página de login...")
        browser.get(f"{BASE_URL}/auth/login")
        take_screenshot(browser, "01_pagina_login")
        
        # 2. Verificar que estamos en la página correcta
        assert "login" in browser.current_url.lower() or "iniciar" in browser.title.lower()
        print("✓ Página de login cargada correctamente")
        
        # 3. Llenar el formulario con credenciales válidas
        print("2. Rellenando formulario con credenciales válidas...")
        email = browser.find_element(By.ID, "email")
        password = browser.find_element(By.ID, "password")
        submit = browser.find_element(By.XPATH, "//button[@type='submit']")
        
        # Usar credenciales de prueba desde variables de entorno o valores predeterminados
        import os
        test_email = os.getenv('TEST_EMAIL', 'test@example.com')
        test_password = os.getenv('TEST_PASSWORD', 'password123')
        
        credenciales = {
            "email": test_email,
            "password": test_password
        }
        
        email.clear()
        email.send_keys(credenciales["email"])
        password.clear()
        password.send_keys(credenciales["password"])
        
        take_screenshot(browser, "02_formulario_lleno")
        
        # 4. Enviar el formulario
        print("3. Enviando formulario...")
        submit.click()
        
        # 5. Verificar inicio de sesión exitoso
        print("4. Verificando inicio de sesión exitoso...")
        try:
            # Esperar a que se redirija después del login exitoso
            WebDriverWait(browser, 10).until(
                lambda d: d.current_url != f"{BASE_URL}/auth/login"
            )
            
            # Verificar que estamos en la página de inicio (root URL)
            assert browser.current_url.rstrip('/') == f"{BASE_URL}" or "home" in browser.current_url.lower()
            print("✓ Redirección exitosa después del login")
            take_screenshot(browser, "03_despues_login")
            
            # Verificar que se muestra el mensaje de bienvenida o el nombre de usuario
            try:
                welcome_message = WebDriverWait(browser, 5).until(
                    EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Bienvenido') or contains(text(), 'Welcome') or contains(@class, 'welcome')]"))
                )
                print(f"✓ Mensaje de bienvenida mostrado: {welcome_message.text}")
            except:
                print("⚠ No se encontró mensaje de bienvenida, pero el login fue exitoso")
            
        except Exception as e:
            take_screenshot(browser, "error_verificacion")
            print("⚠ No se pudo verificar el inicio de sesión exitoso:", str(e))
            raise
            
        print("✓ Prueba de inicio de sesión exitoso completada con éxito")
        
    except Exception as e:
        take_screenshot(browser, "error_prueba")
        print(f"✗ Error durante la prueba: {str(e)}")
        raise
