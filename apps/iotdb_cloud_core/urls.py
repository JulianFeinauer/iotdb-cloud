from django.urls import path

from apps.iotdb_cloud_core.views import HomeView, ExecuteView

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('execute', ExecuteView.as_view(), name="execute"),
]
