import logging

from celery import shared_task
from django.conf import settings
from kubernetes import client

from apps.iotdb_cloud_core import kubernetes_utils
from apps.iotdb_cloud_core.models import IoTDBRelease

namespace = settings.NAMESPACE


@shared_task
def create_release(uuid):
    kubernetes_utils.load_config()

    release = IoTDBRelease.objects.get(pk=uuid)

    statefulset, headless_service, service, job = kubernetes_utils.create_charts(uuid, release.admin_password)

    k8s_apps_v1 = client.AppsV1Api()
    core_api = client.CoreV1Api()
    batch_v1 = client.BatchV1Api()

    resp = k8s_apps_v1.create_namespaced_stateful_set(
        body=statefulset, namespace=namespace)

    logging.info("Staefulset created. status='%s'" % resp.metadata.name)

    resp = core_api.create_namespaced_service(
        body=headless_service, namespace=namespace)

    logging.info("Service created. status='%s'" % resp.metadata.name)

    resp = core_api.create_namespaced_service(
        body=service, namespace=namespace)

    logging.info("Service created. status='%s'" % resp.metadata.name)

    # Create Init Job
    resp = batch_v1.create_namespaced_job(namespace=namespace, body=job)

    logging.info("Job created. status='%s'" % resp.metadata.name)

    # Create and store it in a model
    IoTDBRelease.objects.update(statefulset=statefulset["metadata"]["name"],
                                headless_service=headless_service["metadata"]["name"],
                                service=service["metadata"]["name"], init_job=job["metadata"]["name"])
