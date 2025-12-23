
# XML Namespaces
XMLDSIG = 'http://www.w3.org/2000/09/xmldsig#'
POLITICA_FIRMA_V2 = 'https://facturaelectronica.dian.gov.co/politicadefirma/v2/politicadefirmav2.pdf'
POLITICA_FIRMA_V2_VALUE = 'dMoMvtcG5aIzgYo0tIsSQeVJBDnUnfSOfBpxXrmor0Y='
C14N = 'http://www.w3.org/TR/2001/REC-xml-c14n-20010315'
ENVELOPED_SIGNATURE = 'http://www.w3.org/2000/09/xmldsig#enveloped-signature'
SIGNED_PROPERTIES = 'http://uri.etsi.org/01903#SignedProperties'

NAMESPACES = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'sts': 'dian:gov:co:facturaelectronica:Structures-2-1',
    'inv': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2', # Prefix 'inv' to avoid conflict with default ns
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'xades141': 'http://uri.etsi.org/01903/v1.4.1#',
    'xades': 'http://uri.etsi.org/01903/v1.3.2#',
    'ds': XMLDSIG,
    'wsa': 'http://www.w3.org/2005/08/addressing',
    'soap': 'http://www.w3.org/2003/05/soap-envelope',
    'wcf': 'http://wcf.dian.colombia',
    'wsse': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd',
    'wsu': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd',
    'ec': 'http://www.w3.org/2001/10/xml-exc-c14n#'
}

# SOAP Constants
SOAP_ENV = 'http://www.w3.org/2003/05/soap-envelope'
WSS_WSSECURITY = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'
WSS_WSSECURITY_UTILITY = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'
EXC_C14N = 'http://www.w3.org/2001/10/xml-exc-c14n#'
RSA_SHA256 = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
SHA256 = 'http://www.w3.org/2001/04/xmlenc#sha256'
X509V3 = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3'
BASE64BINARY = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary'


# Algorithms
ALGO_SHA1 = {
    'rsa': 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha1',
    'algorithm': 'http://www.w3.org/2001/04/xmlenc#sha1',
    'hash': 'sha1',
}

ALGO_SHA256 = {
    'rsa': 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256',
    'algorithm': 'http://www.w3.org/2001/04/xmlenc#sha256',
    'hash': 'sha256',
}

ALGO_SHA512 = {
    'rsa': 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha512',
    'algorithm': 'http://www.w3.org/2001/04/xmlenc#sha512',
    'hash': 'sha512',
}
