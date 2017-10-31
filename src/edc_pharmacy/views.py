# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator, EmptyPage
# from django.urls.base import reverse
# from django.utils.decorators import method_decorator
# from django.views.generic import FormView, TemplateView
# from edc_base.model_mixins.constants import DEFAULT_BASE_FIELDS
# from edc_base.view_mixins import EdcBaseViewMixin
# from edc_label.view_mixins import EdcLabelViewMixin
# from urllib.parse import urlencode
#
# from .constants import TABLET, SYRUP, IV, IM, SUPPOSITORY, SOLUTION, CAPSULE
# from .forms import PatientSearchForm
# from .models import Patient, Dispense
#
#
# class HomeView(EdcBaseViewMixin, EdcLabelViewMixin, FormView):
#     template_name = 'edc_pharma/home.html'
# #     form_class = PatientSearchForm
#     paginate_by = 4
#
#     def __init__(self, **kwargs):
#         self.patient = Patient.objects.all().order_by('-consent_datetime')
#         super(HomeView, self).__init__(**kwargs)
#
#     def get_success_url(self):
#         return reverse('home_url')
#
#     def form_valid(self, form):
#         if form.is_valid():
#             subject_identifier = form.cleaned_data['subject_identifier']
#             try:
#                 self.patient = Patient.objects.filter(
#                     subject_identifier__contains=subject_identifier)
#             except Patient.DoesNotExist:
#                 form.add_error(
#                     'subject_identifier', 'Patient not found. Please search again or add a new patient.')
#             context = self.get_context_data(form=form)
#         return self.render_to_response(context)
#
#     def get_context_data(self, **kwargs):
#         context = super(HomeView, self).get_context_data(**kwargs)
#         context.update({
#             'patients': self.patients()})
#         return context
#
#     def patients(self):
#         """Returns a patients queryset after pagination."""
#         patients = self.patient
#         paginator = Paginator(patients, self.paginate_by)
#         try:
#             patients = paginator.page(self.kwargs.get('page', 1))
#         except EmptyPage:
#             patients = paginator.page(paginator.num_pages)
#         return patients
#
#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super(HomeView, self).dispatch(*args, **kwargs)
#
#
# class PatientRecordView(EdcBaseViewMixin, EdcLabelViewMixin, TemplateView):
#     template_name = 'edc_pharma/subject_record.html'
#     paginate_by = 5
#     number_of_copies = 1
#
#     def __init__(self, **kwargs):
#         self.patient = None
#         super(PatientRecordView, self).__init__(**kwargs)
#
#     def get_context_data(self, **kwargs):
#         context = super(PatientRecordView, self).get_context_data(**kwargs)
#         if kwargs.get('dispense_pk'):
#             self.print_label(kwargs['dispense_pk'])
#         try:
#             self.patient = Patient.objects.get(
#                 subject_identifier=kwargs['subject_identifier'])
#         except Patient.DoesNotExist:
#             pass
#         dispenses = Dispense.objects.filter(
#             patient=self.patient).order_by('-prepared_datetime')
#         if dispenses:
#             context.update({'dispenses': self.dispenses})
#         context.update({
#             'recent_dispense_querystring': self.refill_query_string,
#             'patient': self.patient})
#         return context
#
#     def print_label(self, dispense_pk):
#         dispense = Dispense.objects.get(pk=dispense_pk)
#         label_name = self.label_name(dispense.dispense_type)
#         super(PatientRecordView, self).print_label(
#             label_name, copies=self.number_of_copies, context=dispense.label_context)
#
#     def label_name(self, name):
#         if name == TABLET:
#             return 'dispense_label_tablet'
#         elif name == SYRUP:
#             return 'dispense_label_syrup'
#         elif name == IV:
#             return 'dispense_label_iv'
#         elif name == IM:
#             return 'dispense_label_iv'
#         elif name == SUPPOSITORY:
#             return 'dispense_label_suppository'
#         elif name == SOLUTION:
#             return 'dispense_label_syrup'
#         elif name == CAPSULE:
#             return 'dispense_label_capsule'
#
#     @property
#     def dispenses(self):
#         """Returns a dispense queryset after pagination."""
#         dispenses = Dispense.objects.filter(
#             patient=self.patient).order_by('-prepared_datetime')
#         paginator = Paginator(dispenses, self.paginate_by)
#         try:
#             dispenses = paginator.page(self.kwargs.get('page', 1))
#         except EmptyPage:
#             dispenses = paginator.page(paginator.num_pages)
#         return dispenses
#
#     @property
#     def refill_query_string(self):
#         try:
#             last = {}
#             dispense = Dispense.objects.filter(patient=self.patient).last()
#             for field in Dispense._meta.fields:
#                 if field.name not in DEFAULT_BASE_FIELDS + ['prepared_datetime', 'medication_id', 'patient_id']:
#                     value = getattr(dispense, field.name)
#                     if value:
#                         last.update({field.name: value})
#             last['medication'] = last['medication'].id
#             last['patient'] = last['patient'].id
#             query_string = urlencode(last)
#         except AttributeError:
#             query_string = ''
#         return query_string
#
#     @method_decorator(login_required)
#     def dispatch(self, *args, **kwargs):
#         return super(PatientRecordView, self).dispatch(*args, **kwargs)
