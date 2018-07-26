from django.urls.conf import path

from .views import LoginView, LogoutView


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(
        template_name='edc_base/login.html'), name='logout'),
    path('password_reset/', LogoutView.as_view(
        template_name='edc_base/login.html'), name='password_reset'),
    path('password_reset/done/', LogoutView.as_view(
        template_name='edc_base/login.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', LogoutView.as_view(
        template_name='edc_base/login.html'), name='password_reset_confirm'),
    path('reset/done/', LogoutView.as_view(
        template_name='edc_base/login.html'), name='password_reset_complete'),
]
