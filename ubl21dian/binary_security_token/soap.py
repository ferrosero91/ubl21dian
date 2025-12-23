"""
SOAP - WS-Security SOAP signing for DIAN
Ported from PHP BinarySecurityToken/SOAP class
"""
from datetime import datetime, timezone
import time
import hashlib
import base64
from lxml import etree
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from ..sign import Sign
from ..constants import *


class SOAP(Sign):
    """SOAP WS-Security signing class"""
    
    # Constants matching PHP
    ADDRESSING = 'http://www.w3.org/2005/08/addressing'
    SOAP_ENVELOPE = 'http://www.w3.org/2003/05/soap-envelope'
    DIAN_COLOMBIA = 'http://wcf.dian.colombia'
    XMLDSIG = 'http://www.w3.org/2000/09/xmldsig#'
    WSS_WSSECURITY = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'
    WSS_WSSECURITY_UTILITY = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'
    EXC_C14N = 'http://www.w3.org/2001/10/xml-exc-c14n#'
    RSA_SHA256 = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
    SHA256 = 'http://www.w3.org/2001/04/xmlenc#sha256'
    X509V3 = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3'
    BASE64BINARY = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary'
    
    def __init__(self, path_certificate=None, password=None, xml_string=None):
        # IDs - must be set BEFORE calling parent __init__
        self.ids = {
            'wsuBinarySecurityTokenID': 'TORRESOFTWARE',
            'securityTokenReferenceID': 'STR',
            'signatureID': 'SIG',
            'timestampID': 'TS',
            'keyInfoID': 'KI',
            'wsuIDTo': 'ID',
        }
        
        # Namespace maps for C14N - matching PHP exactly
        self.toNS = {
            'xmlns:wsa': self.ADDRESSING,
            'xmlns:soap': self.SOAP_ENVELOPE,
            'xmlns:wcf': self.DIAN_COLOMBIA,
        }
        
        self.signedInfoNS = {
            'xmlns:ds': self.XMLDSIG,
            'xmlns:wsa': self.ADDRESSING,
            'xmlns:soap': self.SOAP_ENVELOPE,
            'xmlns:wcf': self.DIAN_COLOMBIA,
        }

        self.CurrentTime = int(time.time())
        self.TimeToLive = 60000
        self.To = None
        self.Action = None
        
        # Initialize parent (will call read_certs and identifiers_references)
        super().__init__(path_certificate, password, None)
        
        # If xml_string provided, sign it
        if xml_string:
            self.sign(xml_string)

    def load_xml(self):
        """Load and sign SOAP XML with WS-Security - mirrors PHP loadXML()"""
        # Convert to string if DOMDocument equivalent
        if isinstance(self.xml_string, (etree._Element, etree._ElementTree)):
            self.xml_string = etree.tostring(self.xml_string, encoding=self.encoding).decode(self.encoding)

        # Parse the input XML
        self.domDocument = etree.fromstring(self.xml_string.encode(self.encoding))
        
        # Remove existing Header
        self.remove_child('Header')
        
        # Build the header structure as string (like PHP does with prefixes)
        # This ensures we get the exact prefix format PHP produces
        
        action_value = self.Action if self.Action else 'http://wcf.dian.colombia/IWcfDianCustomerServices/GetStatus'
        to_value = self.To if self.To else 'https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc'
        
        created_time = datetime.utcfromtimestamp(self.CurrentTime).strftime('%Y-%m-%dT%H:%M:%SZ')
        expires_time = datetime.utcfromtimestamp(self.CurrentTime + self.TimeToLive).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        x509_cert = self.x509_export()
        
        # Build wsa:To element for digest calculation
        self.to_xml = f'<wsa:To wsu:Id="{self.wsuIDTo}" xmlns:wsu="{self.WSS_WSSECURITY_UTILITY}">{to_value}</wsa:To>'
        
        # Calculate DigestValue
        digest_value = self._calculate_digest_value()
        
        # Build SignedInfo for signature calculation
        self.signed_info_xml = f'''<ds:SignedInfo><ds:CanonicalizationMethod Algorithm="{self.EXC_C14N}"><ec:InclusiveNamespaces PrefixList="wsa soap wcf" xmlns:ec="{self.EXC_C14N}"/></ds:CanonicalizationMethod><ds:SignatureMethod Algorithm="{self.RSA_SHA256}"/><ds:Reference URI="#{self.wsuIDTo}"><ds:Transforms><ds:Transform Algorithm="{self.EXC_C14N}"><ec:InclusiveNamespaces PrefixList="soap wcf" xmlns:ec="{self.EXC_C14N}"/></ds:Transform></ds:Transforms><ds:DigestMethod Algorithm="{self.SHA256}"/><ds:DigestValue>{digest_value}</ds:DigestValue></ds:Reference></ds:SignedInfo>'''
        
        # Calculate SignatureValue
        signature_value = self._calculate_signature_value()
        
        # Build complete header
        header_xml = f'''<soap:Header xmlns:soap="{self.SOAP_ENVELOPE}" xmlns:wsa="{self.ADDRESSING}"><wsse:Security xmlns:wsse="{self.WSS_WSSECURITY}" xmlns:wsu="{self.WSS_WSSECURITY_UTILITY}"><wsu:Timestamp wsu:Id="{self.timestampID}"><wsu:Created>{created_time}</wsu:Created><wsu:Expires>{expires_time}</wsu:Expires></wsu:Timestamp><wsse:BinarySecurityToken EncodingType="{self.BASE64BINARY}" ValueType="{self.X509V3}" wsu:Id="{self.wsuBinarySecurityTokenID}">{x509_cert}</wsse:BinarySecurityToken><ds:Signature Id="{self.signatureID}" xmlns:ds="{self.XMLDSIG}">{self.signed_info_xml}<ds:SignatureValue>{signature_value}</ds:SignatureValue><ds:KeyInfo Id="{self.keyInfoID}"><wsse:SecurityTokenReference wsu:Id="{self.securityTokenReferenceID}"><wsse:Reference URI="#{self.wsuBinarySecurityTokenID}" ValueType="{self.X509V3}"/></wsse:SecurityTokenReference></ds:KeyInfo></ds:Signature></wsse:Security><wsa:Action>{action_value}</wsa:Action><wsa:To wsu:Id="{self.wsuIDTo}" xmlns:wsu="{self.WSS_WSSECURITY_UTILITY}">{to_value}</wsa:To></soap:Header>'''
        
        # Parse header and insert into document
        header_elem = etree.fromstring(header_xml.encode('utf-8'))
        self.domDocument.insert(0, header_elem)
        
        # Update dom_document for parent class
        self.dom_document = self.domDocument

    def _calculate_digest_value(self):
        """Calculate DigestValue for wsa:To element"""
        # Add namespaces via str_replace (exactly like PHP)
        ns_str = self.join_array(self.toNS)
        modified_xml = self.to_xml.replace('<wsa:To ', '<wsa:To ' + ns_str + ' ', 1)
        
        # Load into document and C14N
        temp_doc = etree.fromstring(modified_xml.encode('utf-8'))
        c14n_bytes = etree.tostring(temp_doc, method='c14n')
        
        # Hash
        digest = base64.b64encode(hashlib.sha256(c14n_bytes).digest()).decode('utf-8')
        return digest

    def _calculate_signature_value(self):
        """Calculate SignatureValue for SignedInfo"""
        # Add namespaces via str_replace (exactly like PHP)
        ns_str = self.join_array(self.signedInfoNS)
        modified_xml = self.signed_info_xml.replace('<ds:SignedInfo', '<ds:SignedInfo ' + ns_str, 1)
        
        # Load into document and C14N
        temp_doc = etree.fromstring(modified_xml.encode('utf-8'))
        c14n_bytes = etree.tostring(temp_doc, method='c14n')
        
        # Sign with RSA-SHA256
        private_key = self.certs['pkey']
        signature = private_key.sign(c14n_bytes, padding.PKCS1v15(), hashes.SHA256())
        
        # Base64 encode
        return base64.b64encode(signature).decode('utf-8')

    def remove_child(self, tag_name, item=0):
        """Remove child element by local name"""
        if self.domDocument is None:
            return
        
        # Find elements with matching local name using XPath
        results = self.domDocument.xpath(f".//*[local-name() = '{tag_name}']")
        if results and len(results) > item:
            elem = results[item]
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)
