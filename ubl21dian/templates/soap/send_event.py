from ..template import Template

class SendEvent(Template):
    def __init__(self, path_certificate=None, password=None):
        super().__init__(path_certificate, password)
        self.action_url = 'http://wcf.dian.colombia/IWcfDianCustomerServices/SendEventUpdateStatus'
        self.to_url = 'https://vpfe.dian.gov.co/WcfDianCustomerServices.svc?wsdl'
        self.required_properties = ['content_file']
        self.content_file = None
        
    def create_template(self):
        return f"""
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:wcf="http://wcf.dian.colombia">
           <soap:Header/>
            <soap:Body>
                <wcf:SendEventUpdateStatus>
                    <!--Optional:-->
                    <wcf:contentFile>{self.content_file}</wcf:contentFile>
                </wcf:SendEventUpdateStatus>
            </soap:Body>
        </soap:Envelope>
        """
