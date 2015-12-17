import re

regex_patterns = {
    'word': re.compile('^[a-z_]*=[A-Za-z]*$'),
    'number': re.compile('^[a-z_]*=[0-9]*$'),
    'gender': re.compile('^[MF]{1}$'),
    'date': re.compile('^[0-9]{4}\-[01]{1}[0-9]{1}\-[0-3]{1}[0-9]{1}$'),
    'yyyy_mm': re.compile('^[0-9]{4}\-[01]{1}[0-9]{1}$'),
    'yyyy': re.compile('^[0-9]{4}$'),
    'uuid': re.compile('[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}'),
    }
