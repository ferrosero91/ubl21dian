"""
Template - Base class for SOAP templates
Ported from PHP Template class
"""
from ..binary_security_token.soap import SOAP
from ..client import Client


class Template(SOAP):
    """Base template class for DIAN SOAP operations"""
    
    def __init__(self, path_certificate=None, password=None):
        super().__init__(path_certificate, password)
        self.To = 'https://vpfe-hab.dian.gov.co/WcfDianCustomerServices.svc?wsdl'
        self.to = self.To  # Alias for compatibility
        self.template = None
        self.required_properties = []
        self.Action = None  # To be set by subclasses
        self.action_url = None  # Alias

    def sign(self, string=None):
        """Sign the template"""
        self._required_properties_check()
        
        # Set Action from action_url if defined
        if self.action_url:
            self.Action = self.action_url
        
        template_xml = string if string else self.create_template()
        return super().sign(template_xml)

    def sign_to_send(self, guardar_en=None):
        """Sign and send the template"""
        self._required_properties_check()
        
        # Set Action from action_url if defined
        if self.action_url:
            self.Action = self.action_url
            
        self.sign(self.create_template())
        return Client(self, guardar_en)

    def _required_properties_check(self):
        """Validate required properties are set"""
        for prop in self.required_properties:
            # Convert snake_case to check both formats
            snake_prop = prop
            camel_prop = ''.join(word.capitalize() if i > 0 else word 
                                for i, word in enumerate(prop.split('_')))
            
            val = getattr(self, snake_prop, None) or getattr(self, camel_prop, None)
            if val is None:
                raise Exception(f"The {prop} property has to be defined")
    
    def create_template(self):
        """Create template XML - override in subclasses"""
        raise NotImplementedError("Subclasses must implement create_template()")
