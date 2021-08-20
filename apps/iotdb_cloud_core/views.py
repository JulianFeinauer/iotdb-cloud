import uuid

import yaml
from django.template.loader import render_to_string
from django.views.generic import TemplateView, RedirectView
from kubernetes import config, client
from kubernetes.client import V1DeploymentList


class HomeView(TemplateView):
    template_name = "iotdb_cloud_core/home.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        config.load_incluster_config()
        k8s_apps_v1 = client.AppsV1Api()

        deployments: V1DeploymentList = k8s_apps_v1.list_namespaced_deployment(namespace="default", label_selector="app=auto-deployment")

        context_data["deployments"] = deployments.items

        return context_data


class ExecuteView(RedirectView):
    pattern_name = "home"

    def get(self, request, *args, **kwargs):
        # Execute the Sheduled task
        # execute.delay()

        config.load_incluster_config()

        uuid_ = uuid.uuid4()
        dep = render_to_string('iotdb_cloud_core/deployment.yaml', {"deployment": uuid_})

        print(f"Deployment:\n----\n{dep}\n----\n")

        k8s_apps_v1 = client.AppsV1Api()
        resp = k8s_apps_v1.create_namespaced_deployment(
            body=yaml.safe_load(dep), namespace="default")
        print("Deployment created. status='%s'" % resp.metadata.name)

        return super().get(request, *args, **kwargs)


