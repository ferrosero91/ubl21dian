"""
Test de conexion real con DIAN Colombia
Usa el servicio GetStatus para verificar la comunicacion
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# Configuracion - MODIFICAR SEGUN TU CERTIFICADO
CERT_PATH = r"D:\Certificados digitales\Elier Fernando\certificado.p12"
CERT_PASSWORD = "alnusNhAYtiQtJNe"

# URLs de DIAN
DIAN_HAB_URL = "https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc"  # Habilitacion
DIAN_PROD_URL = "https://vpfe.dian.gov.co/WcfDianCustomerServices.svc"     # Produccion

# Usar ambiente de habilitacion para pruebas
DIAN_URL = DIAN_HAB_URL

print("="*60)
print("TEST DE CONEXION CON DIAN COLOMBIA")
print("="*60)
print(f"URL: {DIAN_URL}")
print(f"Certificado: {CERT_PATH}")
print()

# Verificar que existe el certificado
if not os.path.exists(CERT_PATH):
    print(f"ERROR: No se encuentra el certificado en: {CERT_PATH}")
    print("Por favor modifica CERT_PATH en este archivo")
    sys.exit(1)

# Test 1: Cargar certificado
print("=== TEST 1: Cargando certificado ===")
try:
    from ubl21dian.templates.soap.get_status import GetStatus
    from ubl21dian.client import Client
    
    template = GetStatus(CERT_PATH, CERT_PASSWORD)
    print(f"  Certificado cargado correctamente")
    print(f"  Subject: {template.certs['cert'].subject}")
except Exception as e:
    print(f"  ERROR cargando certificado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Generar request SOAP firmado
print("\n=== TEST 2: Generando request SOAP firmado ===")
try:
    # Configurar ANTES de firmar
    template.track_id = "123456789"  # TrackId de prueba
    template.To = DIAN_URL
    template.Action = "http://wcf.dian.colombia/IWcfDianCustomerServices/GetStatus"
    
    # Ahora firmar
    template.sign()
    
    print(f"  Request SOAP generado: {len(template.xml)} bytes")
    
    # Guardar para debug
    with open('dian_request.xml', 'w', encoding='utf-8') as f:
        f.write(template.xml)
    print(f"  Guardado en: dian_request.xml")
    
except Exception as e:
    print(f"  ERROR generando request: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Enviar a DIAN
print("\n=== TEST 3: Enviando request a DIAN ===")
try:
    print(f"  Conectando a: {DIAN_URL}")
    
    # Crear cliente y enviar
    client = Client(template)
    response = client.get_response()
    
    print(f"  Respuesta recibida: {len(response)} bytes")
    
    # Guardar respuesta
    with open('dian_response.xml', 'w', encoding='utf-8') as f:
        f.write(response)
    print(f"  Guardado en: dian_response.xml")
    
    # Analizar respuesta
    import re
    
    if 'Fault' in response or 'fault' in response.lower():
        print("\n  RESPUESTA CON FAULT (puede ser esperado para trackId invalido):")
        # Extraer mensaje de error
        reason = re.search(r'<[^:]*:?Reason[^>]*>.*?<[^:]*:?Text[^>]*>([^<]+)', response, re.DOTALL)
        if reason:
            print(f"    Mensaje: {reason.group(1)}")
        else:
            faultstring = re.search(r'<faultstring[^>]*>([^<]+)</faultstring>', response)
            if faultstring:
                print(f"    Mensaje: {faultstring.group(1)}")
    elif 'GetStatusResponse' in response:
        print("\n  RESPUESTA GetStatusResponse recibida!")
        # Extraer StatusCode
        status = re.search(r'StatusCode[^>]*>([^<]+)<', response)
        if status:
            print(f"    StatusCode: {status.group(1)}")
        status_msg = re.search(r'StatusMessage[^>]*>([^<]+)<', response)
        if status_msg:
            print(f"    StatusMessage: {status_msg.group(1)}")
    else:
        print("\n  Respuesta (primeros 1000 chars):")
        print(f"    {response[:1000]}")
    
    print("\n" + "="*60)
    print("CONEXION CON DIAN EXITOSA!")
    print("="*60)
    print("\nLa biblioteca puede comunicarse correctamente con los")
    print("servicios web de la DIAN.")
    
except Exception as e:
    print(f"\n  ERROR en conexion: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n" + "="*60)
    print("ERROR DE CONEXION")
    print("="*60)
    print("\nPosibles causas:")
    print("1. Sin conexion a internet")
    print("2. Certificado no autorizado en DIAN")
    print("3. Firewall bloqueando conexion")
    print("4. URL incorrecta")
    sys.exit(1)
