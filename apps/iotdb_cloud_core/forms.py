from django import forms

from apps.iotdb_cloud_core.models import IoTDBRelease


class IoTDBReleaseCreateForm(forms.ModelForm):


    class Meta:
        model = IoTDBRelease
        fields = ["release_name", "cluster_version", "admin_password"]
        widgets = {
            "uuid": forms.HiddenInput(),
            "admin_password": forms.PasswordInput()
        }
