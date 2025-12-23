"""
SignAttachedDocument - XAdES Signature for AttachedDocument
"""
from .sign_invoice import SignInvoice
from ..constants import XMLDSIG


class SignAttachedDocument(SignInvoice):
    """Sign Attached Document XAdES for DIAN Colombia"""
    
    def __init__(self, path_certificate=None, password=None, xml_string=None, 
                 algorithm=None, software_id=None, pin=None, technical_key=None):
        
        # Override namespace for AttachedDocument
        self.ns = {
            'xmlns:cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'xmlns:ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
            'xmlns:cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'xmlns:sts': 'dian:gov:co:facturaelectronica:Structures-2-1',
            'xmlns': 'urn:oasis:names:specification:ubl:schema:xsd:AttachedDocument-2',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xmlns:xades141': 'http://uri.etsi.org/01903/v1.4.1#',
            'xmlns:xades': 'http://uri.etsi.org/01903/v1.3.2#',
            'xmlns:ds': XMLDSIG
        }
        
        super().__init__(path_certificate, password, xml_string, algorithm, 
                        software_id, pin, technical_key)
