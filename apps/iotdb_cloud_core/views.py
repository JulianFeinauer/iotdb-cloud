import json
import uuid

import yaml
from django.conf import settings
from django.template.loader import render_to_string
from django.views.generic import TemplateView, RedirectView
from kubernetes import config, client
from kubernetes.client import V1DeploymentList, V1JobStatus, V1JobCondition, V1Job

from apps.iotdb_cloud_core import kubernetes_utils
from apps.iotdb_cloud_core.models import IoTDBRelease

namespace = settings.NAMESPACE


class HomeView(TemplateView):
    template_name = "iotdb_cloud_core/home.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        config.load_incluster_config()
        k8s_apps_v1 = client.AppsV1Api()
        core_api_v1 = client.CoreV1Api()
        batch_v1 = client.BatchV1Api()

        # deployments: V1DeploymentList = k8s_apps_v1.list_namespaced_deployment(namespace=namespace,
        #                                                                        label_selector="app=auto-deployment")
        #
        # context_data["deployments"] = deployments.items

        releases = []

        for release in IoTDBRelease.objects.all():
            print(f"Service: {release.service}")
            # name = json.loads(release.service.replace("'", '"'))["metadata"]["name"]
            # print(f"Name: {name}")
            try:
                service = core_api_v1.read_namespaced_service(namespace=namespace, name=release.service)

                # Get Readiness of statefulset
                status = k8s_apps_v1.read_namespaced_stateful_set_status(namespace=namespace, name=release.statefulset)

                if status.status.ready_replicas == status.status.replicas:
                    ready = True
                else:
                    ready = False

                try:
                    external_ip = service.status.load_balancer.ingress[0].ip
                except:
                    external_ip = "unknown"

                initialized = False
                try:
                    if release.initialized:
                        initialized = True
                    else:
                        job: V1Job = batch_v1.read_namespaced_job_status(namespace=namespace, name=release.init_job)

                        condition: V1JobCondition = job.status.conditions[0]

                        if condition.type == "Complete":
                            initialized = True

                            release.initialized = True
                            release.save()
                except Exception as e:
                    print(f"Exception: {e}")

                releases.append({"name": release.service, "ip": external_ip, "status": status.status, "ready": ready,
                                 "initialized": initialized, "password": release.admin_password})
            except Exception as e:
                print(e)

        context_data["releases"] = releases

        return context_data


class ExecuteView(RedirectView):
    pattern_name = "home"

    def get(self, request, *args, **kwargs):
        # Execute the Sheduled task
        # execute.delay()

        config.load_incluster_config()

        uuid_ = uuid.uuid4()

        admin_password = uuid.uuid4().__str__().replace("_", "")

        statefulset, headless_service, service, job = kubernetes_utils.create_charts(uuid_, admin_password)

        # dep = render_to_string('iotdb_cloud_core/deployment.yaml', {"deployment": uuid_})

        # print(f"Deployment:\n----\n{dep}\n----\n")

        k8s_apps_v1 = client.AppsV1Api()
        core_api = client.CoreV1Api()
        batch_v1 = client.BatchV1Api()

        resp = k8s_apps_v1.create_namespaced_stateful_set(
            body=statefulset, namespace=namespace)

        print("Staefulset created. status='%s'" % resp.metadata.name)

        resp = core_api.create_namespaced_service(
            body=headless_service, namespace=namespace)

        print("Service created. status='%s'" % resp.metadata.name)

        resp = core_api.create_namespaced_service(
            body=service, namespace=namespace)

        print("Service created. status='%s'" % resp.metadata.name)

        # Create Init Job
        resp = batch_v1.create_namespaced_job(namespace=namespace, body=job)

        print("Job created. status='%s'" % resp.metadata.name)

        # Create and store it in a model
        IoTDBRelease.objects.create(uuid=uuid_, statefulset=statefulset["metadata"]["name"],
                                    headless_service=headless_service["metadata"]["name"],
                                    service=service["metadata"]["name"], init_job=job["metadata"]["name"],
                                    admin_password=admin_password)

        return super().get(request, *args, **kwargs)
