from django.conf import settings
from django.contrib.auth import views
from django.urls.conf import path

from .views import LoginView, LogoutView

allow_password_reset = getattr(settings, "ALLOW_PASSWORD_RESET", None)

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path(
        "logout/",
        LogoutView.as_view(template_name="edc_dashboard/login.html"),
        name="logout",
    ),
]

if allow_password_reset:
    urlpatterns += [
        path(
            "password_change/",
            views.PasswordChangeView.as_view(),
            name="password_change",
        ),
        path(
            "password_change/done/",
            views.PasswordChangeDoneView.as_view(),
            name="password_change_done",
        ),
        path("password_reset/", views.PasswordResetView.as_view(), name="password_reset"),
        path(
            "password_reset/done/",
            views.PasswordResetDoneView.as_view(),
            name="password_reset_done",
        ),
        path(
            "reset/<uidb64>/<token>/",
            views.PasswordResetConfirmView.as_view(),
            name="password_reset_confirm",
        ),
        path(
            "reset/done/",
            views.PasswordResetCompleteView.as_view(),
            name="password_reset_complete",
        ),
    ]
else:
    urlpatterns += [
        path(
            "password_reset/",
            LogoutView.as_view(template_name="edc_dashboard/login.html"),
            name="password_reset",
        ),
        path(
            "password_reset/done/",
            LogoutView.as_view(template_name="edc_dashboard/login.html"),
            name="password_reset_done",
        ),
        path(
            "reset/<uidb64>/<token>/",
            LogoutView.as_view(template_name="edc_dashboard/login.html"),
            name="password_reset_confirm",
        ),
        path(
            "reset/done/",
            LogoutView.as_view(template_name="edc_dashboard/login.html"),
            name="password_reset_complete",
        ),
    ]
