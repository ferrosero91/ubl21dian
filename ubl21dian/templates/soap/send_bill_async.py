"""
SendBillAsync - SOAP template for SendBillAsync operation
"""
from ..template import Template


class SendBillAsync(Template):
    """SendBillAsync SOAP template for DIAN"""
    
    def __init__(self, path_certificate=None, password=None):
        super().__init__(path_certificate, password)
        self.Action = 'http://wcf.dian.colombia/IWcfDianCustomerServices/SendBillAsync'
        self.action_url = self.Action
        self.required_properties = ['file_name', 'content_file']
        self.file_name = None
        self.content_file = None
        self.fileName = None  # PHP compatibility
        self.contentFile = None  # PHP compatibility
        
    def create_template(self):
        """Create SOAP envelope for SendBillAsync"""
        file_name = self.file_name or self.fileName
        content_file = self.content_file or self.contentFile
        return f'''<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:wcf="http://wcf.dian.colombia">
    <soap:Body>
        <wcf:SendBillAsync>
            <!--Optional:-->
            <wcf:fileName>{file_name}</wcf:fileName>
            <!--Optional:-->
            <wcf:contentFile>{content_file}</wcf:contentFile>
        </wcf:SendBillAsync>
    </soap:Body>
</soap:Envelope>'''
