import os

from celery import Celery, shared_task

# set the default Django settings module for the 'celery' program.
from kubernetes import config, client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iotdb_cloud.settings")

app = Celery("iotdb_cloud")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@shared_task
def ping():
    return "pong"


@shared_task
def list_ressources():
    config.load_incluster_config()

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" %
              (i.status.pod_ip, i.metadata.namespace, i.metadata.name))


app.conf.beat_schedule = {
    "ping": {
        "task": "iotdb_cloud.celery.ping",
        "schedule": 5.0,
    },
    "list_ressources": {
        "task": "iotdb_cloud.celery.list_ressources",
        "schedule": 10.0,
    },
}
