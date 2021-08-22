import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, RedirectView, CreateView
from kubernetes import client
from kubernetes.client import V1JobCondition, V1Job

from apps.iotdb_cloud_core import kubernetes_utils
from apps.iotdb_cloud_core.forms import IoTDBReleaseCreateForm
from apps.iotdb_cloud_core.models import IoTDBRelease
from apps.iotdb_cloud_core.tasks import create_release

namespace = settings.NAMESPACE
kubernetes_config = settings.KUBERNETES_CONFIG


@method_decorator(login_required, name="dispatch")
class HomeView(TemplateView):
    template_name = "iotdb_cloud_core/home.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        kubernetes_utils.load_config()

        k8s_apps_v1 = client.AppsV1Api()
        core_api_v1 = client.CoreV1Api()
        batch_v1 = client.BatchV1Api()

        # deployments: V1DeploymentList = k8s_apps_v1.list_namespaced_deployment(namespace=namespace,
        #                                                                        label_selector="app=auto-deployment")
        #
        # context_data["deployments"] = deployments.items

        releases = []

        for release in self.get_queryset():
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

                releases.append({"model": release, "ip": external_ip, "status": status.status, "ready": ready})
            except Exception as e:
                print(e)

        context_data["releases"] = releases

        return context_data

    def get_queryset(self):
        if self.request.user.is_superuser:
            return IoTDBRelease.objects.all()
        else:
            return IoTDBRelease.objects.filter(owner=self.request.user)


@method_decorator(login_required, name="dispatch")
class ExecuteView(RedirectView):
    pattern_name = "home"

    def get(self, request, *args, **kwargs):
        # Execute the Sheduled task
        # execute.delay()

        kubernetes_utils.load_config()

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


@method_decorator(login_required, name="dispatch")
class CreateIoTDBReleaseView(CreateView):
    model = IoTDBRelease
    form_class = IoTDBReleaseCreateForm
    success_url = reverse_lazy("home")

    def get_initial(self):
        initial = super().get_initial()
        initial["owner"] = self.request.user
        return initial

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if not int(form.data["owner"]) == self.request.user.id:
            form.add_error(None, "There was an error processing your request!")
            self.object = None
            return self.form_invalid(form)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form_valid = super().form_valid(form)

        # Start Background Task
        create_release.delay(self.object.pk)

        return form_valid



