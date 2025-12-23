from ..template import Template

class GetStatusZip(Template):
    def __init__(self, path_certificate=None, password=None):
        super().__init__(path_certificate, password)
        self.action_url = 'http://wcf.dian.colombia/IWcfDianCustomerServices/GetStatusZip'
        self.required_properties = ['track_id']
        self.track_id = None
        
    def create_template(self):
        return f"""
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:wcf="http://wcf.dian.colombia">
            <soap:Body>
                <wcf:GetStatusZip>
                    <!--Optional:-->
                    <wcf:trackId>{self.track_id}</wcf:trackId>
                </wcf:GetStatusZip>
            </soap:Body>
        </soap:Envelope>
        """
