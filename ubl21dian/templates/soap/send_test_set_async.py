from ..template import Template

class SendTestSetAsync(Template):
    def __init__(self, path_certificate=None, password=None):
        super().__init__(path_certificate, password)
        self.action_url = 'http://wcf.dian.colombia/IWcfDianCustomerServices/SendTestSetAsync'
        self.required_properties = ['file_name', 'content_file', 'test_set_id']
        self.file_name = None
        self.content_file = None
        self.test_set_id = None
        
    def create_template(self):
        return f"""
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:wcf="http://wcf.dian.colombia">
            <soap:Body>
                <wcf:SendTestSetAsync>
                    <!--Optional:-->
                    <wcf:fileName>{self.file_name}</wcf:fileName>
                    <!--Optional:-->
                    <wcf:contentFile>{self.content_file}</wcf:contentFile>
                    <!--Optional:-->
                    <wcf:testSetId>{self.test_set_id}</wcf:testSetId>
                </wcf:SendTestSetAsync>
            </soap:Body>
        </soap:Envelope>
        """
