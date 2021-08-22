import uuid as uuid
from django.db import models


class IoTDBRelease(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    release_name = models.CharField(max_length=50, null=True, blank=False, unique=True)
    cluster_version = models.CharField(max_length=50, choices=[
        ("apache/iotdb:0.11.1", "0.11.1"),
        ("apache/iotdb:0.11.2", "0.11.2"),
        ("apache/iotdb:0.11.3", "0.11.3"),
        ("apache/iotdb:0.11.4", "0.11.4"),
        ("apache/iotdb:0.12.0-node", "0.12.0"),
        ("apache/iotdb:0.12.1-node", "0.12.1"),
    ], null=False, blank=False)

    started = models.DateTimeField(auto_now=True)

    statefulset = models.TextField(null=True)
    headless_service = models.TextField(null=True)
    service = models.TextField(null=True)
    init_job = models.TextField(null=True)

    admin_password = models.CharField(max_length=20, null=True)

    initialized = models.BooleanField(default=False, null=False)

    class Meta:
        ordering = ("-started",)
