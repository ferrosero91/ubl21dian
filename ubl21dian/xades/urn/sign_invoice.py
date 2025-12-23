"""
SignInvoice URN variant - with urn: namespace prefix
"""
from ..sign_invoice import SignInvoice as BaseSignInvoice
from ...constants import XMLDSIG


class SignInvoice(BaseSignInvoice):
    """URN variant of SignInvoice with urn: namespace prefix"""
    
    def __init__(self, path_certificate=None, password=None, xml_string=None, 
                 algorithm=None, software_id=None, pin=None, technical_key=None):
        
        super().__init__(path_certificate, password, xml_string, algorithm,
                        software_id, pin, technical_key)
        
        # Override with URN namespace
        self.ns = {
            'xmlns:cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'xmlns:ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
            'xmlns:cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'xmlns:sts': 'urn:dian:gov:co:facturaelectronica:Structures-2-1',
            'xmlns': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xmlns:xades141': 'http://uri.etsi.org/01903/v1.4.1#',
            'xmlns:xades': 'http://uri.etsi.org/01903/v1.3.2#',
            'xmlns:ds': XMLDSIG
        }
