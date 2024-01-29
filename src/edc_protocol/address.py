from dataclasses import dataclass, field


@dataclass
class Address:
    contact_name: str = field(default="CONTACT NAME")
    company_name: str = field(default="COMPANY NAME")
    address: str = field(default="ADDRESS")
    city: str = field(default="CITY")
    state: str = field(default="")
    postal_code: str = field(default="0000")
    country: str = field(default="COUNTRY")
    tel: str = field(default="TELEPHONE")
    mobile: str = field(default="MOBILE")
    fax: str = field(default="FAX")
