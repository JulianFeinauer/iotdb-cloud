import uuid as uuid
from django.db import models


class IoTDBRelease(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    started = models.DateTimeField(auto_now=True)

    statefulset = models.TextField(null=False)
    headless_service = models.TextField(null=False)
    service = models.TextField(null=False)
    init_job = models.TextField(null=False)

    admin_password = models.TextField(null=False)

    initialized = models.BooleanField(default=False, null=False)

    class Meta:
        ordering = ("-started",)
