from ..template import Template

class GetReferenceNotes(Template):
    def __init__(self, path_certificate=None, password=None):
        super().__init__(path_certificate, password)
        self.action_url = 'http://wcf.dian.colombia/IWcfDianCustomerServices/GetReferenceNotes'
        self.required_properties = ['cufe']
        self.cufe = None
        
    def create_template(self):
        return f"""
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:wcf="http://wcf.dian.colombia">
            <soap:Body>
                <wcf:GetReferenceNotes>
                    <!--Optional:-->
                    <wcf:cufe>{self.cufe}</wcf:cufe>
                </wcf:GetReferenceNotes>
            </soap:Body>
        </soap:Envelope>
        """
