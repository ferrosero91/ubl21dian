"""
DIANUtils - Utility class for DIAN signature operations
Ported from PHP DIANTrait
"""
import uuid
import hashlib
from lxml import etree
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding


class DIANUtils:
    """Utility class providing common DIAN signature functionality"""
    
    def __init__(self):
        self.version = '1.0'
        self.encoding = 'UTF-8'
        self.certs = None
        self.path_certificate = None
        self.password = None
        
        # Only initialize if not already set by subclass
        if not hasattr(self, 'ids'):
            self.ids = {}
        if not hasattr(self, 'ns'):
            self.ns = {}
        
        self.dom_document = None
        self.domDocument = None  # PHP compatibility
        self.xml = None
        self.xml_string = None

    def read_certs(self):
        """Read and parse PKCS12 certificate"""
        if not self.path_certificate or not self.password:
            raise Exception(f"{self.__class__.__name__}: requires the certificate path and password.")
        
        try:
            with open(self.path_certificate, 'rb') as f:
                p12_data = f.read()
            
            p12_password = self.password.encode('utf-8') if isinstance(self.password, str) else self.password
            
            private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
                p12_data, 
                p12_password
            )
            
            self.certs = {
                'pkey': private_key,
                'cert': certificate,
                'extracerts': additional_certificates or []
            }
            
        except Exception as e:
            raise Exception(f"{self.__class__.__name__}: Failure signing data: {str(e)}")

    def x509_export(self):
        """Export X509 certificate as base64 string (without headers)"""
        if self.certs and self.certs.get('cert'):
            cert_pem = self.certs['cert'].public_bytes(Encoding.PEM).decode('utf-8')
            clean_cert = cert_pem.replace('-----BEGIN CERTIFICATE-----', '')\
                                 .replace('-----END CERTIFICATE-----', '')\
                                 .replace('\n', '').replace('\r', '')
            return clean_cert
            
        raise Exception(f"{self.__class__.__name__}: Error openssl x509 export.")

    def identifiers_references(self):
        """Generate unique IDs for signature elements - mirrors PHP identifiersReferences()"""
        for key, value in self.ids.items():
            # PHP: mb_strtoupper("{$value}-".sha1(uniqid()))
            unique_id = f"{value}-{hashlib.sha1(uuid.uuid4().bytes).hexdigest()}".upper()
            self.ids[key] = unique_id
            # Set as attribute on self (PHP: $this->$key = ...)
            setattr(self, key, unique_id)

    def get_tag(self, tag_name, item=0, attribute=None, attribute_value=None):
        """Get or set tag element/attribute - mirrors PHP getTag()"""
        doc = self.dom_document if self.dom_document is not None else self.domDocument
        if doc is None:
            return None
            
        elements = self._find_elements_by_tag_name(tag_name, doc)
        
        if not elements or len(elements) <= item:
            if attribute is None:
                raise Exception(f"{self.__class__.__name__}: The tag name {tag_name} does not exist.")
            return None
            
        element = elements[item]
        
        if attribute:
            if attribute_value is not None:
                element.set(attribute, str(attribute_value))
                return None
            else:
                return element.get(attribute)
        else:
            return element

    def _find_elements_by_tag_name(self, tag_name, doc=None):
        """Find elements by tag name (ignoring namespace) - like PHP getElementsByTagName"""
        if doc is None:
            doc = self.dom_document if self.dom_document is not None else self.domDocument
        if doc is None:
            return []
        
        root = doc.getroot() if hasattr(doc, 'getroot') else doc
        
        # XPath to find all elements with matching local name
        results = root.xpath(f".//*[local-name() = '{tag_name}']")
        
        # Also check root itself
        if etree.QName(root).localname == tag_name:
            results.insert(0, root)
           
        return results

    def get_query(self, query, validate=True, item=0):
        """Execute XPath query - mirrors PHP getQuery()"""
        doc = self.dom_document if self.dom_document is not None else self.domDocument
        if doc is None:
            raise Exception("DOM document not initialized")
        
        root = doc.getroot() if hasattr(doc, 'getroot') else doc
        
        # Build namespace map for XPath
        namespaces = {}
        for key, value in self.ns.items():
            ns_key = key.replace('xmlns:', '') if key.startswith('xmlns:') else key
            if ns_key != 'xmlns':
                namespaces[ns_key] = value
        
        try:
            results = root.xpath(query, namespaces=namespaces)
        except etree.XPathEvalError as e:
            raise Exception(f"{self.__class__.__name__}: Invalid query {query}. Error: {e}")

        if validate and not results:
            raise Exception(f"{self.__class__.__name__}: The query {query} does not exist.")
             
        if item is None:
            return results
            
        if results and len(results) > item:
            return results[item]
        elif validate:
            raise Exception(f"{self.__class__.__name__}: The query {query} index {item} does not exist.")
        return None

    def join_array(self, array, format_ns=True, join=' '):
        """Join array as attribute string - mirrors PHP joinArray()"""
        items = []
        for key, value in array.items():
            if format_ns:
                items.append(f'{key}="{value}"')
            else:
                items.append(f'{key}={value}')
        return join.join(items)

    def remove_child(self, tag_name, item=0):
        """Remove child element by tag name - mirrors PHP removeChild()"""
        doc = self.dom_document if self.dom_document is not None else self.domDocument
        if doc is None:
            return
            
        elements = self._find_elements_by_tag_name(tag_name, doc)
        
        if len(elements) > item:
            element = elements[item]
            parent = element.getparent()
            if parent is not None:
                parent.remove(element)
