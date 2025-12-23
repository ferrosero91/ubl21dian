"""
GetStatus - SOAP template for GetStatus operation
"""
from ..template import Template


class GetStatus(Template):
    """GetStatus SOAP template for DIAN"""
    
    def __init__(self, path_certificate=None, password=None, ambiente=None):
        super().__init__(path_certificate, password)
        self.Action = 'http://wcf.dian.colombia/IWcfDianCustomerServices/GetStatus'
        self.action_url = self.Action
        self.required_properties = ['track_id']
        self.track_id = None
        self.trackId = None  # PHP compatibility
        
        if ambiente:
            self.To = ambiente
            self.to = ambiente
        
    def create_template(self):
        """Create SOAP envelope for GetStatus"""
        track_id = self.track_id or self.trackId
        return f'''<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:wcf="http://wcf.dian.colombia">
    <soap:Body>
        <wcf:GetStatus>
            <!--Optional:-->
            <wcf:trackId>{track_id}</wcf:trackId>
        </wcf:GetStatus>
    </soap:Body>
</soap:Envelope>'''
