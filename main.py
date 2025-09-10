# guardar_cookies_turso.py
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import libsql_experimental as libsql

# Configuración de Turso
TURSO_URL = "libsql://longcatcookies-srescorpiondev.aws-us-east-2.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NTY4NDE0MDAsImlkIjoiZmIwYWQ2NmYtODIwYS00ODAwLWE3YWEtNjkzNTg2YmRhOWZhIiwicmlkIjoiZGRkNDY1NjAtNTEzNi00NDFiLWEzMzUtMmEwOGEyODA5YThmIn0.McKM9wwLkQakWypS2GSScQ3jSURzpB3ZlRrAJpSxQli47cL4Sn2Iac-TenVhMRDufm5KYEDJ84fFeIfa1JR0Cg"

def init_turso_database():
    """Inicializa la base de datos Turso y maneja migraciones"""
    try:
        conn = libsql.connect(TURSO_URL, auth_token=TURSO_TOKEN)
        cursor = conn.cursor()
        
        # Limpiar tablas temporales que puedan existir de migraciones fallidas
        try:
            cursor.execute("DROP TABLE IF EXISTS cookies_new")
        except:
            pass  # Ignorar errores si la tabla no existe
        
        # Verificar si la tabla cookies existe y su estructura
        cursor.execute("PRAGMA table_info(cookies)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns] if columns else []
        
        # Crear tabla si no existe
        if not columns:
            cursor.execute('''
                CREATE TABLE cookies (
                    id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
                    cookie_str TEXT,
                    timestamp TEXT DEFAULT (datetime('now')),
                    todas_cookies TEXT,
                    updated_at TEXT DEFAULT (datetime('now'))
                )
            ''')
            print("✅ Tabla cookies creada con estructura nueva")
        else:
            # Verificar si hay registros con id ≠ 1 y corregirlos
            cursor.execute('SELECT id FROM cookies WHERE id != 1')
            invalid_ids = cursor.fetchall()
            
            if invalid_ids:
                print(f"🔄 Corrigiendo {len(invalid_ids)} registros con ID incorrecto...")
                # Eliminar registros con ID incorrecto (debería haber solo uno con id=1)
                cursor.execute('DELETE FROM cookies WHERE id != 1')
            
            # Migrar tabla existente si falta la columna updated_at
            if 'updated_at' not in column_names:
                print("🔄 Migrando tabla existente...")
                
                # Crear tabla temporal con nueva estructura
                cursor.execute('''
                    CREATE TABLE cookies_new (
                        id INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
                        cookie_str TEXT,
                        timestamp TEXT DEFAULT (datetime('now')),
                        todas_cookies TEXT,
                        updated_at TEXT DEFAULT (datetime('now'))
                    )
                ''')
                
                # Copiar datos existentes (solo el registro con id=1 si existe)
                cursor.execute('SELECT id, cookie_str, timestamp, todas_cookies FROM cookies WHERE id = 1')
                existing_data = cursor.fetchone()
                
                if existing_data:
                    cursor.execute('''
                        INSERT INTO cookies_new (id, cookie_str, timestamp, todas_cookies, updated_at)
                        VALUES (1, ?, ?, ?, datetime('now'))
                    ''', (existing_data[1], existing_data[2], existing_data[3]))
                
                # Eliminar tabla vieja y renombrar nueva
                cursor.execute('DROP TABLE cookies')
                cursor.execute('ALTER TABLE cookies_new RENAME TO cookies')
                print("✅ Tabla migrada exitosamente")
        
        # Crear tabla para logs si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT (datetime('now')),
                status TEXT,
                message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de datos Turso inicializada y verificada")
        return True
    except Exception as e:
        print(f"❌ Error inicializando Turso: {e}")
        import traceback
        traceback.print_exc()
        return False

def limpiar_tablas_temporales():
    """Limpia tablas temporales que puedan existir por migraciones fallidas"""
    try:
        conn = libsql.connect(TURSO_URL, auth_token=TURSO_TOKEN)
        cursor = conn.cursor()
        
        # Lista de tablas temporales a limpiar
        tablas_temporales = ['cookies_new', 'cookies_old', 'cookies_backup']
        
        for tabla in tablas_temporales:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {tabla}")
                print(f"🧹 Tabla temporal {tabla} limpiada")
            except:
                pass  # Ignorar errores si la tabla no existe
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️  Advertencia limpiando tablas temporales: {e}")
        return False

def guardar_en_turso(cookie_str, todas_cookies):
    """Guarda o actualiza las cookies en la base de datos Turso"""
    try:
        conn = libsql.connect(TURSO_URL, auth_token=TURSO_TOKEN)
        cursor = conn.cursor()
        
        # Verificar estructura de la tabla
        cursor.execute("PRAGMA table_info(cookies)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Verificar si ya existe un registro
        cursor.execute('SELECT COUNT(*) FROM cookies WHERE id = 1')
        count = cursor.fetchone()[0]
        
        if count > 0:
            # Actualizar registro existente
            if 'updated_at' in column_names:
                cursor.execute('''
                    UPDATE cookies 
                    SET cookie_str = ?, todas_cookies = ?, timestamp = datetime('now'), updated_at = datetime('now')
                    WHERE id = 1
                ''', (cookie_str, json.dumps(todas_cookies) if todas_cookies else None))
            else:
                cursor.execute('''
                    UPDATE cookies 
                    SET cookie_str = ?, todas_cookies = ?, timestamp = datetime('now')
                    WHERE id = 1
                ''', (cookie_str, json.dumps(todas_cookies) if todas_cookies else None))
            print("✅ Cookie actualizada en Turso")
        else:
            # Insertar nuevo registro
            if 'updated_at' in column_names:
                cursor.execute('''
                    INSERT INTO cookies (id, cookie_str, todas_cookies)
                    VALUES (1, ?, ?)
                ''', (cookie_str, json.dumps(todas_cookies) if todas_cookies else None))
            else:
                cursor.execute('''
                    INSERT INTO cookies (id, cookie_str, todas_cookies)
                    VALUES (1, ?, ?)
                ''', (cookie_str, json.dumps(todas_cookies) if todas_cookies else None))
            print("✅ Nueva cookie guardada en Turso")
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error guardando/actualizando en Turso: {e}")
        import traceback
        traceback.print_exc()
        return False

def obtener_ultima_cookie_turso():
    """Obtiene la última cookie guardada de Turso"""
    try:
        conn = libsql.connect(TURSO_URL, auth_token=TURSO_TOKEN)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cookie_str, timestamp 
            FROM cookies 
            WHERE id = 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0], result[1]
        return None, None
    except Exception as e:
        print(f"❌ Error obteniendo cookie de Turso: {e}")
        return None, None

def mostrar_estado_base_datos():
    """Muestra el estado actual de la base de datos"""
    try:
        conn = libsql.connect(TURSO_URL, auth_token=TURSO_TOKEN)
        cursor = conn.cursor()
        
        # Verificar estructura de la tabla cookies
        cursor.execute("PRAGMA table_info(cookies)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Contar registros en cookies
        cursor.execute('SELECT COUNT(*) FROM cookies')
        count_cookies = cursor.fetchone()[0]
        
        # Verificar registros con ID incorrecto
        cursor.execute('SELECT COUNT(*) FROM cookies WHERE id != 1')
        invalid_ids = cursor.fetchone()[0]
        
        # Contar registros en logs
        cursor.execute('SELECT COUNT(*) FROM logs')
        count_logs = cursor.fetchone()[0]
        
        # Obtener info de la cookie actual
        cursor.execute('SELECT cookie_str, timestamp FROM cookies WHERE id = 1')
        cookie_info = cursor.fetchone()
        
        conn.close()
        
        print(f"\n📊 ESTADO DE LA BASE DE DATOS:")
        print(f"   • Estructura tabla cookies: {column_names}")
        print(f"   • Registros en tabla cookies: {count_cookies}")
        print(f"   • Registros con ID incorrecto: {invalid_ids}")
        print(f"   • Registros en tabla logs: {count_logs}")
        
        if cookie_info:
            if cookie_info[0]:
                print(f"   • Cookie actual: EXISTE (última actualización: {cookie_info[1]})")
            else:
                print(f"   • Cookie actual: REGISTRO VACÍO")
        else:
            print(f"   • Cookie actual: NO EXISTE")
            
    except Exception as e:
        print(f"❌ Error mostrando estado de BD: {e}")

def limpiar_logs_antiguos():
    """Limpia logs antiguos (mantiene solo los últimos 100 registros)"""
    try:
        conn = libsql.connect(TURSO_URL, auth_token=TURSO_TOKEN)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM logs 
            WHERE id NOT IN (
                SELECT id FROM logs 
                ORDER BY timestamp DESC 
                LIMIT 100
            )
        ''')
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            print(f"🗑️  Se eliminaron {deleted_count} logs antiguos")
            
    except Exception as e:
        print(f"❌ Error limpiando logs: {e}")

def log_action_turso(status, message):
    """Guarda log de acciones en Turso"""
    try:
        conn = libsql.connect(TURSO_URL, auth_token=TURSO_TOKEN)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs (status, message)
            VALUES (?, ?)
        ''', (status, message))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Error en log Turso: {e}")

def obtener_cookies_reales():
    """Obtiene cookies reales de longcat.chat/t"""
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = None
    try:
        print("🚀 Iniciando Chrome...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("🌐 Navegando a https://longcat.chat/t...")
        driver.get("https://longcat.chat/t")
        
        print("⏳ Esperando carga completa (10 segundos)...")
        time.sleep(10)
        
        # Obtener cookies
        cookies = driver.get_cookies()
        
        # Buscar cookies específicas
        target_cookies = {}
        for cookie in cookies:
            if cookie['name'] in ['_lxsdk_cuid', '_lxsdk_s']:
                target_cookies[cookie['name']] = cookie['value']
        
        if '_lxsdk_cuid' in target_cookies and '_lxsdk_s' in target_cookies:
            cookie_str = f'_lxsdk_cuid={target_cookies["_lxsdk_cuid"]}; _lxsdk_s={target_cookies["_lxsdk_s"]}'
            return cookie_str, cookies
        else:
            return None, cookies
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, []
        
    finally:
        if driver:
            driver.quit()

def main():
    """Función principal"""
    print("=== ACTUALIZACIÓN SEMANAL DE COOKIES EN TURSO ===")
    print("=== longcat.chat/t ===\n")
    
    # Limpiar tablas temporales primero
    print("🧹 Limpiando tablas temporales...")
    limpiar_tablas_temporales()
    
    # Mostrar estado actual de la base de datos
    mostrar_estado_base_datos()
    
    # Inicializar base de datos Turso (con manejo de migraciones)
    if not init_turso_database():
        print("❌ No se pudo conectar a Turso")
        return
    
    # Obtener cookies
    print("\n🔄 Obteniendo nuevas cookies...")
    cookie_str, todas_cookies = obtener_cookies_reales()
    
    if cookie_str:
        print(f"\n🎯 NUEVAS COOKIES OBTENIDAS:")
        print(f'COOKIE_STR = "{cookie_str}"')
        
        # Obtener cookie anterior para mostrar comparación
        cookie_anterior, fecha_anterior = obtener_ultima_cookie_turso()
        
        if cookie_anterior:
            print(f"📅 Cookie anterior: {fecha_anterior}")
        
        # Siempre guardar/actualizar en Turso
        if guardar_en_turso(cookie_str, todas_cookies):
            log_action_turso("SUCCESS", "Cookie actualizada correctamente (ejecución semanal)")
            print("✅ Cookie actualizada exitosamente")
            
            # Mostrar nueva fecha de actualización
            nueva_cookie, nueva_fecha = obtener_ultima_cookie_turso()
            print(f"📅 Nueva fecha de actualización: {nueva_fecha}")
        else:
            log_action_turso("ERROR", "Error actualizando cookie en Turso")
            print("❌ Error actualizando en Turso")
        
        # Limpiar logs antiguos
        limpiar_logs_antiguos()
        
        # Mostrar estado final
        mostrar_estado_base_datos()
            
    else:
        print("❌ No se pudieron obtener las cookies")
        log_action_turso("ERROR", "No se pudieron obtener las cookies específicas")
        
        # Guardar intento fallido (pero mantener registro de que se intentó)
        guardar_en_turso(None, todas_cookies)

if __name__ == "__main__":
    main()
