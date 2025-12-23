"""Test with real certificate"""
import sys
import os

# Password provided by user
password = "alnusNhAYtiQtJNe"

print(f"Using password: {password}")

cert_path = r"D:\Certificados digitales\Elier Fernando\certificado.p12"

# Test 1: Load certificate
print("\n=== TEST 1: Loading Certificate ===")
try:
    from ubl21dian.xades.sign_invoice import SignInvoice
    
    with open('sample_invoice.xml', 'r', encoding='utf-8') as f:
        xml = f.read()
    
    signer = SignInvoice(cert_path, password, xml)
    print("✅ Certificate loaded successfully!")
    print(f"   Certificate subject: {signer.certs['cert'].subject}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Sign invoice
print("\n=== TEST 2: Signing Invoice ===")
try:
    signer.software_id = 'aae35b45-6f9a-4da5-a32c-78d63da52364'
    signer.pin = '12345'
    signer.technical_key = 'fc8eac422eba16e22ffd8c6f94b3940a6e38e62cd3ad353850410b63421dcaea90224431ee00823797b52fb050410b63'
    
    signer.software_security_code()
    signer.set_uuid()
    
    with open('signed_with_real_cert.xml', 'w', encoding='utf-8') as f:
        f.write(signer.xml)
    
    print("✅ Invoice signed successfully!")
    print(f"   Output: signed_with_real_cert.xml")
    
    if '<ds:SignatureValue>' in signer.xml:
        print("✅ Signature value present")
    if 'rsa-sha256' in signer.xml:
        print("✅ SHA256 algorithm detected")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: SOAP Template
print("\n=== TEST 3: SOAP Template with Real Certificate ===")
try:
    from ubl21dian.templates.soap.get_status import GetStatus
    
    template = GetStatus(cert_path, password)
    template.track_id = '1234567890'
    template.sign()
    
    with open('soap_real_cert.xml', 'w', encoding='utf-8') as f:
        f.write(template.xml)
    
    print("✅ SOAP request generated successfully!")
    print(f"   Output: soap_real_cert.xml")
    
    if '<wsse:BinarySecurityToken' in template.xml:
        print("✅ Binary Security Token present")
    if '<ds:Signature' in template.xml:
        print("✅ WS-Security signature present")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("✅ ALL TESTS PASSED WITH REAL CERTIFICATE!")
print("="*60)
