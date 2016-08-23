from collections import namedtuple

AliquotTypeTuple = namedtuple('AliquotTypeTuple', 'name alpha_code numeric_code')
ProfileTuple = namedtuple('ProfileItemTuple', 'profile_name alpha_code')
ProfileItemTuple = namedtuple('ProfileItemTuple', 'profile_name alpha_code volume count')
