from django import forms
from django.core.exceptions import ValidationError

from apps.iotdb_cloud_core.models import IoTDBRelease


class IoTDBReleaseCreateForm(forms.ModelForm):

    def clean_admin_password(self):
        password = self.cleaned_data.get('admin_password')
        if len(password) < 4:
            raise ValidationError('Password too short')
        return password

    class Meta:
        model = IoTDBRelease
        fields = ["release_name", "cluster_version", "admin_password"]
        widgets = {
            "uuid": forms.HiddenInput(),
            "admin_password": forms.PasswordInput()
        }
