# from datetime import date, timedelta, datetime
# from bhp_registration.models import SubjectIdentifierAuditTrail
# from edc.core.bhp_variables.models import StudySpecific
# from bhp_registration.models import RegisteredSubject #RandomizedSubject
# 
# 
# def AllocateInfantIdentifier(** kwargs):
# 
#     """
#     Allocate infant identifiers for as many live_infants_to_register.
#     Choose an id_suffix based on the value of live_infants. So if 
#     live_infants <> live_infants_to_register, use live_infants to
#     determine the suffix, and live_infants_to_register for the number
#     to register
#     """
# 
#     registration_model = kwargs.get('registration_model')
#     registered_mother = kwargs.get('mother_identifier')
#     live_infants = kwargs.get('live_infants')
#     live_infants_to_register = kwargs.get('live_infants_to_register')
#     user = kwargs.get('user')
# 
#     if live_infants_to_register > live_infants:
#         # Trap this on the form, not here!!
#         raise TypeError("Number of infants to register may not exceed number of live infants.")
# 
#     subject_identifier = {}
# 
#     subject_identifier['mother'] = registered_mother.subject_identifier   
# 
#     # we use the mother's consent as the consent pk to store in 
#     # registered subject for this/these infant(s)
# 
#     first_name = ''
#     initials = ''
#     id_suffix = 0
# 
#     if live_infants == 1:
#         id_suffix = 10
#     elif live_infants == 2:
#         id_suffix = 25
#     elif live_infants == 3:
#         id_suffix = 36
#     elif live_infants == 4:
#         id_suffix = 47
#     else:
#         raise TypeError('Ensure number of infants is greater than 0 and less than or equal to 4. You wrote %s' % (live_infants))
# 
#     for infant_order in range(0, live_infants_to_register):
#         id_suffix += (infant_order) * 10
#         subject_identifier['id'] = "%s-%s" % (subject_identifier['mother'], id_suffix)            
#         RegisterSubject(
#             identifier = subject_identifier['id'], 
#             relative_identifier = registered_mother.subject_identifier,
#             consent_pk = registered_mother.pk,
#             first_name = first_name,
#             initials = initials,
#             subject_type = 'infant',
#             user = user)
# 
#     # update subject_identifier to the audit trail table
#     # audit.subject_identifier = subject_identifier['identifier']
#     # audit.save()
# 
#     return True
