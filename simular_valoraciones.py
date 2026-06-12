"""
Simulacion de 12 valoraciones deportivas para el deportista 10025735
Cada valoracion tiene 3 medidas (detalles)
Fechas distribuidas en los ultimos 12 meses
"""
import sys
sys.path.insert(0, r'C:\Users\fralm\Desktop\Opencode_SomatoCarta')

import requests
from datetime import datetime, timedelta
from src.backend.database import SessionLocal
from sqlalchemy import text

BASE = "http://127.0.0.1:8085"
USERNAME = "admin"
PASSWORD = "CDR2026"
ATHLETE_ID = "10025735"

# Datos base realistas para el deportista
BASE_MEASUREMENTS = {
    "ESTA_USER_CM": 179.0,
    "PESO_kg": 75.0,
    "PLIEGUE_TRICIPITAL": 12.0,
    "PLIEGUE_SUBESCAPULAR": 10.0,
    "PLIEGUE_SUPRAILIACO": 11.0,
    "PLIEGUE_ABDOMINAL": 15.0,
    "PLIEGUE_MUSLO_ANT": 8.0,
    "PLIEGUE_MEDIAL_PIERNA": 9.0,
    "DIAMETRO_BIEPI_MUNECA": 55.0,
    "DIAMETRO_BIEPI_FEMUR": 88.0,
    "DIAMETRO_CODO": 66.0,
    "PERIMETRO_BICED_CONTRAIDO": 32.0,
    "PERIMETRO_PIERNA": 52.0,
    "CIRCUNFERENCIA_CARPO": 18.0,
}

def login():
    """Realiza login y retorna el token"""
    print("1. Realizando login...")
    r = requests.post(
        f"{BASE}/auth/login",
        json={"username": USERNAME, "password": PASSWORD},
        timeout=10
    )
    if r.status_code != 200:
        print(f"   [X] Error de login: {r.status_code}")
        return None
    
    data = r.json()
    print(f"   [OK] Login exitoso: {data.get('username')}")
    return data.get("access_token")

def create_measurement_variation(base, month_offset):
    """Crea variaciones realistas de mediciones basadas en el mes"""
    import random
    random.seed(month_offset)  # Reproducible
    
    measurement = dict(base)
    
    # Variaciones realistas por mes
    measurement["PESO_kg"] = round(base["PESO_kg"] + random.uniform(-2, 2), 1)
    measurement["PLIEGUE_TRICIPITAL"] = round(base["PLIEGUE_TRICIPITAL"] + random.uniform(-1.5, 1.5), 1)
    measurement["PLIEGUE_SUBESCAPULAR"] = round(base["PLIEGUE_SUBESCAPULAR"] + random.uniform(-1, 1), 1)
    measurement["PLIEGUE_SUPRAILIACO"] = round(base["PLIEGUE_SUPRAILIACO"] + random.uniform(-1.5, 1.5), 1)
    measurement["PLIEGUE_ABDOMINAL"] = round(base["PLIEGUE_ABDOMINAL"] + random.uniform(-2, 2), 1)
    measurement["PLIEGUE_MUSLO_ANT"] = round(base["PLIEGUE_MUSLO_ANT"] + random.uniform(-1, 1), 1)
    measurement["PLIEGUE_MEDIAL_PIERNA"] = round(base["PLIEGUE_MEDIAL_PIERNA"] + random.uniform(-1, 1), 1)
    measurement["PERIMETRO_BICED_CONTRAIDO"] = round(base["PERIMETRO_BICED_CONTRAIDO"] + random.uniform(-1, 1), 1)
    measurement["PERIMETRO_PIERNA"] = round(base["PERIMETRO_PIERNA"] + random.uniform(-1, 1), 1)
    
    return measurement

def create_valoracion(token, fecha, detalles):
    """Crea una valoracion con multiples detalles"""
    payload = {
        "IDENTI_DEPORTISTA": ATHLETE_ID,
        "LOGIN_USER": USERNAME,
        "FECHA_MEDIDA": fecha.strftime("%Y-%m-%d"),
        "OBSERV": f"Valoracion mensual simulada - Mes {fecha.month}",
        "DETALLES": detalles
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(
        f"{BASE}/somatotipo/",
        json=payload,
        headers=headers,
        timeout=10
    )
    
    return r.status_code, r.json() if r.status_code == 200 else r.text

def main():
    print("\n" + "="*70)
    print("SIMULACION DE 12 VALORACIONES DEPORTIVAS")
    print("="*70 + "\n")
    
    # Paso 1: Login
    token = login()
    if not token:
        return
    
    # Paso 2: Generar fechas de los ultimos 12 meses
    print("\n2. Generando fechas de evaluacion...")
    today = datetime.now()
    fechas = []
    for i in range(12):
        # Retroceder i meses desde el mes actual
        mes = today.month - i
        anio = today.year
        while mes <= 0:
            mes += 12
            anio -= 1
        # Dia 15 de cada mes
        fecha = datetime(anio, mes, 15)
        fechas.append(fecha)
    
    fechas.reverse()  # Ordenar de mas antiguo a mas reciente
    
    for i, fecha in enumerate(fechas, 1):
        print(f"   Mes {i}: {fecha.strftime('%Y-%m-%d')}")
    
    # Paso 3: Crear 12 valoraciones
    print("\n3. Creando valoraciones...")
    valoraciones_creadas = 0
    
    for i, fecha in enumerate(fechas, 1):
        print(f"\n   Valoracion {i}/12 - Fecha: {fecha.strftime('%Y-%m-%d')}")
        
        # Crear 3 medidas (detalles) para cada valoracion
        detalles = []
        for j in range(3):
            # Variacion ligera entre las 3 medidas del mismo dia
            measurement = create_measurement_variation(BASE_MEASUREMENTS, i * 10 + j)
            detalles.append(measurement)
        
        # Crear valoracion
        status, response = create_valoracion(token, fecha, detalles)
        
        if status == 200:
            valoracion_id = response.get('id', 'N/A')
            print(f"   [OK] Creada - ID: {valoracion_id}")
            valoraciones_creadas += 1
        else:
            print(f"   [X] Error: {response}")
    
    # Paso 4: Verificar registros en BD
    print("\n" + "="*70)
    print("VERIFICACION EN BASE DE DATOS")
    print("="*70 + "\n")
    
    db = SessionLocal()
    try:
        # Contar valoraciones del deportista
        count_valoraciones = db.execute(text("""
            SELECT COUNT(*) 
            FROM CDRTablaSomatotipo 
            WHERE IDENTI_DEPORTISTA = :identi
        """), {"identi": ATHLETE_ID}).scalar()
        
        print(f"4.1. Total de valoraciones para deportista {ATHLETE_ID}:")
        print(f"     {count_valoraciones} registros en CDRTablaSomatotipo")
        
        # Contar detalles
        count_detalles = db.execute(text("""
            SELECT COUNT(*) 
            FROM CDRTablaSomatotipoDetalle d
            JOIN CDRTablaSomatotipo s ON d.id_Somatotipo = s.id_Somatotipo
            WHERE s.IDENTI_DEPORTISTA = :identi
        """), {"identi": ATHLETE_ID}).scalar()
        
        print(f"\n4.2. Total de medidas (detalles):")
        print(f"     {count_detalles} registros en CDRTablaSomatotipoDetalle")
        print(f"     Esperado: {valoraciones_creadas * 3} (3 medidas x {valoraciones_creadas} valoraciones)")
        
        # Mostrar ultimas 5 valoraciones
        print(f"\n4.3. Ultimas 5 valoraciones creadas:")
        rows = db.execute(text("""
            SELECT s.id_Somatotipo, s.FECHA_MEDIDA, s.LOGIN_USER,
                   (SELECT COUNT(*) FROM CDRTablaSomatotipoDetalle WHERE id_Somatotipo = s.id_Somatotipo) as num_detalles
            FROM CDRTablaSomatotipo s
            WHERE s.IDENTI_DEPORTISTA = :identi
            ORDER BY s.FECHA_MEDIDA DESC
            LIMIT 5
        """), {"identi": ATHLETE_ID}).fetchall()
        
        for row in rows:
            print(f"     - ID: {row[0]}, Fecha: {row[1]}, Usuario: {row[2]}, Detalles: {row[3]}")
        
    finally:
        db.close()
    
    # Paso 5: Verificar auditoria
    print("\n" + "="*70)
    print("VERIFICACION DE AUDITORIA")
    print("="*70 + "\n")
    
    db = SessionLocal()
    try:
        # Contar eventos de auditoria
        count_audit = db.execute(text("""
            SELECT COUNT(*) 
            FROM CDRTablaAuditoria
        """)).scalar()
        
        print(f"5.1. Total de eventos de auditoria:")
        print(f"     {count_audit} registros en CDRTablaAuditoria")
        
        # Eventos de creacion de somatotipo
        count_create = db.execute(text("""
            SELECT COUNT(*) 
            FROM CDRTablaAuditoria
            WHERE ACTION_CODE = 'CREATE_SOMATOTIPO'
        """)).scalar()
        
        print(f"\n5.2. Eventos CREATE_SOMATOTIPO:")
        print(f"     {count_create} registros")
        print(f"     Esperado: {valoraciones_creadas}")
        
        # Eventos de login
        count_login = db.execute(text("""
            SELECT COUNT(*) 
            FROM CDRTablaAuditoria
            WHERE ACTION_CODE IN ('LOGIN_SUCCESS', 'LOGIN_FAILED')
        """)).scalar()
        
        print(f"\n5.3. Eventos de autenticacion:")
        print(f"     {count_login} registros (LOGIN_SUCCESS + LOGIN_FAILED)")
        
        # Mostrar ultimos 10 eventos de auditoria
        print(f"\n5.4. Ultimos 10 eventos de auditoria:")
        rows = db.execute(text("""
            SELECT ID_AUDIT, OCCURRED_AT_UTC, ACTION_CODE, ACTOR_LOGIN, 
                   EVENT_RESULT, RESOURCE_TYPE, RESOURCE_ID
            FROM CDRTablaAuditoria 
            ORDER BY ID_AUDIT DESC 
            LIMIT 10
        """)).fetchall()
        
        for row in rows:
            print(f"     - ID: {row[0]}")
            print(f"       Fecha: {row[1]}")
            print(f"       Accion: {row[2]}")
            print(f"       Usuario: {row[3]}")
            print(f"       Resultado: {row[4]}")
            print(f"       Recurso: {row[5]}:{row[6]}")
            print()
        
    finally:
        db.close()
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN FINAL")
    print("="*70)
    print(f"\n[OK] Valoraciones creadas: {valoraciones_creadas}/12")
    print(f"[OK] Medidas totales: {count_detalles}")
    print(f"[OK] Eventos de auditoria: {count_audit}")
    print(f"[OK] Deportista: {ATHLETE_ID}")
    print(f"[OK] Periodo: {fechas[0].strftime('%Y-%m-%d')} a {fechas[-1].strftime('%Y-%m-%d')}")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
