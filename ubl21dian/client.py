"""
Client - HTTP Client for DIAN SOAP services
Ported from PHP Client class
"""
import requests
from lxml import etree
import json
import re


class Client:
    """HTTP Client for sending SOAP requests to DIAN"""
    
    def __init__(self, template, guardar_en=None):
        """
        Initialize client with a signed template
        
        Args:
            template: A Template instance with signed XML
            guardar_en: Optional path to save the request XML
        """
        self.template = template
        self.to = template.to if hasattr(template, 'to') else template.To
        self.response = None
        self.guardar_en = guardar_en
        
        headers = {
            'Accept': 'application/xml',
            'Content-type': 'application/soap+xml',
        }
        
        # Clean path and save if requested
        if self.guardar_en:
            clean_path = re.sub(r'[\r\n]+', '', self.guardar_en)
            with open(clean_path, 'w', encoding='utf-8') as f:
                f.write(template.xml)
                 
        self._exec_request(headers)

    def _exec_request(self, headers):
        """Execute HTTP POST request"""
        try:
            resp = requests.post(
                self.to, 
                data=self.template.xml.encode('utf-8'), 
                headers=headers, 
                verify=False,  # PHP: CURLOPT_SSL_VERIFYPEER = false
                timeout=180    # PHP: CURLOPT_TIMEOUT = 180
            )
            self.response = resp.content.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"{self.__class__.__name__}: {str(e)}")

    def get_response(self):
        """Get raw response string"""
        return self.response

    def get_response_to_object(self, guardar_en=None):
        """Parse response XML to object/dict"""
        try:
            if not self.response:
                return None
                
            xml_response = etree.fromstring(self.response.encode('utf-8'))
            
            if guardar_en:
                clean_path = re.sub(r'[\r\n]+', '', guardar_en)
                with open(clean_path, 'w', encoding='utf-8') as f:
                    f.write(self.response)
            
            return self._xml_to_object(xml_response)

        except Exception as e:
            raise Exception(f"{self.__class__.__name__}: {self.to} {self.response} - {str(e)}")

    def _xml_to_object(self, root):
        """Convert XML element to dict/object (mirrors PHP xmlToObject)"""
        data_xml = {}

        # Attributes
        if root.attrib:
            data_xml['_attributes'] = dict(root.attrib)

        # Children
        children = list(root)
        if not children:
            text = root.text
            if text and text.strip():
                data_xml['_value'] = text.strip()
                return data_xml['_value'] if len(data_xml) == 1 else data_xml
            return data_xml if data_xml else None

        groups = {}
        
        for child in children:
            # Get local name without namespace
            tag_name = etree.QName(child).localname
            val = self._xml_to_object(child)
            
            if tag_name not in data_xml:
                data_xml[tag_name] = val
            else:
                if tag_name not in groups:
                    data_xml[tag_name] = [data_xml[tag_name]]
                    groups[tag_name] = 1
                data_xml[tag_name].append(val)
                 
        return data_xml

    def __str__(self):
        """String representation as JSON"""
        return json.dumps(self.get_response_to_object())
