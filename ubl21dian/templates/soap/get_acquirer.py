from ..template import Template

class GetAcquirer(Template):
    def __init__(self, path_certificate=None, password=None, environment=None):
        super().__init__(path_certificate, password)
        self.action_url = 'http://wcf.dian.colombia/IWcfDianCustomerServices/GetAcquirer'
        if environment:
            self.to_url = environment
        else:
            self.to_url = 'https://vpfe.dian.gov.co/WcfDianCustomerServices.svc?wsdl'
        
        self.required_properties = ['identification_type', 'identification_number']
        self.identification_type = None
        self.identification_number = None
        
    def create_template(self):
        return f"""
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:wcf="http://wcf.dian.colombia">
            <soap:Body>
                <wcf:GetAcquirer>
                    <wcf:identificationType>{self.identification_type}</wcf:identificationType>
                    <wcf:identificationNumber>{self.identification_number}</wcf:identificationNumber>
                </wcf:GetAcquirer>
            </soap:Body>
        </soap:Envelope>
        """
