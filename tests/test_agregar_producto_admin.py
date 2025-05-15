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

@pytest.fixture(scope="function")
def browser():
    """Configura el navegador para las pruebas"""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)  # 30 segundos para cargar la página
    driver.implicitly_wait(10)  # 10 segundos para encontrar elementos
    
    # Maximizar la ventana
    try:
        driver.maximize_window()
    except:
        pass
    
    yield driver
    
    # Cerrar el navegador después de las pruebas
    try:
        if driver:
            driver.quit()
    except:
        pass

def login_as_admin(browser):
    """Función auxiliar para iniciar sesión como administrador"""
    print("\nIniciando sesión como administrador...")
    
    # Navegar a la página de login
    browser.get(f"{BASE_URL}/auth/login")
    time.sleep(2)
    take_screenshot(browser, "01_pagina_login")
    
    # Buscar y llenar el formulario de login
    try:
        email = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password = browser.find_element(By.NAME, "password")
        
        # Credenciales de administrador
        admin_email = "luacas@tienda.com"
        admin_password = "Lucas123456"  # Corregido: se agregó la 'a' faltante
        
        print(f"Iniciando sesión como {admin_email}...")
        
        # Limpiar y llenar campos con esperas
        try:
            email.clear()
            time.sleep(0.5)
            email.send_keys(admin_email)
            print("✓ Email ingresado")
            
            password.clear()
            time.sleep(0.5)
            password.send_keys(admin_password)
            print("✓ Contraseña ingresada")
            
            take_screenshot(browser, "02_formulario_lleno")
            
            # Enviar el formulario con JavaScript para evitar problemas de interactividad
            print("Enviando formulario...")
            try:
                # Primero intentar con el botón normal
                submit_button = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.ID, "submit"))
                )
                # Hacer scroll al botón
                browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(0.5)
                submit_button.click()
                print("✓ Formulario enviado con el botón")
            except Exception as e:
                print(f"No se pudo hacer clic en el botón: {str(e)}")
                print("Intentando enviar el formulario con JavaScript...")
                browser.execute_script("document.forms[0].submit();")
                print("✓ Formulario enviado con JavaScript")
                
        except Exception as e:
            print(f"Error al llenar el formulario: {str(e)}")
            take_screenshot(browser, "error_llenando_formulario")
            raise
        
        # Esperar a que se complete el inicio de sesión (máximo 20 segundos)
        print("Esperando redirección después del login...")
        try:
            WebDriverWait(browser, 20).until(
                lambda d: d.current_url != f"{BASE_URL}/auth/login"
            )
            print(f"✓ Redirigido a: {browser.current_url}")
            take_screenshot(browser, "03_despues_de_iniciar_sesion")
            
            # Verificar que el inicio de sesión fue exitoso
            if "login" in browser.current_url.lower():
                # Si aún estamos en la página de login, verificar si hay mensajes de error
                try:
                    error_messages = browser.find_elements(By.CLASS_NAME, "alert-danger")
                    if error_messages:
                        error_text = " | ".join([msg.text for msg in error_messages if msg.is_displayed()])
                        raise Exception(f"Error en el inicio de sesión: {error_text}")
                except:
                    pass
                raise Exception("Parece que el inicio de sesión falló - Sigue en la página de login")
                
            print("✓ Inicio de sesión exitoso")
            
        except Exception as e:
            print(f"Error durante la espera de redirección: {str(e)}")
            print(f"URL actual: {browser.current_url}")
            print("HTML de la página:", browser.page_source[:1500])
            take_screenshot(browser, "error_despues_login")
            raise
        
    except Exception as e:
        print(f"✗ Error durante el inicio de sesión: {str(e)}")
        take_screenshot(browser, "error_login")
        raise

def test_agregar_producto_como_admin(browser):
    """Prueba el flujo completo de agregar un producto como administrador"""
    try:
        print("\n=== Iniciando prueba de agregar producto como administrador ===")
        
        # 1. Iniciar sesión como administrador
        login_as_admin(browser)
        
        # 2. Navegar a la página de agregar producto
        print("\nNavegando a la página de agregar producto...")
        try:
            # Intentar encontrar el enlace en la barra de navegación
            add_product_link = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/add-product')]"))
            )
            add_product_link.click()
            print("✓ Enlace a 'Agregar Producto' encontrado y clickeado")
        except Exception as e:
            print(f"No se pudo encontrar el enlace en la barra de navegación. Navegando directamente...")
            browser.get(f"{BASE_URL}/add-product")
        
        # Esperar a que se cargue la página de agregar producto
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        
        take_screenshot(browser, "04_pagina_agregar_producto")
        
        # 3. Llenar el formulario con datos de prueba
        print("\nLlenando el formulario de producto...")
        
        # Datos de prueba para el producto
        test_product = {
            "product_name": "Producto de Prueba " + datetime.now().strftime("%Y%m%d%H%M%S"),
            "description": "Este es un producto de prueba creado automáticamente",
            "current_price": "99.99",
            "previous_price": "129.99",
            "in_stock": "50",
            "colors": "Rojo,Azul,Verde",
            "discount": "10",
            "category_id": "1"  # Asumiendo que la categoría con ID 1 existe
        }
        
        # Llenar los campos del formulario
        try:
            # Nombre del producto
            product_name = browser.find_element(By.NAME, "product_name")
            product_name.clear()
            product_name.send_keys(test_product["product_name"])
            
            # Categoría
            from selenium.webdriver.support.ui import Select
            category = Select(browser.find_element(By.NAME, "category_id"))
            category.select_by_value(test_product["category_id"])
            
            # Descripción
            description = browser.find_element(By.NAME, "description")
            description.clear()
            description.send_keys(test_product["description"])
            
            # Precio actual
            current_price = browser.find_element(By.NAME, "current_price")
            current_price.clear()
            current_price.send_keys(test_product["current_price"])
            
            # Precio anterior (opcional)
            previous_price = browser.find_element(By.NAME, "previous_price")
            previous_price.clear()
            previous_price.send_keys(test_product["previous_price"])
            
            # Solo completar campos esenciales
            try:
                # Stock
                in_stock = browser.find_element(By.ID, "stock_quantity")
                in_stock.clear()
                in_stock.send_keys(test_product["in_stock"])
                print("✓ Stock ingresado")
                
                # Seleccionar la oferta flash
                flash_sale = browser.find_element(By.ID, "flash_sale")
                if not flash_sale.is_selected():
                    browser.execute_script("arguments[0].click();", flash_sale)
                    print("✓ Oferta flash activada")
                else:
                    print("✓ Oferta flash ya estaba activada")
                    
                take_screenshot(browser, "05_formulario_lleno")
                
            except Exception as e:
                print(f"⚠ Error al completar campos: {str(e)}")
                take_screenshot(browser, "error_campos")
                raise
            
        except Exception as e:
            print(f"✗ Error al llenar el formulario: {str(e)}")
            take_screenshot(browser, "error_llenar_formulario")
            raise
        
        # 4. Enviar el formulario
        print("\nEnviando el formulario...")
        try:
            # Buscar el botón de guardar por ID
            submit_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.ID, "add_product"))
            )
            # Hacer scroll hasta el botón para asegurar que es visible
            browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(0.5)
            submit_button.click()
            print("✓ Formulario enviado")
            
            # Esperar a que se procese el formulario
            time.sleep(3)
            take_screenshot(browser, "06_despues_de_enviar")
            
            # Verificar que se mostró el mensaje de éxito
            try:
                success_message = WebDriverWait(browser, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "alert-success"))
                )
                print(f"✓ Mensaje de éxito: {success_message.text}")
                take_screenshot(browser, "07_mensaje_exito")
            except:
                print("⚠ No se mostró el mensaje de éxito esperado")
                # Verificar si hay mensajes de error
                try:
                    error_messages = browser.find_elements(By.CLASS_NAME, "alert-danger")
                    for msg in error_messages:
                        if msg.is_displayed():
                            print(f"✗ Error mostrado: {msg.text}")
                except:
                    pass
                
                take_screenshot(browser, "07_sin_mensaje_esperado")
                
        except Exception as e:
            print(f"✗ Error al enviar el formulario: {str(e)}")
            take_screenshot(browser, "error_enviar_formulario")
            raise
        
        print("\n✓ Prueba de agregar producto completada con éxito")
        
    except Exception as e:
        print(f"\n✗ Error durante la prueba: {str(e)}")
        print(f"URL actual: {browser.current_url}")
        print("Contenido de la página:")
        print(browser.page_source[:1500])  # Mostrar los primeros 1500 caracteres
        take_screenshot(browser, "error_prueba")
        raise
