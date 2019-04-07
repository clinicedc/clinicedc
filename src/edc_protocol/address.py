class Address:
    def __init__(
        self,
        contact_name=None,
        company_name=None,
        address=None,
        city=None,
        state=None,
        postal_code=None,
        country=None,
        tel=None,
        mobile=None,
        fax=None,
    ):
        self.contact_name = contact_name or "CONTACT NAME"
        self.company_name = company_name or "COMPANY NAME"
        self.address = address or "ADDRESS"
        self.city = city or "CITY"
        self.state = state or ""
        self.postal_code = postal_code or ""
        self.country = country or "COUNTRY"
        self.tel = tel or "TELEPHONE"
        self.mobile = mobile or "MOBILE"
        self.fax = fax or "FAX"
