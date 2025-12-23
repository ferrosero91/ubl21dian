# UBL21DIAN - Firma Electrónica DIAN Colombia (Python)

Biblioteca Python para firma electrónica de documentos UBL 2.1 para la DIAN Colombia.



## Estado

✅ **Probado en producción** - Factura enviada y aceptada por DIAN (StatusCode: 00)

## Características

- Firma XAdES-EPES para documentos electrónicos
- WS-Security SOAP para comunicación con servicios DIAN
- Soporte completo para:
  - Facturas electrónicas
  - Notas crédito/débito
  - Documento soporte
  - Nómina electrónica
  - Eventos RADIAN
- Cálculo automático de CUFE, CUDE, CUDS, CUNE
- 15 operaciones SOAP disponibles

## Instalación

```bash
pip install -r requirements.txt
```

## Uso Rápido

### Firmar una Factura

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

template = SendBillSync('certificado.p12', 'password')
template.file_name = 'factura.zip'
template.content_file = base64.b64encode(zip_content).decode()
template.To = 'https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc'
template.sign()

response = Client(template).get_response()
```

## Documentación



## Tests

```bash
python test_migration.py
```

## Licencia

MIT
