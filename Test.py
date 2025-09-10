from playwright.sync_api import sync_playwright
import time
import random

def move_slider_human_like(url):
    with sync_playwright() as p:
        # Configurar el navegador en modo headless
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = context.new_page()
        
        # Navegar a la página
        page.goto(url)
        
        # Esperar a que el deslizador esté visible usando el selector proporcionado
        slider = page.locator('//*[@id="aliyunCaptcha-sliding-slider"]')
        slider.wait_for(state="visible", timeout=15000)
        
        # Obtener las dimensiones del deslizador
        box = slider.bounding_box()
        if not box:
            raise Exception("No se pudo obtener el bounding box del deslizador")
        
        # Calcular el punto central del deslizador
        start_x = box['x'] + box['width'] / 2
        start_y = box['y'] + box['height'] / 2
        
        # Simular movimiento humano con arrastre no lineal
        page.mouse.move(start_x, start_y)
        page.mouse.down()
        
        # Mover en varios pasos con pausas para simular comportamiento humano
        steps = [
            (start_x + 50, start_y, 100),
            (start_x + 100, start_y, 150),
            (start_x + 150, start_y, 100),
            (start_x + 200, start_y, 200),
            (start_x + 250, start_y, 150)
        ]
        
        for step_x, step_y, pause in steps:
            page.mouse.move(step_x, step_y)
            time.sleep(pause / 1000)  # Convertir ms a segundos
        
        # Soltar el mouse
        page.mouse.up()
        
        # Esperar a que se complete la acción
        page.wait_for_timeout(3000)
        
        # Tomar una captura de pantalla para verificación
        page.screenshot(path="slider_result.png")
        
        # Cerrar el navegador
        browser.close()

if __name__ == "__main__":
    # Reemplaza con la URL real
    url = "https://chat.z.ai/auth"
    move_slider_human_like(url)
