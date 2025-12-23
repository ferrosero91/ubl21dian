# Estado de Migracion PHP a Python - DIAN Colombia

## MIGRACION COMPLETADA Y PROBADA EN PRODUCCION

**Fecha**: 23 de Diciembre 2025  
**Estado**: Funcional - Factura enviada y aceptada por DIAN (StatusCode: 00, IsValid: true)

---

## Resumen

La biblioteca Python `ubl21dian` es una migracion completa de la biblioteca PHP original para firma electronica de documentos DIAN Colombia. Ha sido probada exitosamente enviando facturas reales al ambiente de habilitacion de la DIAN.

---

## Capacidades Soportadas

### Tipos de Documentos Electronicos

| Documento | Firmador | Estado |
|-----------|----------|--------|
| Factura Electronica de Venta | `SignInvoice` | Probado |
| Nota Credito | `SignCreditNote` | Implementado |
| Nota Debito | `SignDebitNote` | Implementado |
| Nomina Individual | `SignPayroll` | Implementado |
| Nota de Ajuste Nomina | `SignPayrollNote` | Implementado |
| Eventos (Acuse, Recibo, etc.) | `SignEvent` | Implementado |
| Documento Adjunto | `SignAttachedDocument` | Implementado |

### Variantes de Namespace

| Variante | Namespace STS | Uso |
|----------|---------------|-----|
| Estandar | `dian:gov:co:facturaelectronica:Structures-2-1` | Documentos antiguos |
| URN | `urn:dian:gov:co:facturaelectronica:Structures-2-1` | Recomendado |

### Operaciones SOAP Soportadas (15 templates)

| Operacion | Template | Descripcion |
|-----------|----------|-------------|
| SendBillSync | `send_bill_sync.py` | Envio sincrono de facturas |
| SendBillAsync | `send_bill_async.py` | Envio asincrono de facturas |
| SendBillAttachmentAsync | `send_bill_attachment_async.py` | Envio de documentos adjuntos |
| SendEvent | `send_event.py` | Envio de eventos RADIAN |
| SendPayrollSync | `send_payroll_sync.py` | Envio sincrono de nomina |
| SendPayrollAsync | `send_payroll_async.py` | Envio asincrono de nomina |
| SendTestSetAsync | `send_test_set_async.py` | Envio de set de pruebas |
| GetStatus | `get_status.py` | Consulta estado por TrackId |
| GetStatusZip | `get_status_zip.py` | Consulta estado de ZIP |
| GetStatusEvents | `get_status_events.py` | Consulta eventos de documento |
| GetNumberingRange | `get_numbering_range.py` | Consulta rangos de numeracion |
| GetXmlByDocumentKey | `get_xml_by_document_key.py` | Obtener XML por CUFE/CUDE |
| GetDocumentInfo | `get_document_info.py` | Informacion de documento |
| GetAcquirer | `get_acquirer.py` | Consulta adquirente |
| GetReferenceNotes | `get_reference_notes.py` | Consulta notas de referencia |

### Calculos de UUID Soportados

| Tipo | Metodo | Documentos |
|------|--------|------------|
| CUFE | `cufe()` | Facturas con clave tecnica |
| CUDE | `cude()` | Notas credito/debito, documentos soporte |
| CUDS | `cuds()` | Documentos soporte en adquisiciones |
| CUNE | `cune()` | Nomina electronica |
| CUDE Event | `cudeevent()` | Eventos RADIAN |

### Algoritmos de Firma

- SHA-1 (legacy)
- SHA-256 (recomendado)
- SHA-512

---

## Prueba Real Exitosa

```
Factura: SETP990000096
Fecha: 2025-12-23
NIT Emisor: 1085286295
Ambiente: Habilitacion

Respuesta DIAN:
- StatusCode: 00
- StatusDescription: Procesado Correctamente
- IsValid: true
```

---

## Uso Basico

### Firmar una Factura (Recomendado: usar variante URN)

```python
from ubl21dian.xades.urn.sign_invoice import SignInvoice

signer = SignInvoice(
    path_certificate='certificado.p12',
    password='password',
    xml_string=xml_factura,
    software_id='tu-software-id',
    pin='tu-pin',
    technical_key='tu-clave-tecnica'
)

xml_firmado = signer.xml
cufe = signer.get_tag('UUID', 0).text
```

### Enviar a DIAN

```python
from ubl21dian.templates.soap.send_bill_sync import SendBillSync
from ubl21dian.client import Client
import base64

zip_base64 = base64.b64encode(zip_content).decode('utf-8')

template = SendBillSync('certificado.p12', 'password')
template.file_name = 'z_nit00000factura.zip'
template.content_file = zip_base64
template.To = 'https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc'
template.sign()

client = Client(template)
response = client.get_response()
```

### Consultar Estado

```python
from ubl21dian.templates.soap.get_status import GetStatus
from ubl21dian.client import Client

template = GetStatus('certificado.p12', 'password')
template.track_id = 'tu-track-id-o-cufe'
template.To = 'https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc'
template.sign()

client = Client(template)
response = client.get_response()
```

---

## URLs de Servicios DIAN

| Ambiente | URL |
|----------|-----|
| Habilitacion | `https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc` |
| Produccion | `https://vpfe.dian.gov.co/WcfDianCustomerServices.svc` |

---

## Dependencias

```
lxml>=4.9.0
cryptography>=41.0.0
requests>=2.31.0
```

Instalar con: `pip install -r requirements.txt`

---

## Tests

15/15 tests pasando:

```bash
python test_migration.py
```

---

## Notas Importantes

1. **Usar variante URN**: Para documentos actuales, usar los firmadores en `ubl21dian/xades/urn/`

2. **Parametros en constructor**: Pasar `software_id`, `pin` y `technical_key` en el constructor

3. **ProfileID**: Debe ser exactamente `"DIAN 2.1: Factura Electronica de Venta"`

4. **schemeID para persona natural**: Usar `schemeID="3"` y `schemeName="13"` para cedula

5. **AdditionalAccountID**: Usar `"2"` para persona natural, `"1"` para persona juridica
