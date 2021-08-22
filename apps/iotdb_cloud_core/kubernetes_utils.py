import yaml
from django.conf import settings
from django.template.loader import render_to_string
from kubernetes import config


def load_config():
    if settings.KUBERNETES_CONFIG == "INTERNAL":
        config.load_incluster_config()
    else:
        config.load_kube_config()

def create_charts(identifier, admin_password):
    context = {
        "statefulset": {
            "name": f"iotdb-{identifier}"
        },
        "service": {
            "name": f"iotdb-{identifier}"
        },
        "labels": {
            "app": "apache-iotdb",
            "release": f"{identifier}"
        },
        "selector_labels": {
            "app": "apache-iotdb",
            "release": f"{identifier}"
        },
        "job": {
            "name": f"init-{identifier}",
            "password": f"{admin_password}"
        }
    }
    statefulset = render_to_string('iotdb_cloud_core/stateful.yaml', context)
    headless_service = render_to_string('iotdb_cloud_core/headless-service.yaml', context)
    service = render_to_string('iotdb_cloud_core/service.yaml', context)
    job = render_to_string('iotdb_cloud_core/job.yaml', context)

    return yaml.safe_load(statefulset), yaml.safe_load(headless_service), yaml.safe_load(service), yaml.safe_load(job)