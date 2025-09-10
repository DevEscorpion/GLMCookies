# test_turso.py
import libsql_experimental as libsql

TURSO_URL = "libsql://longcatcookies-srescorpiondev.aws-us-east-2.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NTY4NDE0MDAsImlkIjoiZmIwYWQ2NmYtODIwYS00ODAwLWE3YWEtNjkzNTg2YmRhOWZhIiwicmlkIjoiZGRkNDY1NjAtNTEzNi00NDFiLWEzMzUtMmEwOGEyODA5YThmIn0.McKM9wwLkQakWypS2GSScQ3jSURzpB3ZlRrAJpSxQli47cL4Sn2Iac-TenVhMRDufm5KYEDJ84fFeIfa1JR0Cg"

def test_connection():
    try:
        print("🔍 Probando conexión a Turso...")
        conn = libsql.connect(TURSO_URL, auth_token=TURSO_TOKEN)
        cursor = conn.cursor()
        
        # Ejecutar una consulta simple
        cursor.execute("SELECT 'Conexión exitosa' as result")
        result = cursor.fetchone()
        print(f"✅ {result[0]}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_connection()
