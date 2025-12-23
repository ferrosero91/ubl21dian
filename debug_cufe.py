"""Debug CUFE calculation"""
import sys
sys.path.insert(0, '.')
import hashlib
from lxml import etree

# Leer factura sin firmar
with open('invoice_unsigned.xml', 'r', encoding='utf-8') as f:
    xml = f.read()

doc = etree.fromstring(xml.encode('utf-8'))

# Namespaces
ns = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
}

# Extraer valores
def get_text(xpath):
    result = doc.xpath(xpath, namespaces=ns)
    return result[0].text if result else None

def get_tax(code):
    xpath = "cac:TaxTotal[cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID='" + code + "']/cbc:TaxAmount"
    result = doc.xpath(xpath, namespaces=ns)
    return result[0].text if result else '0.00'

# Valores
val_id = get_text('//cbc:ID')
val_date = get_text('//cbc:IssueDate')
val_time = get_text('//cbc:IssueTime')
val_le_amt = get_text('//cac:LegalMonetaryTotal/cbc:LineExtensionAmount')
val_tax_01 = get_tax('01')
val_tax_04 = get_tax('04')
val_tax_03 = get_tax('03')
val_payable = get_text('//cac:LegalMonetaryTotal/cbc:PayableAmount')
val_supp_id = get_text('//cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID')
val_cust_id = get_text('//cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID')
val_prof_exec_id = get_text('//cbc:ProfileExecutionID')

TECHNICAL_KEY = 'fc8eac422eba16e22ffd8c6f94b3f40a6e38162c'

print('Valores extraidos:')
print(f'  ID: {val_id}')
print(f'  IssueDate: {val_date}')
print(f'  IssueTime: {val_time}')
print(f'  LineExtensionAmount: {val_le_amt}')
print(f'  Tax 01 (IVA): {val_tax_01}')
print(f'  Tax 04 (INC): {val_tax_04}')
print(f'  Tax 03 (ICA): {val_tax_03}')
print(f'  PayableAmount: {val_payable}')
print(f'  SupplierID: {val_supp_id}')
print(f'  CustomerID: {val_cust_id}')
print(f'  ProfileExecutionID: {val_prof_exec_id}')
print(f'  TechnicalKey: {TECHNICAL_KEY}')
print()

# Construir cadena CUFE
raw_str = f'{val_id}{val_date}{val_time}{val_le_amt}01{val_tax_01}04{val_tax_04}03{val_tax_03}{val_payable}{val_supp_id}{val_cust_id}{TECHNICAL_KEY}{val_prof_exec_id}'
print(f'Cadena CUFE:')
print(f'  {raw_str}')
print()

cufe = hashlib.sha384(raw_str.encode('utf-8')).hexdigest()
print(f'CUFE calculado: {cufe}')
