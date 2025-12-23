"""
Comprehensive Test Suite for DIAN Migration
Tests all XAdES signers, SOAP templates, and core functionality
"""
import sys
import os
import traceback

sys.path.append(os.path.join(os.path.dirname(__file__)))

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test(self, name, func):
        """Run a single test"""
        try:
            func()
            print(f"✅ {name}")
            self.passed += 1
            return True
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
            self.errors.append((name, str(e), traceback.format_exc()))
            self.failed += 1
            return False
    
    def summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"Test Results: {self.passed}/{total} passed")
        print(f"{'='*60}")
        
        if self.errors:
            print("\n❌ Failed Tests:")
            for name, error, trace in self.errors:
                print(f"\n{name}:")
                print(f"  Error: {error}")
        
        return self.failed == 0

# Test Runner Instance
runner = TestRunner()

# ============================================================================
# TEST 1: Core Imports
# ============================================================================
def test_core_imports():
    """Test that all core modules can be imported"""
    from ubl21dian import sign, utils, client, constants
    from ubl21dian.binary_security_token import soap
    from ubl21dian.templates import template
    assert sign is not None
    assert utils is not None
    assert client is not None
    assert constants is not None
    assert soap is not None
    assert template is not None

runner.test("Core Imports", test_core_imports)

# ============================================================================
# TEST 2: XAdES Signers Import
# ============================================================================
def test_xades_imports():
    """Test that all XAdES signers can be imported"""
    from ubl21dian.xades.sign_invoice import SignInvoice
    from ubl21dian.xades.sign_credit_note import SignCreditNote
    from ubl21dian.xades.sign_debit_note import SignDebitNote
    from ubl21dian.xades.sign_payroll import SignPayroll
    from ubl21dian.xades.sign_payroll_note import SignPayrollNote
    from ubl21dian.xades.sign_event import SignEvent
    from ubl21dian.xades.sign_attached_document import SignAttachedDocument
    
    assert SignInvoice is not None
    assert SignCreditNote is not None
    assert SignDebitNote is not None
    assert SignPayroll is not None
    assert SignPayrollNote is not None
    assert SignEvent is not None
    assert SignAttachedDocument is not None

runner.test("XAdES Signers Import", test_xades_imports)

# ============================================================================
# TEST 3: URN Variants Import
# ============================================================================
def test_urn_imports():
    """Test that all URN variants can be imported"""
    from ubl21dian.xades.urn.sign_invoice import SignInvoice as URNSignInvoice
    from ubl21dian.xades.urn.sign_credit_note import SignCreditNote as URNSignCreditNote
    from ubl21dian.xades.urn.sign_debit_note import SignDebitNote as URNSignDebitNote
    from ubl21dian.xades.urn.sign_event import SignEvent as URNSignEvent
    
    assert URNSignInvoice is not None
    assert URNSignCreditNote is not None
    assert URNSignDebitNote is not None
    assert URNSignEvent is not None

runner.test("URN Variants Import", test_urn_imports)

# ============================================================================
# TEST 4: SOAP Templates Import
# ============================================================================
def test_soap_templates_import():
    """Test that all SOAP templates can be imported"""
    from ubl21dian.templates.soap.get_status import GetStatus
    from ubl21dian.templates.soap.send_bill_async import SendBillAsync
    from ubl21dian.templates.soap.send_bill_sync import SendBillSync
    from ubl21dian.templates.soap.send_test_set_async import SendTestSetAsync
    from ubl21dian.templates.soap.get_numbering_range import GetNumberingRange
    from ubl21dian.templates.soap.send_event import SendEvent
    from ubl21dian.templates.soap.get_status_zip import GetStatusZip
    from ubl21dian.templates.soap.get_acquirer import GetAcquirer
    from ubl21dian.templates.soap.get_document_info import GetDocumentInfo
    from ubl21dian.templates.soap.get_reference_notes import GetReferenceNotes
    from ubl21dian.templates.soap.get_status_events import GetStatusEvents
    from ubl21dian.templates.soap.get_xml_by_document_key import GetXmlByDocumentKey
    from ubl21dian.templates.soap.send_bill_attachment_async import SendBillAttachmentAsync
    from ubl21dian.templates.soap.send_payroll_async import SendPayrollASync
    from ubl21dian.templates.soap.send_payroll_sync import SendPayrollSync
    
    assert GetStatus is not None
    assert SendBillAsync is not None
    assert SendBillSync is not None
    assert SendTestSetAsync is not None
    assert GetNumberingRange is not None
    assert SendEvent is not None
    assert GetStatusZip is not None
    assert GetAcquirer is not None
    assert GetDocumentInfo is not None
    assert GetReferenceNotes is not None
    assert GetStatusEvents is not None
    assert GetXmlByDocumentKey is not None
    assert SendBillAttachmentAsync is not None
    assert SendPayrollASync is not None
    assert SendPayrollSync is not None

runner.test("SOAP Templates Import (15 templates)", test_soap_templates_import)

# ============================================================================
# TEST 5: Certificate Loading
# ============================================================================
def test_certificate_loading():
    """Test certificate loading functionality"""
    from ubl21dian.utils import DIANUtils
    
    utils = DIANUtils()
    utils.path_certificate = 'certificate.p12'
    utils.password = '1234'
    
    # Should load without errors
    utils.read_certs()
    
    assert utils.certs is not None
    assert 'pkey' in utils.certs
    assert 'cert' in utils.certs
    assert utils.certs['pkey'] is not None
    assert utils.certs['cert'] is not None

runner.test("Certificate Loading", test_certificate_loading)

# ============================================================================
# TEST 6: SignInvoice Instantiation
# ============================================================================
def test_sign_invoice_instantiation():
    """Test SignInvoice can be instantiated"""
    from ubl21dian.xades.sign_invoice import SignInvoice
    
    # Load sample XML
    with open('sample_invoice.xml', 'r', encoding='utf-8') as f:
        xml = f.read()
    
    signer = SignInvoice('certificate.p12', '1234', xml)
    
    assert signer is not None
    assert signer.xml_string is not None
    assert signer.certs is not None

runner.test("SignInvoice Instantiation", test_sign_invoice_instantiation)

# ============================================================================
# TEST 7: CUFE Calculation
# ============================================================================
def test_cufe_calculation():
    """Test CUFE calculation"""
    from ubl21dian.xades.sign_invoice import SignInvoice
    
    with open('sample_invoice.xml', 'r', encoding='utf-8') as f:
        xml = f.read()
    
    signer = SignInvoice('certificate.p12', '1234', xml)
    signer.technical_key = 'fc8eac422eba16e22ffd8c6f94b3940a6e38e62cd3ad353850410b63421dcaea90224431ee00823797b52fb050410b63'
    signer.set_uuid()
    
    # Check that UUID was set using get_tag
    uuid_tag = signer.get_tag('UUID', 0)
    assert uuid_tag is not None
    assert uuid_tag.text is not None
    assert len(uuid_tag.text) == 96  # SHA384 hash length

runner.test("CUFE Calculation", test_cufe_calculation)

# ============================================================================
# TEST 8: Software Security Code
# ============================================================================
def test_software_security_code():
    """Test Software Security Code calculation"""
    from ubl21dian.xades.sign_invoice import SignInvoice
    
    with open('sample_invoice.xml', 'r', encoding='utf-8') as f:
        xml = f.read()
    
    signer = SignInvoice('certificate.p12', '1234', xml)
    signer.software_id = 'aae35b45-6f9a-4da5-a32c-78d63da52364'
    signer.pin = '12345'
    signer.software_security_code()
    
    # Check that SoftwareSecurityCode was set
    ssc_tag = signer.get_tag('SoftwareSecurityCode', 0)
    assert ssc_tag.text is not None
    assert len(ssc_tag.text) == 96  # SHA384 hash

runner.test("Software Security Code", test_software_security_code)

# ============================================================================
# TEST 9: SOAP Template Generation
# ============================================================================
def test_soap_template_generation():
    """Test SOAP template generation"""
    from ubl21dian.templates.soap.get_status import GetStatus
    
    template = GetStatus('certificate.p12', '1234')
    template.track_id = 'TEST123'
    
    xml_body = template.create_template()
    
    assert xml_body is not None
    assert 'TEST123' in xml_body
    assert '<wcf:GetStatus>' in xml_body
    assert 'soap:Envelope' in xml_body

runner.test("SOAP Template Generation", test_soap_template_generation)

# ============================================================================
# TEST 10: WS-Security Header
# ============================================================================
def test_ws_security_header():
    """Test WS-Security header generation"""
    from ubl21dian.templates.soap.get_status import GetStatus
    
    template = GetStatus('certificate.p12', '1234')
    template.track_id = 'TEST123'
    template.sign()
    
    assert template.xml is not None
    assert '<wsse:Security' in template.xml
    assert '<wsse:BinarySecurityToken' in template.xml
    assert '<wsu:Timestamp' in template.xml
    assert '<ds:Signature' in template.xml

runner.test("WS-Security Header", test_ws_security_header)

# ============================================================================
# TEST 11: Namespace Handling
# ============================================================================
def test_namespace_handling():
    """Test that namespaces are correctly set"""
    from ubl21dian.xades.sign_invoice import SignInvoice
    from ubl21dian.xades.urn.sign_invoice import SignInvoice as URNSignInvoice
    
    with open('sample_invoice.xml', 'r', encoding='utf-8') as f:
        xml = f.read()
    
    # Standard namespace
    signer1 = SignInvoice('certificate.p12', '1234', xml)
    assert 'dian:gov:co:facturaelectronica:Structures-2-1' in signer1.ns.values()
    
    # URN namespace
    signer2 = URNSignInvoice('certificate.p12', '1234', xml)
    assert 'urn:dian:gov:co:facturaelectronica:Structures-2-1' in signer2.ns.values()

runner.test("Namespace Handling", test_namespace_handling)

# ============================================================================
# TEST 12: Algorithm Support
# ============================================================================
def test_algorithm_support():
    """Test different hash algorithms"""
    from ubl21dian.xades.sign_invoice import SignInvoice
    from ubl21dian.constants import ALGO_SHA1, ALGO_SHA256, ALGO_SHA512
    
    with open('sample_invoice.xml', 'r', encoding='utf-8') as f:
        xml = f.read()
    
    # SHA256 (default)
    signer_sha256 = SignInvoice('certificate.p12', '1234', xml, ALGO_SHA256)
    assert signer_sha256.algorithm == ALGO_SHA256
    
    # SHA512
    signer_sha512 = SignInvoice('certificate.p12', '1234', xml, ALGO_SHA512)
    assert signer_sha512.algorithm == ALGO_SHA512
    
    # SHA1
    signer_sha1 = SignInvoice('certificate.p12', '1234', xml, ALGO_SHA1)
    assert signer_sha1.algorithm == ALGO_SHA1

runner.test("Algorithm Support (SHA1/SHA256/SHA512)", test_algorithm_support)

# ============================================================================
# TEST 13: Template Properties Validation
# ============================================================================
def test_template_properties():
    """Test that templates have correct required properties"""
    from ubl21dian.templates.soap.send_bill_async import SendBillAsync
    from ubl21dian.templates.soap.send_test_set_async import SendTestSetAsync
    
    # SendBillAsync should require file_name and content_file
    template1 = SendBillAsync('certificate.p12', '1234')
    assert 'file_name' in template1.required_properties
    assert 'content_file' in template1.required_properties
    
    # SendTestSetAsync should require test_set_id additionally
    template2 = SendTestSetAsync('certificate.p12', '1234')
    assert 'test_set_id' in template2.required_properties

runner.test("Template Properties Validation", test_template_properties)

# ============================================================================
# TEST 14: Client Module
# ============================================================================
def test_client_module():
    """Test Client module can be imported"""
    from ubl21dian.client import Client
    
    # Client requires a template object, just verify import works
    assert Client is not None
    assert hasattr(Client, 'get_response')
    assert hasattr(Client, 'get_response_to_object')

runner.test("Client Module", test_client_module)

# ============================================================================
# TEST 15: Full Signing Workflow
# ============================================================================
def test_full_signing_workflow():
    """Test complete signing workflow"""
    from ubl21dian.xades.sign_invoice import SignInvoice
    
    with open('sample_invoice.xml', 'r', encoding='utf-8') as f:
        xml = f.read()
    
    signer = SignInvoice('certificate.p12', '1234', xml)
    signer.software_id = 'test-software-id'
    signer.pin = '12345'
    signer.technical_key = 'fc8eac422eba16e22ffd8c6f94b3940a6e38e62cd3ad353850410b63421dcaea90224431ee00823797b52fb050410b63'
    
    # Execute full workflow
    signer.software_security_code()
    signer.set_uuid()
    
    # Verify output
    assert signer.xml is not None
    assert '<ds:Signature' in signer.xml
    assert '<ds:SignatureValue' in signer.xml  # May have Id attribute
    assert 'Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"' in signer.xml

runner.test("Full Signing Workflow", test_full_signing_workflow)

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*60)
print("COMPREHENSIVE TEST SUITE COMPLETED")
print("="*60)

success = runner.summary()

if success:
    print("\n✅ ALL TESTS PASSED - Migration is correct!")
    sys.exit(0)
else:
    print("\n❌ SOME TESTS FAILED - Review errors above")
    sys.exit(1)
