"""
SignInvoice - XAdES Signature for DIAN Colombia
Ported from PHP ubl21dian/XAdES/SignInvoice.php
"""
from datetime import datetime
import base64
import hashlib
from lxml import etree
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import Encoding

from ..sign import Sign
from ..constants import *


class SignInvoice(Sign):
    """Sign Invoice XAdES for DIAN Colombia"""
    
    # Constants matching PHP
    XMLDSIG = 'http://www.w3.org/2000/09/xmldsig#'
    POLITICA_FIRMA_V2 = 'https://facturaelectronica.dian.gov.co/politicadefirma/v2/politicadefirmav2.pdf'
    POLITICA_FIRMA_V2_VALUE = 'dMoMvtcG5aIzgYo0tIsSQeVJBDnUnfSOfBpxXrmor0Y='
    C14N = 'http://www.w3.org/TR/2001/REC-xml-c14n-20010315'
    ENVELOPED_SIGNATURE = 'http://www.w3.org/2000/09/xmldsig#enveloped-signature'
    SIGNED_PROPERTIES = 'http://uri.etsi.org/01903#SignedProperties'
    
    # Algorithm constants
    ALGO_SHA1 = ALGO_SHA1
    ALGO_SHA256 = ALGO_SHA256
    ALGO_SHA512 = ALGO_SHA512
    
    def __init__(self, path_certificate=None, password=None, xml_string=None, 
                 algorithm=None, software_id=None, pin=None, technical_key=None):
        
        # IDs - must be set BEFORE calling parent __init__
        self.ids = {
            'SignedPropertiesID': 'SIGNED-PROPS',
            'SignatureValueID': 'SIG-VALUE',
            'SignatureID': 'TORRESOFTWARE',
            'KeyInfoID': 'KEY-INFO',
            'ReferenceID': 'REF',
        }
        
        # Namespaces - matches PHP exactly
        self.ns = {
            'xmlns:cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'xmlns:ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
            'xmlns:cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
            'xmlns:sts': 'dian:gov:co:facturaelectronica:Structures-2-1',
            'xmlns': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xmlns:xades141': 'http://uri.etsi.org/01903/v1.4.1#',
            'xmlns:xades': 'http://uri.etsi.org/01903/v1.3.2#',
            'xmlns:ds': self.XMLDSIG
        }

        self.algorithm = algorithm if algorithm else self.ALGO_SHA256
        self.softwareID = software_id
        self.pin = pin
        self.technicalKey = technical_key
        self.groupOfTotals = 'LegalMonetaryTotal'
        self.GuardarEn = False
        
        # Call parent constructor
        super().__init__(path_certificate, password, xml_string)

    def load_xml(self):
        """Load and sign XML document - mirrors PHP loadXML()"""
        # Convert to string if needed
        if isinstance(self.xml_string, (etree._Element, etree._ElementTree)):
            self.xml_string = etree.tostring(self.xml_string, encoding=self.encoding).decode(self.encoding)
        
        # Create DOM Document
        self.domDocument = etree.fromstring(self.xml_string.encode(self.encoding))
        self.dom_document = self.domDocument
        
        # Save before signing if requested
        if self.GuardarEn:
            guardar_en = str(self.GuardarEn).replace('\r\n', '').replace('\n', '').replace('\r', '')
            with open(guardar_en, 'w', encoding='utf-8') as f:
                f.write(self.xml_string)
        
        # Create DOMXPath equivalent (register namespaces)
        self.domXPath = self.domDocument
        
        # Software security code
        self.softwareSecurityCode()
        
        # UUID calculation based on document type
        if '</NominaIndividual>' in self.xml_string or '</NominaIndividualDeAjuste>' in self.xml_string:
            self.setCUNE()
        elif '</ApplicationResponse>' in self.xml_string and '</AttachedDocument>' not in self.xml_string:
            self.setCUDEEVENT()
        else:
            self.setUUID()
        
        # Calculate digest of XML before adding signature
        self.digestValueXML()
        
        # Find ExtensionContent to append signature
        self._findExtensionContent()
        
        # Build signature structure
        self._buildSignature()

    def _findExtensionContent(self):
        """Find the correct ExtensionContent element for signature"""
        extension_contents = self._find_elements_by_tag_name('ExtensionContent', self.domDocument)
        
        if '</NominaIndividual>' in self.xml_string or '</NominaIndividualDeAjuste>' in self.xml_string or '</AttachedDocument>' in self.xml_string:
            self.extensionContentSing = extension_contents[0] if extension_contents else None
        elif 'www.minsalud.gov.co' in self.xml_string and len(extension_contents) > 2:
            self.extensionContentSing = extension_contents[2]
        elif 'DIAN 2.1: Documento Equivalente POS' in self.xml_string and len(extension_contents) > 4:
            self.extensionContentSing = extension_contents[4]
        elif 'DIAN 2.1: Documento Equivalente Tiquete de Transporte Terrestre de Pasajeros' in self.xml_string and len(extension_contents) > 3:
            self.extensionContentSing = extension_contents[3]
        elif 'DIAN 2.1: Boleta de ingreso a cine' in self.xml_string and len(extension_contents) > 3:
            self.extensionContentSing = extension_contents[3]
        elif 'DIAN 2.1: Documento Equivalente SPD' in self.xml_string and extension_contents:
            self.extensionContentSing = extension_contents[-1]
        elif len(extension_contents) > 1:
            self.extensionContentSing = extension_contents[1]
        elif extension_contents:
            self.extensionContentSing = extension_contents[0]
        else:
            raise Exception("No ExtensionContent found in document")

    def _buildSignature(self):
        """Build the complete ds:Signature structure - mirrors PHP loadXML()"""
        # Define namespaces
        DS_NS = self.XMLDSIG
        XADES_NS = 'http://uri.etsi.org/01903/v1.3.2#'
        
        # Create ds:Signature using Clark notation {namespace}localname
        self.signature = etree.SubElement(self.extensionContentSing, '{%s}Signature' % DS_NS)
        self.signature.set('Id', self.SignatureID)
        
        # Create ds:SignedInfo
        self.signedInfo = etree.SubElement(self.signature, '{%s}SignedInfo' % DS_NS)
        
        # Create ds:SignatureValue placeholder
        self.signatureValue = etree.SubElement(self.signature, '{%s}SignatureValue' % DS_NS)
        self.signatureValue.set('Id', self.SignatureValueID)
        self.signatureValue.text = 'ERROR!'
        
        # Create ds:KeyInfo
        self.keyInfo = etree.SubElement(self.signature, '{%s}KeyInfo' % DS_NS)
        self.keyInfo.set('Id', self.KeyInfoID)
        
        X509Data = etree.SubElement(self.keyInfo, '{%s}X509Data' % DS_NS)
        X509Certificate = etree.SubElement(X509Data, '{%s}X509Certificate' % DS_NS)
        X509Certificate.text = self.x509_export()
        
        # Create ds:Object with xades:QualifyingProperties
        obj = etree.SubElement(self.signature, '{%s}Object' % DS_NS)
        
        qualifyingProperties = etree.SubElement(obj, '{%s}QualifyingProperties' % XADES_NS)
        qualifyingProperties.set('Target', '#' + self.SignatureID)
        
        signedProperties = etree.SubElement(qualifyingProperties, '{%s}SignedProperties' % XADES_NS)
        signedProperties.set('Id', self.SignedPropertiesID)
        self.signedProperties = signedProperties
        
        signedSignatureProperties = etree.SubElement(signedProperties, '{%s}SignedSignatureProperties' % XADES_NS)
        
        # SigningTime
        signingTime = etree.SubElement(signedSignatureProperties, '{%s}SigningTime' % XADES_NS)
        now = datetime.now()
        signingTime.text = now.strftime('%Y-%m-%dT%H:%M:%S.') + f'{now.microsecond // 1000:03d}-05:00'
        
        # SigningCertificate
        self._buildSigningCertificate(signedSignatureProperties)
        
        # SignaturePolicyIdentifier
        self._buildPolicyIdentifier(signedSignatureProperties)
        
        # SignerRole
        signerRole = etree.SubElement(signedSignatureProperties, '{%s}SignerRole' % XADES_NS)
        claimedRoles = etree.SubElement(signerRole, '{%s}ClaimedRoles' % XADES_NS)
        claimedRole = etree.SubElement(claimedRoles, '{%s}ClaimedRole' % XADES_NS)
        claimedRole.text = 'supplier'
        
        # Build SignedInfo content
        self._buildSignedInfo()
        
        # Calculate and set SignatureValue
        self._calculateSignatureValue()

    def _buildSigningCertificate(self, parent):
        """Build xades:SigningCertificate"""
        DS_NS = self.XMLDSIG
        XADES_NS = 'http://uri.etsi.org/01903/v1.3.2#'
        
        signingCertificate = etree.SubElement(parent, '{%s}SigningCertificate' % XADES_NS)
        
        # Main certificate
        cert = etree.SubElement(signingCertificate, '{%s}Cert' % XADES_NS)
        certDigest = etree.SubElement(cert, '{%s}CertDigest' % XADES_NS)
        
        digestMethod = etree.SubElement(certDigest, '{%s}DigestMethod' % DS_NS)
        digestMethod.set('Algorithm', self.algorithm['algorithm'])
        
        # Calculate cert fingerprint
        cert_der = self.certs['cert'].public_bytes(Encoding.DER)
        h = hashlib.new(self.algorithm['hash'])
        h.update(cert_der)
        
        digestValue = etree.SubElement(certDigest, '{%s}DigestValue' % DS_NS)
        digestValue.text = base64.b64encode(h.digest()).decode('utf-8')
        
        # IssuerSerial
        issuerSerial = etree.SubElement(cert, '{%s}IssuerSerial' % XADES_NS)
        X509IssuerName = etree.SubElement(issuerSerial, '{%s}X509IssuerName' % DS_NS)
        X509IssuerName.text = self._getIssuerString(self.certs['cert'].issuer)
        
        X509SerialNumber = etree.SubElement(issuerSerial, '{%s}X509SerialNumber' % DS_NS)
        X509SerialNumber.text = str(self.certs['cert'].serial_number)
        
        # Extra certificates
        if self.certs.get('extracerts'):
            for extracert in self.certs['extracerts']:
                self._addExtraCert(signingCertificate, extracert)

    def _addExtraCert(self, parent, extracert):
        """Add extra certificate to SigningCertificate"""
        DS_NS = self.XMLDSIG
        XADES_NS = 'http://uri.etsi.org/01903/v1.3.2#'
        
        cert = etree.SubElement(parent, '{%s}Cert' % XADES_NS)
        certDigest = etree.SubElement(cert, '{%s}CertDigest' % XADES_NS)
        
        digestMethod = etree.SubElement(certDigest, '{%s}DigestMethod' % DS_NS)
        digestMethod.set('Algorithm', self.algorithm['algorithm'])
        
        cert_der = extracert.public_bytes(Encoding.DER)
        h = hashlib.new(self.algorithm['hash'])
        h.update(cert_der)
        
        digestValue = etree.SubElement(certDigest, '{%s}DigestValue' % DS_NS)
        digestValue.text = base64.b64encode(h.digest()).decode('utf-8')
        
        issuerSerial = etree.SubElement(cert, '{%s}IssuerSerial' % XADES_NS)
        X509IssuerName = etree.SubElement(issuerSerial, '{%s}X509IssuerName' % DS_NS)
        X509IssuerName.text = self._getIssuerString(extracert.issuer)
        
        X509SerialNumber = etree.SubElement(issuerSerial, '{%s}X509SerialNumber' % DS_NS)
        X509SerialNumber.text = str(extracert.serial_number)

    def _getIssuerString(self, issuer):
        """Get issuer string in PHP format: reversed, comma-separated"""
        oid_map = {
            'countryName': 'C',
            'stateOrProvinceName': 'ST',
            'localityName': 'L',
            'organizationName': 'O',
            'organizationalUnitName': 'OU',
            'commonName': 'CN',
            'emailAddress': 'emailAddress',
            'serialNumber': 'serialNumber',
        }
        
        parts = []
        for attr in reversed(list(issuer)):
            name = oid_map.get(attr.oid._name, attr.oid._name)
            parts.append(f'{name}={attr.value}')
        
        return ','.join(parts)

    def _buildPolicyIdentifier(self, parent):
        """Build xades:SignaturePolicyIdentifier"""
        DS_NS = self.XMLDSIG
        XADES_NS = 'http://uri.etsi.org/01903/v1.3.2#'
        
        policyId = etree.SubElement(parent, '{%s}SignaturePolicyIdentifier' % XADES_NS)
        sigPolicyId = etree.SubElement(policyId, '{%s}SignaturePolicyId' % XADES_NS)
        
        sigPolicyIdNode = etree.SubElement(sigPolicyId, '{%s}SigPolicyId' % XADES_NS)
        identifier = etree.SubElement(sigPolicyIdNode, '{%s}Identifier' % XADES_NS)
        identifier.text = self.POLITICA_FIRMA_V2
        
        sigPolicyHash = etree.SubElement(sigPolicyId, '{%s}SigPolicyHash' % XADES_NS)
        digestMethod = etree.SubElement(sigPolicyHash, '{%s}DigestMethod' % DS_NS)
        digestMethod.set('Algorithm', self.algorithm['algorithm'])
        
        digestValue = etree.SubElement(sigPolicyHash, '{%s}DigestValue' % DS_NS)
        digestValue.text = self.POLITICA_FIRMA_V2_VALUE

    def _buildSignedInfo(self):
        """Build ds:SignedInfo content"""
        DS_NS = self.XMLDSIG
        
        # CanonicalizationMethod
        canonMethod = etree.SubElement(self.signedInfo, '{%s}CanonicalizationMethod' % DS_NS)
        canonMethod.set('Algorithm', self.C14N)
        
        # SignatureMethod
        sigMethod = etree.SubElement(self.signedInfo, '{%s}SignatureMethod' % DS_NS)
        sigMethod.set('Algorithm', self.algorithm['rsa'])
        
        # Reference to XML document
        referenceXML = etree.SubElement(self.signedInfo, '{%s}Reference' % DS_NS)
        referenceXML.set('Id', self.ReferenceID)
        referenceXML.set('URI', '')
        
        transformsXML = etree.SubElement(referenceXML, '{%s}Transforms' % DS_NS)
        transformXML = etree.SubElement(transformsXML, '{%s}Transform' % DS_NS)
        transformXML.set('Algorithm', self.ENVELOPED_SIGNATURE)
        
        digestMethodXML = etree.SubElement(referenceXML, '{%s}DigestMethod' % DS_NS)
        digestMethodXML.set('Algorithm', self.algorithm['algorithm'])
        
        digestValueXML = etree.SubElement(referenceXML, '{%s}DigestValue' % DS_NS)
        digestValueXML.text = self.DigestValueXML
        
        # Reference to KeyInfo
        self._addKeyInfoReference()
        
        # Reference to SignedProperties
        self._addSignedPropertiesReference()

    def _addKeyInfoReference(self):
        """Add reference to KeyInfo in SignedInfo - mirrors PHP logic"""
        DS_NS = self.XMLDSIG
        
        # PHP: str_replace('<ds:KeyInfo ', "<ds:KeyInfo {$this->joinArray($this->ns)} ", $this->domDocument->saveXML($this->keyInfo))
        keyInfo_xml = etree.tostring(self.keyInfo, encoding='unicode')
        # lxml outputs {namespace}localname, we need to convert to prefix:localname
        keyInfo_xml = self._convertToPrefix(keyInfo_xml)
        
        # Build namespace string excluding namespaces already present in the element
        ns_to_add = {}
        for k, v in self.ns.items():
            # Check if this namespace declaration is already in the XML
            if f'{k}=' not in keyInfo_xml:
                ns_to_add[k] = v
        ns_str = self.join_array(ns_to_add)
        
        if ns_str:
            modified_xml = keyInfo_xml.replace('<ds:KeyInfo ', '<ds:KeyInfo ' + ns_str + ' ', 1)
        else:
            modified_xml = keyInfo_xml
        
        # Handle Nomina namespace swap if needed
        DigestValueKeyInfo = self._calculateC14NDigestWithNominaSwap(modified_xml)
        
        referenceKeyInfo = etree.SubElement(self.signedInfo, '{%s}Reference' % DS_NS)
        referenceKeyInfo.set('URI', '#' + self.KeyInfoID)
        
        digestMethod = etree.SubElement(referenceKeyInfo, '{%s}DigestMethod' % DS_NS)
        digestMethod.set('Algorithm', self.algorithm['algorithm'])
        
        digestValue = etree.SubElement(referenceKeyInfo, '{%s}DigestValue' % DS_NS)
        digestValue.text = DigestValueKeyInfo

    def _addSignedPropertiesReference(self):
        """Add reference to SignedProperties in SignedInfo - mirrors PHP logic"""
        DS_NS = self.XMLDSIG
        
        # PHP: str_replace('<xades:SignedProperties ', "<xades:SignedProperties {$this->joinArray($this->ns)} ", ...)
        sp_xml = etree.tostring(self.signedProperties, encoding='unicode')
        sp_xml = self._convertToPrefix(sp_xml)
        
        # Build namespace string excluding namespaces already present in the element
        ns_to_add = {}
        for k, v in self.ns.items():
            # Check if this namespace declaration is already in the XML
            if f'{k}=' not in sp_xml:
                ns_to_add[k] = v
        ns_str = self.join_array(ns_to_add)
        
        if ns_str:
            modified_xml = sp_xml.replace('<xades:SignedProperties ', '<xades:SignedProperties ' + ns_str + ' ', 1)
        else:
            modified_xml = sp_xml
        
        DigestValueSignedProperties = self._calculateC14NDigestWithNominaSwap(modified_xml)
        
        referenceSignedProperties = etree.SubElement(self.signedInfo, '{%s}Reference' % DS_NS)
        referenceSignedProperties.set('Type', self.SIGNED_PROPERTIES)
        referenceSignedProperties.set('URI', '#' + self.SignedPropertiesID)
        
        digestMethod = etree.SubElement(referenceSignedProperties, '{%s}DigestMethod' % DS_NS)
        digestMethod.set('Algorithm', self.algorithm['algorithm'])
        
        digestValue = etree.SubElement(referenceSignedProperties, '{%s}DigestValue' % DS_NS)
        digestValue.text = DigestValueSignedProperties

    def _convertToPrefix(self, xml_str):
        """Convert Clark notation {namespace}localname to prefix:localname"""
        # Map namespaces to prefixes
        ns_map = {
            '{http://www.w3.org/2000/09/xmldsig#}': 'ds:',
            '{http://uri.etsi.org/01903/v1.3.2#}': 'xades:',
            '{http://uri.etsi.org/01903/v1.4.1#}': 'xades141:',
        }
        
        result = xml_str
        for ns, prefix in ns_map.items():
            result = result.replace(ns, prefix)
        
        return result

    def _calculateC14NDigestWithNominaSwap(self, xml_str):
        """Calculate C14N digest with Nomina namespace swap if needed - mirrors PHP logic"""
        if '</NominaIndividual>' in self.xml_string:
            SearchNS = 'xmlns="dian:gov:co:facturaelectronica:NominaIndividual"'
            ReplacementNS = 'xmlns="urn:dian:gov:co:facturaelectronica:NominaIndividual"'
        elif '</NominaIndividualDeAjuste>' in self.xml_string:
            SearchNS = 'xmlns="dian:gov:co:facturaelectronica:NominaIndividualDeAjuste"'
            ReplacementNS = 'xmlns="urn:dian:gov:co:facturaelectronica:NominaIndividualDeAjuste"'
        else:
            # Standard case - no swap needed
            temp_doc = etree.fromstring(xml_str.encode('utf-8'))
            c14n = etree.tostring(temp_doc, method='c14n')
            h = hashlib.new(self.algorithm['hash'])
            h.update(c14n)
            return base64.b64encode(h.digest()).decode('utf-8')
        
        # Nomina case - swap namespaces for C14N
        CopyOf = xml_str
        modified = xml_str.replace(SearchNS, ReplacementNS)
        temp_doc = etree.fromstring(modified.encode('utf-8'))
        c14n_str = etree.tostring(temp_doc, method='c14n').decode('utf-8')
        
        # Swap back
        if '</NominaIndividual>' in self.xml_string:
            SearchNS2 = 'xmlns="urn:dian:gov:co:facturaelectronica:NominaIndividual"'
            ReplacementNS2 = 'xmlns="dian:gov:co:facturaelectronica:NominaIndividual"'
        else:
            SearchNS2 = 'xmlns="urn:dian:gov:co:facturaelectronica:NominaIndividualDeAjuste"'
            ReplacementNS2 = 'xmlns="dian:gov:co:facturaelectronica:NominaIndividualDeAjuste"'
        
        c14n_str = c14n_str.replace(SearchNS2, ReplacementNS2)
        
        h = hashlib.new(self.algorithm['hash'])
        h.update(c14n_str.encode('utf-8'))
        return base64.b64encode(h.digest()).decode('utf-8')

    def _calculateSignatureValue(self):
        """Calculate and set SignatureValue - mirrors PHP logic"""
        DS_NS = self.XMLDSIG
        
        # PHP: str_replace('<ds:SignedInfo', "<ds:SignedInfo {$this->joinArray($this->ns)} ", ...)
        si_xml = etree.tostring(self.signedInfo, encoding='unicode')
        si_xml = self._convertToPrefix(si_xml)
        
        # Build namespace string excluding namespaces already present in the element
        ns_to_add = {}
        for k, v in self.ns.items():
            # Check if this namespace declaration is already in the XML
            if f'{k}=' not in si_xml:
                ns_to_add[k] = v
        ns_str = self.join_array(ns_to_add)
        
        if ns_str:
            modified_xml = si_xml.replace('<ds:SignedInfo', '<ds:SignedInfo ' + ns_str, 1)
        else:
            modified_xml = si_xml
        
        # Handle Nomina namespace swap
        if '</NominaIndividual>' in self.xml_string:
            SearchNS = 'xmlns="dian:gov:co:facturaelectronica:NominaIndividual"'
            ReplacementNS = 'xmlns="urn:dian:gov:co:facturaelectronica:NominaIndividual"'
            modified_xml = modified_xml.replace(SearchNS, ReplacementNS)
            temp_doc = etree.fromstring(modified_xml.encode('utf-8'))
            c14n = etree.tostring(temp_doc, method='c14n').decode('utf-8')
            c14n = c14n.replace(ReplacementNS, SearchNS)
            data_to_sign = c14n.encode('utf-8')
        elif '</NominaIndividualDeAjuste>' in self.xml_string:
            SearchNS = 'xmlns="dian:gov:co:facturaelectronica:NominaIndividualDeAjuste"'
            ReplacementNS = 'xmlns="urn:dian:gov:co:facturaelectronica:NominaIndividualDeAjuste"'
            modified_xml = modified_xml.replace(SearchNS, ReplacementNS)
            temp_doc = etree.fromstring(modified_xml.encode('utf-8'))
            c14n = etree.tostring(temp_doc, method='c14n').decode('utf-8')
            c14n = c14n.replace(ReplacementNS, SearchNS)
            data_to_sign = c14n.encode('utf-8')
        else:
            temp_doc = etree.fromstring(modified_xml.encode('utf-8'))
            data_to_sign = etree.tostring(temp_doc, method='c14n')
        
        # Sign with private key
        private_key = self.certs['pkey']
        hash_algo = getattr(hashes, self.algorithm['hash'].upper())()
        
        signature = private_key.sign(data_to_sign, padding.PKCS1v15(), hash_algo)
        self.signatureValue.text = base64.b64encode(signature).decode('utf-8')

    def digestValueXML(self):
        """Calculate digest of XML document - mirrors PHP digestValueXML()"""
        if '</NominaIndividual>' in self.xml_string:
            SearchNS = 'xmlns="dian:gov:co:facturaelectronica:NominaIndividual"'
            ReplacementNS = 'xmlns="urn:dian:gov:co:facturaelectronica:NominaIndividual"'
            
            CopyOf = etree.tostring(self.domDocument, encoding='unicode')
            modified = CopyOf.replace(SearchNS, ReplacementNS)
            temp_doc = etree.fromstring(modified.encode('utf-8'))
            c14n = etree.tostring(temp_doc, method='c14n').decode('utf-8')
            c14n = c14n.replace(ReplacementNS, SearchNS)
            
            h = hashlib.new(self.algorithm['hash'])
            h.update(c14n.encode('utf-8'))
            self.DigestValueXML = base64.b64encode(h.digest()).decode('utf-8')
            
        elif '</NominaIndividualDeAjuste>' in self.xml_string:
            SearchNS = 'xmlns="dian:gov:co:facturaelectronica:NominaIndividualDeAjuste"'
            ReplacementNS = 'xmlns="urn:dian:gov:co:facturaelectronica:NominaIndividualDeAjuste"'
            
            CopyOf = etree.tostring(self.domDocument, encoding='unicode')
            modified = CopyOf.replace(SearchNS, ReplacementNS)
            temp_doc = etree.fromstring(modified.encode('utf-8'))
            c14n = etree.tostring(temp_doc, method='c14n').decode('utf-8')
            c14n = c14n.replace(ReplacementNS, SearchNS)
            
            h = hashlib.new(self.algorithm['hash'])
            h.update(c14n.encode('utf-8'))
            self.DigestValueXML = base64.b64encode(h.digest()).decode('utf-8')
        else:
            c14n = etree.tostring(self.domDocument, method='c14n')
            h = hashlib.new(self.algorithm['hash'])
            h.update(c14n)
            self.DigestValueXML = base64.b64encode(h.digest()).decode('utf-8')

    def softwareSecurityCode(self):
        """Calculate and set SoftwareSecurityCode - mirrors PHP softwareSecurityCode()"""
        if not self.softwareID or not self.pin:
            return
        
        xml_str = etree.tostring(self.domDocument, encoding='unicode')
        
        # Check for Nomina (ProveedorXML)
        if '/NominaIndividual/ProveedorXML/' in xml_str or '/NominaIndividualDeAjuste/ProveedorXML/' in xml_str:
            numero = self.get_tag('NumeroSecuenciaXML', 0, 'Numero')
            hash_val = hashlib.sha384(f'{self.softwareID}{self.pin}{numero}'.encode('utf-8')).hexdigest()
            self.get_tag('ProveedorXML', 0, 'SoftwareSC', hash_val)
        else:
            doc_id = self.get_query('cbc:ID').text
            hash_val = hashlib.sha384(f'{self.softwareID}{self.pin}{doc_id}'.encode('utf-8')).hexdigest()
            ssc_tag = self.get_tag('SoftwareSecurityCode', 0)
            if ssc_tag is not None:
                ssc_tag.text = hash_val

    def setUUID(self):
        """Set UUID (CUFE or CUDE) - mirrors PHP setUUID()"""
        if self.pin and (not self.technicalKey or self.technicalKey == ''):
            profile_id = self.get_query('cbc:ProfileID', validate=False)
            if profile_id is not None:
                profile_text = profile_id.text if hasattr(profile_id, 'text') else ''
                if 'documento soporte en adquisiciones' in profile_text or 'Nota de ajuste al documento soporte' in profile_text:
                    self.cuds()
                else:
                    self.cude()
        
        if self.technicalKey and self.technicalKey != '':
            self.cufe()

    def cufe(self):
        """Calculate CUFE - mirrors PHP cufe()"""
        val_id = self.get_tag('ID', 0).text
        val_date = self.get_tag('IssueDate', 0).text
        val_time = self.get_tag('IssueTime', 0).text
        val_le_amt = self.get_query(f'cac:{self.groupOfTotals}/cbc:LineExtensionAmount').text
        
        val_tax_01 = self._getTaxAmount('01')
        val_tax_04 = self._getTaxAmount('04')
        val_tax_03 = self._getTaxAmount('03')
        
        val_payable = self.get_query(f'cac:{self.groupOfTotals}/cbc:PayableAmount').text
        val_supp_id = self.get_query('cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID').text
        val_cust_id = self.get_query('cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID').text
        val_prof_exec_id = self.get_tag('ProfileExecutionID', 0).text
        
        raw_str = f'{val_id}{val_date}{val_time}{val_le_amt}01{val_tax_01}04{val_tax_04}03{val_tax_03}{val_payable}{val_supp_id}{val_cust_id}{self.technicalKey}{val_prof_exec_id}'
        
        cufe_hash = hashlib.sha384(raw_str.encode('utf-8')).hexdigest()
        
        self.get_tag('UUID', 0).text = cufe_hash
        
        qr_tag = self.get_tag('QRCode', 0)
        if qr_tag is not None and qr_tag.text:
            qr_tag.text = qr_tag.text.replace('-----CUFECUDE-----', cufe_hash)

    def cude(self):
        """Calculate CUDE - mirrors PHP cude()"""
        val_id = self.get_query('cbc:ID').text
        val_date = self.get_query('cbc:IssueDate').text
        val_time = self.get_tag('IssueTime', 0).text
        val_le_amt = self.get_query(f'cac:{self.groupOfTotals}/cbc:LineExtensionAmount').text
        
        val_tax_01 = self._getTaxAmount('01')
        val_tax_04 = self._getTaxAmount('04')
        val_tax_03 = self._getTaxAmount('03')
        
        val_payable = self.get_query(f'cac:{self.groupOfTotals}/cbc:PayableAmount').text
        val_supp_id = self.get_query('cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID').text
        val_cust_id = self.get_query('cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID').text
        val_prof_exec_id = self.get_tag('ProfileExecutionID', 0).text
        
        raw_str = f'{val_id}{val_date}{val_time}{val_le_amt}01{val_tax_01}04{val_tax_04}03{val_tax_03}{val_payable}{val_supp_id}{val_cust_id}{self.pin}{val_prof_exec_id}'
        
        cude_hash = hashlib.sha384(raw_str.encode('utf-8')).hexdigest()
        
        self.get_tag('UUID', 0).text = cude_hash
        
        qr_tag = self.get_tag('QRCode', 0)
        if qr_tag is not None and qr_tag.text:
            qr_tag.text = qr_tag.text.replace('-----CUFECUDE-----', cude_hash)

    def cuds(self):
        """Calculate CUDS - mirrors PHP cuds()"""
        val_id = self.get_tag('ID', 0).text
        val_date = self.get_tag('IssueDate', 0).text
        val_time = self.get_tag('IssueTime', 0).text
        val_le_amt = self.get_query(f'cac:{self.groupOfTotals}/cbc:LineExtensionAmount').text
        
        val_tax_01 = self._getTaxAmount('01')
        
        val_payable = self.get_query(f'cac:{self.groupOfTotals}/cbc:PayableAmount').text
        val_supp_id = self.get_query('cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID').text
        val_cust_id = self.get_query('cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID').text
        val_prof_exec_id = self.get_tag('ProfileExecutionID', 0).text
        
        raw_str = f'{val_id}{val_date}{val_time}{val_le_amt}01{val_tax_01}{val_payable}{val_supp_id}{val_cust_id}{self.pin}{val_prof_exec_id}'
        
        cuds_hash = hashlib.sha384(raw_str.encode('utf-8')).hexdigest()
        
        self.get_tag('UUID', 0).text = cuds_hash
        
        qr_tag = self.get_tag('QRCode', 0)
        if qr_tag is not None and qr_tag.text:
            qr_tag.text = qr_tag.text.replace('-----CUFECUDE-----', cuds_hash)

    def setCUDEEVENT(self):
        """Set CUDE for events - mirrors PHP setCUDEEVENT()"""
        self.cudeevent()

    def cudeevent(self):
        """Calculate CUDE for events - mirrors PHP cudeevent()"""
        val_id = self.get_tag('ID', 0).text
        val_date = self.get_tag('IssueDate', 0).text
        val_time = self.get_tag('IssueTime', 0).text
        val_sender = self.get_query('cac:SenderParty/cac:PartyTaxScheme/cbc:CompanyID').text
        val_receiver = self.get_query('cac:ReceiverParty/cac:PartyTaxScheme/cbc:CompanyID').text
        val_response_code = self.get_query('cac:DocumentResponse/cac:Response/cbc:ResponseCode').text
        val_doc_ref_id = self.get_query('cac:DocumentResponse/cac:DocumentReference/cbc:ID').text
        val_doc_type_code = self.get_query('cac:DocumentResponse/cac:DocumentReference/cbc:DocumentTypeCode').text
        
        raw_str = f'{val_id}{val_date}{val_time}{val_sender}{val_receiver}{val_response_code}{val_doc_ref_id}{val_doc_type_code}{self.pin}'
        
        cude_hash = hashlib.sha384(raw_str.encode('utf-8')).hexdigest()
        
        self.get_tag('UUID', 0).text = cude_hash
        
        qr_tag = self.get_tag('QRCode', 0)
        if qr_tag is not None and qr_tag.text:
            qr_tag.text = qr_tag.text.replace('-----CUFECUDE-----', cude_hash)

    def setCUNE(self):
        """Set CUNE for Nomina - mirrors PHP setCUNE()"""
        self.cune()

    def cune(self):
        """Calculate CUNE - mirrors PHP cune()"""
        xml_str = etree.tostring(self.domDocument, encoding='unicode')
        
        if '</NominaIndividual>' in xml_str:
            numero = self.get_tag('NumeroSecuenciaXML', 0, 'Numero')
            fecha_gen = self.get_tag('InformacionGeneral', 0, 'FechaGen')
            hora_gen = self.get_tag('InformacionGeneral', 0, 'HoraGen')
            devengados = self.get_tag('DevengadosTotal', 0).text
            deducciones = self.get_tag('DeduccionesTotal', 0).text
            comprobante = self.get_tag('ComprobanteTotal', 0).text
            nit = self.get_tag('ProveedorXML', 0, 'NIT')
            num_doc = self.get_tag('Trabajador', 0, 'NumeroDocumento')
            tipo_xml = self.get_tag('InformacionGeneral', 0, 'TipoXML')
            ambiente = self.get_tag('InformacionGeneral', 0, 'Ambiente')
            
            raw_str = f'{numero}{fecha_gen}{hora_gen}{devengados}{deducciones}{comprobante}{nit}{num_doc}{tipo_xml}{self.pin}{ambiente}'
            cune_hash = hashlib.sha384(raw_str.encode('utf-8')).hexdigest()
            
            self.get_tag('InformacionGeneral', 0, 'CUNE', cune_hash)
            
            qr_tag = self.get_tag('CodigoQR', 0)
            if qr_tag is not None and qr_tag.text:
                qr_tag.text = qr_tag.text.replace('-----CUFECUDE-----', cune_hash)
                
        elif '</Eliminar>' in xml_str:
            numero = self.get_tag('NumeroSecuenciaXML', 0, 'Numero')
            fecha_gen = self.get_tag('InformacionGeneral', 0, 'FechaGen')
            hora_gen = self.get_tag('InformacionGeneral', 0, 'HoraGen')
            nit = self.get_tag('Empleador', 0, 'NIT')
            tipo_xml = self.get_tag('InformacionGeneral', 0, 'TipoXML')
            ambiente = self.get_tag('InformacionGeneral', 0, 'Ambiente')
            
            raw_str = f'{numero}{fecha_gen}{hora_gen}0.000.000.00{nit}0{tipo_xml}{self.pin}{ambiente}'
            cune_hash = hashlib.sha384(raw_str.encode('utf-8')).hexdigest()
            
            self.get_tag('InformacionGeneral', 0, 'CUNE', cune_hash)
            
            qr_tag = self.get_tag('CodigoQR', 0)
            if qr_tag is not None and qr_tag.text:
                qr_tag.text = qr_tag.text.replace('-----CUFECUDE-----', cune_hash)
        else:
            numero = self.get_tag('NumeroSecuenciaXML', 0, 'Numero')
            fecha_gen = self.get_tag('InformacionGeneral', 0, 'FechaGen')
            hora_gen = self.get_tag('InformacionGeneral', 0, 'HoraGen')
            devengados = self.get_tag('DevengadosTotal', 0).text
            deducciones = self.get_tag('DeduccionesTotal', 0).text
            comprobante = self.get_tag('ComprobanteTotal', 0).text
            nit = self.get_tag('Empleador', 0, 'NIT')
            num_doc = self.get_tag('Trabajador', 0, 'NumeroDocumento')
            tipo_xml = self.get_tag('InformacionGeneral', 0, 'TipoXML')
            ambiente = self.get_tag('InformacionGeneral', 0, 'Ambiente')
            
            raw_str = f'{numero}{fecha_gen}{hora_gen}{devengados}{deducciones}{comprobante}{nit}{num_doc}{tipo_xml}{self.pin}{ambiente}'
            cune_hash = hashlib.sha384(raw_str.encode('utf-8')).hexdigest()
            
            self.get_tag('InformacionGeneral', 0, 'CUNE', cune_hash)
            
            qr_tag = self.get_tag('CodigoQR', 0)
            if qr_tag is not None and qr_tag.text:
                qr_tag.text = qr_tag.text.replace('-----CUFECUDE-----', cune_hash)

    def _getTaxAmount(self, tax_code):
        """Get tax amount by code"""
        query = f"cac:TaxTotal[cac:TaxSubtotal/cac:TaxCategory/cac:TaxScheme/cbc:ID='{tax_code}']/cbc:TaxAmount"
        result = self.get_query(query, validate=False)
        if result is not None and hasattr(result, 'text'):
            return result.text
        return '0.00'

    # Public methods for consulting calculated values
    def ConsultarCUFE(self):
        if self.technicalKey:
            return self.get_tag('UUID', 0).text
        return None

    def ConsultarCUDE(self):
        if self.pin:
            return self.get_tag('UUID', 0).text
        return None

    def ConsultarCUNE(self):
        if self.pin:
            return self.get_tag('InformacionGeneral', 0, 'CUNE')
        return None

    def ConsultarQRStr(self):
        return self.get_tag('QRCode', 0).text


    # Aliases for snake_case compatibility
    def set_uuid(self):
        """Alias for setUUID"""
        return self.setUUID()
    
    def set_cune(self):
        """Alias for setCUNE"""
        return self.setCUNE()
    
    def set_cude_event(self):
        """Alias for setCUDEEVENT"""
        return self.setCUDEEVENT()
    
    def software_security_code(self):
        """Alias for softwareSecurityCode"""
        return self.softwareSecurityCode()
    
    @property
    def software_id(self):
        return self.softwareID
    
    @software_id.setter
    def software_id(self, value):
        self.softwareID = value
    
    @property
    def technical_key(self):
        return self.technicalKey
    
    @technical_key.setter
    def technical_key(self, value):
        self.technicalKey = value
    
    @property
    def group_of_totals(self):
        return self.groupOfTotals
    
    @group_of_totals.setter
    def group_of_totals(self, value):
        self.groupOfTotals = value
