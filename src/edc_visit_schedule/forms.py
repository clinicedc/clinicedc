# from django import forms
# 
# # from .models import MembershipForm
# 
# 
# class EnrollmentForm(forms.ModelForm):
# 
#     class Meta:
#         model = MembershipForm
#         fields = '__all__'
# 
#     def clean(self):
#         cleaned_data = self.cleaned_data
#         try:
#             cleaned_data.get('content_type_map').model_class().prepare_appointments
#         except AttributeError:
#             raise forms.ValidationError(
#                 'Enrollment forms must be a subclass of CreateAppointmentsMixin. See module appointment_helper.')
#         return cleaned_data
