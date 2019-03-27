from .views import DashboardView

app_name = "dashboard2_app"

urlpatterns = DashboardView.urls(app_name, label="dashboard2")
