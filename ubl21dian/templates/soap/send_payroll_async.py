from ..template import Template

class SendPayrollASync(Template):
    def __init__(self, path_certificate=None, password=None):
        super().__init__(path_certificate, password)
        self.action_url = 'http://wcf.dian.colombia/IWcfDianCustomerServices/SendPayrollASync'
        self.to_url = 'https://vpfe.dian.gov.co/WcfDianCustomerServices.svc?wsdl'
        self.required_properties = ['file_name', 'content_file']
        self.file_name = None
        self.content_file = None
        
    def create_template(self):
        return f"""
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:wcf="http://wcf.dian.colombia">
           <soap:Header/>
            <soap:Body>
                <wcf:SendPayrollASync>
                    <!--Optional:-->
                    <wcf:fileName>{self.file_name}</wcf:fileName>
                    <!--Optional:-->
                    <wcf:contentFile>{self.content_file}</wcf:contentFile>
                </wcf:SendPayrollASync>
            </soap:Body>
        </soap:Envelope>
        """
