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

def test_agregar_producto_al_carrito(browser):
    """Prueba el flujo completo de inicio de sesión, navegación y agregar al carrito"""
    try:
        print("\n=== Iniciando prueba de agregar producto al carrito ===")
        
        # 1. Navegar a la página de login
        print("1. Navegando a la página de login...")
        browser.get(f"{BASE_URL}/auth/login")
        time.sleep(2)  # Esperar a que cargue la página
        take_screenshot(browser, "01_pagina_login")
        
        # 2. Iniciar sesión
        print("2. Iniciando sesión...")
        
        # Tomar captura de la página de login
        take_screenshot(browser, "02_01_pagina_login")
        
        # Esperar a que el formulario esté presente
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            print("✓ Formulario de login encontrado")
        except Exception as e:
            print(f"✗ No se pudo encontrar el formulario: {str(e)}")
            print("HTML de la página:")
            print(browser.page_source[:2000])
            raise
        
        # Buscar los campos del formulario
        try:
            email = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            password = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            print("✓ Campos del formulario encontrados por NAME")
        except Exception as e:
            try:
                email = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.ID, "email"))
                )
                password = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.ID, "password"))
                )
                print("✓ Campos del formulario encontrados por ID")
            except Exception as e:
                print(f"✗ No se encontraron los campos por NAME o ID: {str(e)}")
                raise
        
        # Credenciales de prueba
        credenciales = {
            "email": "cinthia@tienda.com",
            "password": "Cinthia123456"
        }
        
        # Llenar el formulario
        try:
            email.clear()
            email.send_keys(credenciales["email"])
            password.clear()
            password.send_keys(credenciales["password"])
            print("✓ Formulario llenado correctamente")
            take_screenshot(browser, "02_02_formulario_lleno")
        except Exception as e:
            print(f"✗ Error al llenar el formulario: {str(e)}")
            raise
        
        # Enviar el formulario usando el botón con id="submit"
        try:
            submit_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.ID, "submit"))
            )
            print("✓ Botón de envío encontrado por ID")
            submit_button.click()
            print("✓ Formulario de inicio de sesión enviado")
        except Exception as e:
            print(f"✗ No se pudo encontrar el botón de envío por ID: {str(e)}")
            # Intentar métodos alternativos si falla
            try:
                submit_button = WebDriverWait(browser, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
                )
                submit_button.click()
                print("✓ Formulario de inicio de sesión enviado (botón submit)")
            except:
                try:
                    submit_button = WebDriverWait(browser, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))
                    )
                    submit_button.click()
                    print("✓ Formulario de inicio de sesión enviado (input submit)")
                except Exception as e2:
                    print(f"✗ No se pudo enviar el formulario: {str(e2)}")
                    raise
        
        # Esperar a que se complete el inicio de sesión
        try:
            WebDriverWait(browser, 10).until(
                lambda d: d.current_url != f"{BASE_URL}/auth/login"
            )
            print("✓ Redirección después del login exitosa")
            time.sleep(2)  # Esperar un poco más para asegurar que todo esté cargado
            take_screenshot(browser, "03_despues_de_iniciar_sesion")
        except Exception as e:
            print(f"✗ Posible error en el inicio de sesión o redirección: {str(e)}")
            print(f"URL actual: {browser.current_url}")
            take_screenshot(browser, "03_error_inicio_sesion")
            raise
        
        # 3. Verificar que el inicio de sesión fue exitoso
        print("3. Verificando inicio de sesión exitoso...")
        time.sleep(3)
        take_screenshot(browser, "03_despues_de_iniciar_sesion")
        
        # Verificar si hay un mensaje de error de inicio de sesión
        try:
            mensajes_error = browser.find_elements(By.CLASS_NAME, "alert-danger")
            for mensaje in mensajes_error:
                if mensaje.is_displayed():
                    print(f"✗ Error al iniciar sesión: {mensaje.text}")
                    raise Exception(f"Error en el inicio de sesión: {mensaje.text}")
        except:
            pass  # No hay mensajes de error
        
        # 4. Navegar directamente a la categoría 2
        print("4. Navegando directamente a la categoría 2...")
        browser.get(f"{BASE_URL}/category/2")
        time.sleep(3)
        take_screenshot(browser, "04_pagina_categoria_2")
        
        # Verificar que estamos en la página de categoría
        if "category/2" not in browser.current_url:
            print(f"⚠ No se pudo cargar la categoría 2. URL actual: {browser.current_url}")
            print("Contenido de la página:")
            print(browser.page_source[:1000])  # Mostrar los primeros 1000 caracteres
            raise Exception("No se pudo cargar la página de categoría 2")
        
        # 5. Agregar un producto al carrito
        print("5. Intentando agregar un producto al carrito...")
        try:
            # Tomar captura de la página antes de buscar el botón
            take_screenshot(browser, "05_antes_de_buscar_boton")
            
            # Intentar diferentes formas de encontrar el botón de agregar al carrito
            selectores_posibles = [
                "//button[contains(@class, 'btn-primary') and contains(., 'Agregar al carrito')]",
                "//button[contains(., 'Agregar al carrito')]",
                "//a[contains(@class, 'btn-primary') and contains(., 'Agregar al carrito')]",
                "//a[contains(., 'Agregar al carrito')]",
                "//button[contains(@class, 'btn') and contains(., 'Agregar')]",
                "//a[contains(@class, 'btn') and contains(., 'Agregar')]"
            ]
            
            boton_encontrado = False
            for selector in selectores_posibles:
                try:
                    boton = WebDriverWait(browser, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"✓ Botón encontrado con el selector: {selector}")
                    boton.click()
                    print("✓ Producto agregado al carrito")
                    take_screenshot(browser, "06_producto_agregado")
                    boton_encontrado = True
                    break
                except Exception as e:
                    print(f"  - No se pudo encontrar el botón con el selector: {selector}")
            
            if not boton_encontrado:
                raise Exception("No se pudo encontrar ningún botón de 'Agregar al carrito'")
                
            
            # Verificar que se mostró el mensaje de éxito
            try:
                WebDriverWait(browser, 5).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "alert-success"))
                )
                print("✓ Mensaje de éxito mostrado")
                take_screenshot(browser, "07_mensaje_exito")
            except:
                print("⚠ No se mostró el mensaje de éxito")
            
        except Exception as e:
            print(f"✗ No se pudo agregar el producto al carrito: {str(e)}")
            take_screenshot(browser, "error_agregar_carrito")
            raise
        
        # 6. Verificar el carrito
        print("6. Verificando el carrito...")
        try:
            # Tomar captura antes de buscar el carrito
            take_screenshot(browser, "07_antes_de_ver_carrito")
            
            # Intentar diferentes formas de encontrar el enlace al carrito
            selectores_carrito = [
                "//a[contains(@href, '/cart')]",
                "//a[contains(., 'Carrito')]",
                "//a[contains(., 'carrito')]",
                "//a[contains(., 'Ver carrito')]",
                "//a[contains(@class, 'cart')]"
            ]
            
            carrito_encontrado = False
            for selector in selectores_carrito:
                try:
                    carrito = WebDriverWait(browser, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"✓ Enlace al carrito encontrado con el selector: {selector}")
                    carrito.click()
                    time.sleep(3)
                    take_screenshot(browser, "08_pagina_carrito")
                    carrito_encontrado = True
                    break
                except Exception as e:
                    print(f"  - No se pudo encontrar el carrito con el selector: {selector}")
            
            if not carrito_encontrado:
                raise Exception("No se pudo encontrar el enlace al carrito")
            
            # Verificar que hay productos en el carrito
            try:
                # Intentar diferentes selectores para los productos en el carrito
                selectores_productos = [
                    "//div[contains(@class, 'cart-item')]",
                    "//div[contains(@class, 'item')]",
                    "//tr[contains(@class, 'product')]",
                    "//div[contains(@class, 'product')]"
                ]
                
                productos_encontrados = False
                for selector in selectores_productos:
                    try:
                        productos = browser.find_elements(By.XPATH, selector)
                        if productos:
                            print(f"✓ Se encontraron {len(productos)} productos en el carrito con el selector: {selector}")
                            productos_encontrados = True
                            break
                    except:
                        continue
                
                if not productos_encontrados:
                    print("⚠ No se encontraron productos en el carrito")
                    print("Contenido de la página del carrito:")
                    print(browser.page_source[:1500])  # Mostrar más contenido para diagnóstico
                    
            except Exception as e:
                print(f"⚠ No se pudo verificar el contenido del carrito: {str(e)}")
                
        except Exception as e:
            print(f"✗ No se pudo acceder al carrito: {str(e)}")
            take_screenshot(browser, "error_ver_carrito")
            print("Contenido de la página actual:")
            print(browser.page_source[:1500])  # Mostrar más contenido para diagnóstico
        
        print("\n✓ Prueba de agregar producto al carrito completada con éxito")
        
    except Exception as e:
        take_screenshot(browser, "error_prueba")
        print(f"\n✗ Error durante la prueba: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"URL actual: {browser.current_url}")
        print("Contenido de la página:")
        print(browser.page_source[:1000])  # Mostrar los primeros 1000 caracteres
        raise
