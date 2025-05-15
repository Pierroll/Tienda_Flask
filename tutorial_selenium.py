from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep

def test_login_flow():
    # Configuración del navegador
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    
    # Inicializar el WebDriver de Chrome
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # 1. Navegar a la página principal
        driver.get("http://127.0.0.1:5000/")
        print("1. Navegando a la página principal...")
        
        # 2. Localizar y hacer clic en el botón de menú desplegable
        print("2. Buscando el botón de menú...")
        menu_button = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "dropdown-toggle"))
        )
        menu_button.click()
        print("   - Menú desplegable abierto")
        
        # 3. Hacer clic en la opción de Iniciar Sesión
        print("3. Buscando la opción de Iniciar Sesión...")
        login_option = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "dropdown-item"))
        )
        login_option.click()
        print("   - Navegando a la página de inicio de sesión")
        
        # 4. Verificar que estamos en la página de login
        wait.until(EC.title_contains("Iniciar Sesión"))
        print("4. Página de inicio de sesión cargada correctamente")
        
        # 5. Llenar el formulario de inicio de sesión
        print("5. Llenando credenciales...")
        
        # Esperar a que el formulario esté presente
        form = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        print("   - Formulario encontrado")
        
        # Encontrar los campos del formulario
        email = wait.until(
            EC.presence_of_element_located((By.ID, "email"))  # Buscar por ID
        )
        password = driver.find_element(By.ID, "password")  # Buscar por ID
        submit = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        
        print(f"   - Email field found: {email.is_displayed()}")
        print(f"   - Password field found: {password.is_displayed()}")
        print(f"   - Submit button found: {submit.is_displayed()}")
        
        # Desplazarse al campo de email para asegurar que sea visible
        driver.execute_script("arguments[0].scrollIntoView(true);", email)
        sleep(1)  # Pequeña pausa para asegurar el desplazamiento
        
        # Reemplaza estos valores con credenciales válidas
        email.clear()
        email.send_keys("admin@example.com")
        print("   - Email ingresado")
        
        password.clear()
        password.send_keys("password123")
        print("   - Contraseña ingresada")
        print("   - Credenciales ingresadas")
        
        # 6. Hacer clic en el botón de Iniciar Sesión
        print("6. Enviando formulario...")
        submit.click()
        
        # 7. Verificar redirección exitosa
        wait.until(EC.title_contains("Inicio"))
        print("7. Inicio de sesión exitoso")
        print(f"   - Página actual: {driver.current_url}")
        print(f"   - Título de la página: {driver.title}")
        
        # Mantener el navegador abierto por 5 segundos más
        sleep(5)
        
    except Exception as e:
        print(f"\n¡Error durante la prueba!")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        
        # Tomar captura de pantalla en caso de error
        driver.save_screenshot("error_login_test.png")
        print("Se ha guardado una captura de pantalla como 'error_login_test.png'")
        
    finally:
        # Cerrar el navegador
        print("\nFinalizando la prueba...")
        driver.quit()
        print("Prueba finalizada")

if __name__ == "__main__":
    test_login_flow()
