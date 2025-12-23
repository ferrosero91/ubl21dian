from ..template import Template

class GetNumberingRange(Template):
    def __init__(self, path_certificate=None, password=None):
        super().__init__(path_certificate, password)
        self.action_url = 'http://wcf.dian.colombia/IWcfDianCustomerServices/GetNumberingRange'
        # Note: PHP sets self.To = 'https://vpfe.dian.gov.co/WcfDianCustomerServices.svc?wsdl'
        # We might want to allow configuring this in the base Template class or here
        self.to_url = 'https://vpfe.dian.gov.co/WcfDianCustomerServices.svc?wsdl' 
        
        self.required_properties = ['nit', 'id_software']
        self.nit = None
        self.id_software = None
        
    def create_template(self):
        return f"""
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:wcf="http://wcf.dian.colombia">
           <soap:Header/>
           <soap:Body>
              <wcf:GetNumberingRange>
                 <!--Optional:-->
                 <wcf:accountCode>{self.nit}</wcf:accountCode>
                 <!--Optional:-->
                 <wcf:accountCodeT>{self.nit}</wcf:accountCodeT>
                 <!--Optional:-->
                 <wcf:softwareCode>{self.id_software}</wcf:softwareCode>
              </wcf:GetNumberingRange>
           </soap:Body>
        </soap:Envelope>
        """
