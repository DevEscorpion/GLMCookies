# get_qwen_cookies_sin_captcha.py

import os
import json
import time
import uuid
from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURACIÓN ---
LOGIN_URL = "https://chat.qwen.ai/auth?action=signin"

# --- CREDENCIALES ---
# Para pruebas, las dejamos aquí. ¡No subas esto a un repositorio público!
# --- CREDENCIALES (desde variables de entorno) ---
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

if not USERNAME or not PASSWORD:
    raise RuntimeError("Faltan las variables de entorno del nombre y contraseña")

# --- OPCIONES DE CHROME ---
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument(f"--user-data-dir=/tmp/selenium_user_data_{uuid.uuid4()}")

print("Configuración de Selenium lista.")

driver = None
try:
    print("Inicializando el driver de Chrome...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)
    print("¡Driver inicializado correctamente!")

    # --- FLUJO DE LOGIN CORRECTO Y SIMPLIFICADO ---

    # PASO 1: Navegar a la página de login
    print(f"Navegando a {LOGIN_URL}...")
    driver.get(LOGIN_URL)
    print("Página cargada.")
    
    # PASO 2: Rellenar el campo de usuario (email)
    print("Buscando el campo de email...")
    user_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
    user_field.send_keys(USERNAME)
    print("Usuario introducido.")
    
    # PASO 3: Rellenar la contraseña
    print("Buscando el campo de contraseña...")
    # ¡SELECTOR MEJORADO! Usamos By.NAME que es mucho más fiable que el XPath absoluto.
    pass_field = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[3]/div[1]/div/div/form/div[2]/div[2]/span/input")))
    pass_field.send_keys(PASSWORD)
    print("Contraseña introducida.")

    # PASO 4: Hacer clic en el botón de "Iniciar sesión"
    print("Buscando el botón de 'Iniciar sesión'...")
    # ¡SELECTOR MEJORADO! Este XPath relativo es mucho más robusto.
    login_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[3]/div[1]/div/div/form/div[4]/button"))
    )
    login_button.click()
    print("Botón 'Iniciar sesión' presionado.")

    # PASO 5: LÓGICA DEL CAPTCHA ELIMINADA, COMO SOLICITASTE.
    # El script ahora asumirá que el login fue exitoso o que no se requirió captcha.
    print("Esperando confirmación de login en la página del chat...")

    # PASO 6: Esperar a que cargue la página principal del chat
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder*='How can I help you today?']")))
    print("✅ ¡Login exitoso! Se ha cargado la página principal del chat.")

    # PASO 7: Obtener y guardar las cookies
    cookies = driver.get_cookies()
    print(f"Se han obtenido {len(cookies)} cookies.")
    with open("cookies.json", "w") as f:
        json.dump(cookies, f, indent=4)
    print("Cookies guardadas exitosamente en 'cookies.json'.")


except Exception as e:
    print("\n--- ❌ OCURRIÓ UN ERROR DURANTE LA EJECUCIÓN ---")
    print(type(e).__name__, ":", e)
    if driver:
        driver.save_screenshot("runtime_error.png")
        print("Se ha guardado una captura de pantalla del error en 'runtime_error.png'.")

finally:
    if driver:
        print("Cerrando el driver de Selenium...")
        driver.quit()
        print("Driver cerrado.")
