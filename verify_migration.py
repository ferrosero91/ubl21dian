import sys
import os
import argparse
import traceback

# Add parent dir to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from ubl21dian.xades.sign_invoice import SignInvoice
from ubl21dian.templates.soap.get_status import GetStatus

def verify_invoice_signing():
    print("--- Verifying Invoice Signing ---")
    try:
        with open('sample_invoice.xml', 'r', encoding='utf-8') as f:
            xml_string = f.read()
            
        path_cert = args.cert
        password = args.password
        
        signer = SignInvoice(path_cert, password, xml_string)
        
        # Test Software Security Code logic
        signer.software_id = 'aae35b45-6f9a-4da5-a32c-78d63da52364'
        signer.pin = '12345'
        signer.software_security_code()
        
        # Test CUFE logic
        signer.technical_key = 'fc8eac422eba16e22ffd8c6f94b3940a6e38e62cd3ad353850410b63421dcaea90224431ee00823797b52fb050410b63'
        signer.set_uuid()
        
        # Save signed XML
        with open('signed_invoice.xml', 'w', encoding='utf-8') as f:
            f.write(signer.xml)
            
        print("Success! Signed Invoice saved to signed_invoice.xml")
        
        # Quick validation of contents
        if 'Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"' in signer.xml:
            print("[OK] SHA256 Algorithm found")
        else:
            print("[FAIL] SHA256 Algorithm NOT found")
            
        if '<ds:SignatureValue>' in signer.xml:
             print("[OK] SignatureValue found")
             
    except Exception as e:
        print(f"Error during verification: {e}")
        traceback.print_exc()

def verify_soap_template():
    print("\n--- Verifying SOAP Template (GetStatus) ---")
    try:
        path_cert = args.cert
        password = args.password
        
        template = GetStatus(path_cert, password)
        template.track_id = '1234567890'
        
        # Sign (generate SOAP envelope)
        template.sign()
        
        with open('soap_request.xml', 'w', encoding='utf-8') as f:
            f.write(template.xml)
            
        print("Success! SOAP Request saved to soap_request.xml")
        
        if '<soap:Body>' in template.xml and '<wcf:trackId>1234567890</wcf:trackId>' in template.xml:
             print("[OK] Body content verification passed")
             
        if '<wsse:Security' in template.xml:
             print("[OK] WS-Security Header found")
             
    except Exception as e:
        print(f"Error during SOAP verification: {e}")
        traceback.print_exc()

def verify_send_bill_async():
    print("\n--- Verifying SOAP Template (SendBillAsync) ---")
    try:
        from ubl21dian.templates.soap.send_bill_async import SendBillAsync
        path_cert = args.cert
        password = args.password
        
        template = SendBillAsync(path_cert, password)
        template.file_name = 'test.zip'
        template.content_file = 'BASE64CONTENT=='
        
        template.sign()
        
        with open('send_bill_request.xml', 'w', encoding='utf-8') as f:
            f.write(template.xml)
            
        print("Success! SendBillAsync Request saved to send_bill_request.xml")
        
        if '<wcf:fileName>test.zip</wcf:fileName>' in template.xml:
             print("[OK] FileName found")
             
    except Exception as e:
        print(f"Error during SendBillAsync verification: {e}")
        traceback.print_exc()

def verify_get_numbering_range():
    print("\n--- Verifying SOAP Template (GetNumberingRange) ---")
    try:
        from ubl21dian.templates.soap.get_numbering_range import GetNumberingRange
        path_cert = args.cert
        password = args.password
        
        template = GetNumberingRange(path_cert, password)
        template.nit = '900000000'
        template.id_software = 'SOFTWARE-ID'
        
        template.sign()
        
        with open('get_numbering_range_request.xml', 'w', encoding='utf-8') as f:
            f.write(template.xml)
            
        print("Success! GetNumberingRange Request saved to get_numbering_range_request.xml")
        
        if '<wcf:accountCode>900000000</wcf:accountCode>' in template.xml:
             print("[OK] AccountCode found")
             
    except Exception as e:
        print(f"Error during GetNumberingRange verification: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Verify DIAN Migration')
    parser.add_argument('--cert', default='certificate.p12', help='Path to .p12 certificate')
    parser.add_argument('--password', default='1234', help='Certificate password')
    args = parser.parse_args()
    
    verify_invoice_signing()
    verify_soap_template()
    verify_send_bill_async()
    verify_get_numbering_range()
