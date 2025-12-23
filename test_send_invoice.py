"""
Test de envio de factura real a DIAN Colombia
Basado en XML de referencia que funciona
"""
import sys
import os
import base64
import zipfile
import io
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

# ============================================================================
# CONFIGURACION
# ============================================================================
CERT_PATH = r"D:\Certificados digitales\Elier Fernando\certificado.p12"
CERT_PASSWORD = "alnusNhAYtiQtJNe"

SOFTWARE_ID = "03f12b96-f0bf-40a3-bc71-0afbbd20b626"
PIN = "12345"
TECHNICAL_KEY = "fc8eac422eba16e22ffd8c6f94b3f40a6e38162c"

PREFIX = "SETP"
RESOLUTION_NUMBER = "18760000001"
RANGE_FROM = 990000000
RANGE_TO = 995000000
NEXT_INVOICE = 990000100

SUPPLIER_NIT = "1085286295"
SUPPLIER_NAME = "ELIER FERNANDO ROSERO BRAVO"

DIAN_URL = "https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc"


def generate_invoice_xml():
    """Genera XML de factura basado en ejemplo que funciona de la DIAN"""
    now = datetime.now()
    issue_date = now.strftime("%Y-%m-%d")
    issue_time = now.strftime("%H:%M:%S") + "-05:00"
    invoice_number = f"{PREFIX}{NEXT_INVOICE}"
    
    invoice_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
    xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    xmlns:sts="urn:dian:gov:co:facturaelectronica:Structures-2-1"
    xmlns:xades="http://uri.etsi.org/01903/v1.3.2#"
    xmlns:xades141="http://uri.etsi.org/01903/v1.4.1#"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <ext:UBLExtensions>
        <ext:UBLExtension>
            <ext:ExtensionContent>
                <sts:DianExtensions>
                    <sts:InvoiceControl>
                        <sts:InvoiceAuthorization>{RESOLUTION_NUMBER}</sts:InvoiceAuthorization>
                        <sts:AuthorizationPeriod>
                            <cbc:StartDate>2019-01-19</cbc:StartDate>
                            <cbc:EndDate>2030-01-19</cbc:EndDate>
                        </sts:AuthorizationPeriod>
                        <sts:AuthorizedInvoices>
                            <sts:Prefix>{PREFIX}</sts:Prefix>
                            <sts:From>{RANGE_FROM}</sts:From>
                            <sts:To>{RANGE_TO}</sts:To>
                        </sts:AuthorizedInvoices>
                    </sts:InvoiceControl>
                    <sts:InvoiceSource>
                        <cbc:IdentificationCode listAgencyID="6" listAgencyName="United Nations Economic Commission for Europe" listSchemeURI="urn:oasis:names:specification:ubl:codelist:gc:CountryIdentificationCode-2.1">CO</cbc:IdentificationCode>
                    </sts:InvoiceSource>
                    <sts:SoftwareProvider>
                        <sts:ProviderID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)" schemeID="3" schemeName="31">{SUPPLIER_NIT}</sts:ProviderID>
                        <sts:SoftwareID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)">{SOFTWARE_ID}</sts:SoftwareID>
                    </sts:SoftwareProvider>
                    <sts:SoftwareSecurityCode schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)"></sts:SoftwareSecurityCode>
                    <sts:AuthorizationProvider>
                        <sts:AuthorizationProviderID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)" schemeID="4" schemeName="31">800197268</sts:AuthorizationProviderID>
                    </sts:AuthorizationProvider>
                    <sts:QRCode>NumFac: {invoice_number} FecFac: {issue_date} NitFac: {SUPPLIER_NIT} DocAdq: 222222222222 ValFac: 100000.00 ValIva: 19000.00 ValOtroIm: 0.00 ValTotal: 119000.00 CUFE: -----CUFECUDE----- https://catalogo-vpfe-hab.dian.gov.co/document/searchqr?documentkey=-----CUFECUDE-----</sts:QRCode>
                </sts:DianExtensions>
            </ext:ExtensionContent>
        </ext:UBLExtension>
        <ext:UBLExtension>
            <ext:ExtensionContent></ext:ExtensionContent>
        </ext:UBLExtension>
    </ext:UBLExtensions>
    <cbc:UBLVersionID>UBL 2.1</cbc:UBLVersionID>
    <cbc:CustomizationID>10</cbc:CustomizationID>
    <cbc:ProfileID>DIAN 2.1: Factura Electrónica de Venta</cbc:ProfileID>
    <cbc:ProfileExecutionID>2</cbc:ProfileExecutionID>
    <cbc:ID>{invoice_number}</cbc:ID>
    <cbc:UUID schemeID="2" schemeName="CUFE-SHA384"></cbc:UUID>
    <cbc:IssueDate>{issue_date}</cbc:IssueDate>
    <cbc:IssueTime>{issue_time}</cbc:IssueTime>
    <cbc:InvoiceTypeCode>01</cbc:InvoiceTypeCode>
    <cbc:DocumentCurrencyCode>COP</cbc:DocumentCurrencyCode>
    <cbc:LineCountNumeric>1</cbc:LineCountNumeric>
    <cac:AccountingSupplierParty>
        <cbc:AdditionalAccountID>2</cbc:AdditionalAccountID>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)" schemeID="3" schemeName="13">{SUPPLIER_NIT}</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyName>
                <cbc:Name>{SUPPLIER_NAME}</cbc:Name>
            </cac:PartyName>
            <cac:PhysicalLocation>
                <cac:Address>
                    <cbc:ID>52001</cbc:ID>
                    <cbc:CityName>Pasto</cbc:CityName>
                    <cbc:CountrySubentity>Nariño</cbc:CountrySubentity>
                    <cbc:CountrySubentityCode>52</cbc:CountrySubentityCode>
                    <cac:AddressLine>
                        <cbc:Line>CRA 16B 19 26</cbc:Line>
                    </cac:AddressLine>
                    <cac:Country>
                        <cbc:IdentificationCode>CO</cbc:IdentificationCode>
                        <cbc:Name languageID="es">Colombia</cbc:Name>
                    </cac:Country>
                </cac:Address>
            </cac:PhysicalLocation>
            <cac:PartyTaxScheme>
                <cbc:RegistrationName>{SUPPLIER_NAME}</cbc:RegistrationName>
                <cbc:CompanyID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)" schemeID="3" schemeName="13">{SUPPLIER_NIT}</cbc:CompanyID>
                <cbc:TaxLevelCode listName="49">R-99-PN</cbc:TaxLevelCode>
                <cac:RegistrationAddress>
                    <cbc:ID>52001</cbc:ID>
                    <cbc:CityName>Pasto</cbc:CityName>
                    <cbc:CountrySubentity>Nariño</cbc:CountrySubentity>
                    <cbc:CountrySubentityCode>52</cbc:CountrySubentityCode>
                    <cac:AddressLine>
                        <cbc:Line>CRA 16B 19 26</cbc:Line>
                    </cac:AddressLine>
                    <cac:Country>
                        <cbc:IdentificationCode>CO</cbc:IdentificationCode>
                        <cbc:Name languageID="es">Colombia</cbc:Name>
                    </cac:Country>
                </cac:RegistrationAddress>
                <cac:TaxScheme>
                    <cbc:ID>01</cbc:ID>
                    <cbc:Name>IVA</cbc:Name>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:PartyLegalEntity>
                <cbc:RegistrationName>{SUPPLIER_NAME}</cbc:RegistrationName>
                <cbc:CompanyID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)" schemeID="3" schemeName="13">{SUPPLIER_NIT}</cbc:CompanyID>
                <cac:CorporateRegistrationScheme>
                    <cbc:ID>{PREFIX}</cbc:ID>
                    <cbc:Name>0000000-00</cbc:Name>
                </cac:CorporateRegistrationScheme>
            </cac:PartyLegalEntity>
            <cac:Contact>
                <cbc:Telephone>3156544882</cbc:Telephone>
                <cbc:ElectronicMail>ferrosero911@gmail.com</cbc:ElectronicMail>
            </cac:Contact>
        </cac:Party>
    </cac:AccountingSupplierParty>
    <cac:AccountingCustomerParty>
        <cbc:AdditionalAccountID>2</cbc:AdditionalAccountID>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)" schemeID="7" schemeName="31">222222222222</cbc:ID>
            </cac:PartyIdentification>
            <cac:PartyName>
                <cbc:Name>CONSUMIDOR FINAL</cbc:Name>
            </cac:PartyName>
            <cac:PhysicalLocation>
                <cac:Address>
                    <cbc:ID>11001</cbc:ID>
                    <cbc:CityName>Bogotá, D.c.</cbc:CityName>
                    <cbc:CountrySubentity>Bogotá</cbc:CountrySubentity>
                    <cbc:CountrySubentityCode>11</cbc:CountrySubentityCode>
                    <cac:AddressLine>
                        <cbc:Line>Sin dirección</cbc:Line>
                    </cac:AddressLine>
                    <cac:Country>
                        <cbc:IdentificationCode>CO</cbc:IdentificationCode>
                        <cbc:Name languageID="es">Colombia</cbc:Name>
                    </cac:Country>
                </cac:Address>
            </cac:PhysicalLocation>
            <cac:PartyTaxScheme>
                <cbc:RegistrationName>CONSUMIDOR FINAL</cbc:RegistrationName>
                <cbc:CompanyID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)" schemeID="7" schemeName="31">222222222222</cbc:CompanyID>
                <cbc:TaxLevelCode listName="49">R-99-PN</cbc:TaxLevelCode>
                <cac:RegistrationAddress>
                    <cbc:ID>11001</cbc:ID>
                    <cbc:CityName>Bogotá, D.c.</cbc:CityName>
                    <cbc:CountrySubentity>Bogotá</cbc:CountrySubentity>
                    <cbc:CountrySubentityCode>11</cbc:CountrySubentityCode>
                    <cac:AddressLine>
                        <cbc:Line>Sin dirección</cbc:Line>
                    </cac:AddressLine>
                    <cac:Country>
                        <cbc:IdentificationCode>CO</cbc:IdentificationCode>
                        <cbc:Name languageID="es">Colombia</cbc:Name>
                    </cac:Country>
                </cac:RegistrationAddress>
                <cac:TaxScheme>
                    <cbc:ID>01</cbc:ID>
                    <cbc:Name>IVA</cbc:Name>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:PartyLegalEntity>
                <cbc:RegistrationName>CONSUMIDOR FINAL</cbc:RegistrationName>
                <cbc:CompanyID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)" schemeID="7" schemeName="31">222222222222</cbc:CompanyID>
                <cac:CorporateRegistrationScheme>
                    <cbc:Name>0000000-00</cbc:Name>
                </cac:CorporateRegistrationScheme>
            </cac:PartyLegalEntity>
            <cac:Contact> </cac:Contact>
        </cac:Party>
    </cac:AccountingCustomerParty>
    <cac:PaymentMeans>
        <cbc:ID>1</cbc:ID>
        <cbc:PaymentMeansCode>10</cbc:PaymentMeansCode>
        <cbc:PaymentDueDate>{issue_date}</cbc:PaymentDueDate>
        <cbc:PaymentID>1</cbc:PaymentID>
    </cac:PaymentMeans>
    <cac:PaymentTerms>
        <cbc:ReferenceEventCode>1</cbc:ReferenceEventCode>
        <cac:SettlementPeriod>
            <cbc:DurationMeasure unitCode="DAY">0</cbc:DurationMeasure>
        </cac:SettlementPeriod>
    </cac:PaymentTerms>
    <cac:TaxTotal>
        <cbc:TaxAmount currencyID="COP">19000.00</cbc:TaxAmount>
        <cbc:RoundingAmount currencyID="COP">0.00</cbc:RoundingAmount>
        <cac:TaxSubtotal>
            <cbc:TaxableAmount currencyID="COP">100000.00</cbc:TaxableAmount>
            <cbc:TaxAmount currencyID="COP">19000.00</cbc:TaxAmount>
            <cac:TaxCategory>
                <cbc:Percent>19.00</cbc:Percent>
                <cac:TaxScheme>
                    <cbc:ID>01</cbc:ID>
                    <cbc:Name>IVA</cbc:Name>
                </cac:TaxScheme>
            </cac:TaxCategory>
        </cac:TaxSubtotal>
    </cac:TaxTotal>
    <cac:LegalMonetaryTotal>
        <cbc:LineExtensionAmount currencyID="COP">100000.00</cbc:LineExtensionAmount>
        <cbc:TaxExclusiveAmount currencyID="COP">100000.00</cbc:TaxExclusiveAmount>
        <cbc:TaxInclusiveAmount currencyID="COP">119000.00</cbc:TaxInclusiveAmount>
        <cbc:AllowanceTotalAmount currencyID="COP">0.00</cbc:AllowanceTotalAmount>
        <cbc:PayableAmount currencyID="COP">119000.00</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
    <cac:InvoiceLine>
        <cbc:ID>1</cbc:ID>
        <cbc:InvoicedQuantity unitCode="94">1.000000</cbc:InvoicedQuantity>
        <cbc:LineExtensionAmount currencyID="COP">100000.00</cbc:LineExtensionAmount>
        <cbc:FreeOfChargeIndicator>false</cbc:FreeOfChargeIndicator>
        <cac:TaxTotal>
            <cbc:TaxAmount currencyID="COP">19000.00</cbc:TaxAmount>
            <cbc:RoundingAmount currencyID="COP">0.00</cbc:RoundingAmount>
            <cac:TaxSubtotal>
                <cbc:TaxableAmount currencyID="COP">100000.00</cbc:TaxableAmount>
                <cbc:TaxAmount currencyID="COP">19000.00</cbc:TaxAmount>
                <cac:TaxCategory>
                    <cbc:Percent>19.00</cbc:Percent>
                    <cac:TaxScheme>
                        <cbc:ID>01</cbc:ID>
                        <cbc:Name>IVA</cbc:Name>
                    </cac:TaxScheme>
                </cac:TaxCategory>
            </cac:TaxSubtotal>
        </cac:TaxTotal>
        <cac:Item>
            <cbc:Description>SERVICIO PRUEBA PYTHON</cbc:Description>
            <cac:StandardItemIdentification>
                <cbc:ID schemeID="999" schemeName="Estándar de adopción del contribuyente" schemeAgencyID="">001</cbc:ID>
            </cac:StandardItemIdentification>
        </cac:Item>
        <cac:Price>
            <cbc:PriceAmount currencyID="COP">100000.00</cbc:PriceAmount>
            <cbc:BaseQuantity unitCode="94">1.000000</cbc:BaseQuantity>
        </cac:Price>
    </cac:InvoiceLine>
</Invoice>'''
    
    return invoice_xml, invoice_number


print("="*60)
print("TEST DE ENVIO DE FACTURA A DIAN")
print("="*60)

if not os.path.exists(CERT_PATH):
    print(f"ERROR: No se encuentra el certificado: {CERT_PATH}")
    sys.exit(1)

# Paso 1: Generar XML
print("\n=== PASO 1: Generando XML ===")
invoice_xml, invoice_number = generate_invoice_xml()
print(f"  Factura: {invoice_number}")

with open('invoice_unsigned.xml', 'w', encoding='utf-8') as f:
    f.write(invoice_xml)
print("  Guardado: invoice_unsigned.xml")

# Paso 2: Firmar
print("\n=== PASO 2: Firmando factura ===")
print("  - Usando namespace URN")
try:
    from ubl21dian.xades.urn.sign_invoice import SignInvoice
    
    signer = SignInvoice(
        path_certificate=CERT_PATH,
        password=CERT_PASSWORD,
        xml_string=invoice_xml,
        software_id=SOFTWARE_ID,
        pin=PIN,
        technical_key=TECHNICAL_KEY
    )
    
    signed_xml = signer.xml
    cufe = signer.get_tag('UUID', 0).text
    print(f"  CUFE: {cufe[:50]}...")
    
    with open('invoice_signed.xml', 'w', encoding='utf-8') as f:
        f.write(signed_xml)
    print("  Guardado: invoice_signed.xml")
    
except Exception as e:
    import traceback
    print(f"  ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

# Paso 3: Crear ZIP
print("\n=== PASO 3: Creando ZIP ===")
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
    xml_filename = f"face_{SUPPLIER_NIT}00000{invoice_number}.xml"
    zf.writestr(xml_filename, signed_xml.encode('utf-8'))

zip_content = zip_buffer.getvalue()
zip_base64 = base64.b64encode(zip_content).decode('utf-8')
zipfilename = f"z_{SUPPLIER_NIT}00000{invoice_number}.zip"

with open(zipfilename, 'wb') as f:
    f.write(zip_content)
print(f"  ZIP: {zipfilename} ({len(zip_content)} bytes)")

# Paso 4: Enviar a DIAN
print("\n=== PASO 4: Enviando a DIAN ===")
try:
    from ubl21dian.templates.soap.send_bill_sync import SendBillSync
    from ubl21dian.client import Client
    
    template = SendBillSync(CERT_PATH, CERT_PASSWORD)
    template.file_name = zipfilename
    template.content_file = zip_base64
    template.To = DIAN_URL
    template.sign()
    
    with open('dian_send_request.xml', 'w', encoding='utf-8') as f:
        f.write(template.xml)
    
    print(f"  Enviando a: {DIAN_URL}")
    client = Client(template)
    response = client.get_response()
    
    with open('dian_send_response.xml', 'w', encoding='utf-8') as f:
        f.write(response)
    print(f"  Respuesta: {len(response)} bytes")
    
    # Analizar respuesta
    import re
    print("\n=== RESPUESTA DIAN ===")
    
    status = re.search(r'<b:StatusCode[^>]*>([^<]+)</b:StatusCode>', response)
    desc = re.search(r'<b:StatusDescription[^>]*>([^<]+)</b:StatusDescription>', response)
    valid = re.search(r'<b:IsValid[^>]*>([^<]+)</b:IsValid>', response)
    
    if status:
        print(f"  StatusCode: {status.group(1)}")
    if desc:
        print(f"  Description: {desc.group(1)}")
    if valid:
        print(f"  IsValid: {valid.group(1)}")
    
    # Errores
    errors = re.findall(r'<c:string>([^<]+)</c:string>', response)
    if errors:
        print(f"\n  Errores ({len(errors)}):")
        for e in errors[:10]:
            print(f"    - {e[:100]}")
        if len(errors) > 10:
            print(f"    ... y {len(errors)-10} más")

except Exception as e:
    import traceback
    print(f"  ERROR: {e}")
    traceback.print_exc()
