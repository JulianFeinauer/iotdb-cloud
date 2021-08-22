from django.urls import path

from apps.iotdb_cloud_core.views import HomeView, ExecuteView, CreateIoTDBReleaseView

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('create', CreateIoTDBReleaseView.as_view(), name="release/create"),
    path('execute', ExecuteView.as_view(), name="execute"),
]
