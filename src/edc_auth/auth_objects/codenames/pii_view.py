from .pii import pii_codenames

pii_view_codenames = [codename for codename in pii_codenames if "view_" in codename]
