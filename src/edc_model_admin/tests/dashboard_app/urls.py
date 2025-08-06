from .views import DashboardView

app_name = "dashboard_app"

urlpatterns = DashboardView.urls(namespace=app_name, label="dashboard")
