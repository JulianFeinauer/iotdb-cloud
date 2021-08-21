from django.test import TestCase

from apps.iotdb_cloud_core import kubernetes_utils


class Tests(TestCase):

    def test_kubernetes_utils(self):
        kubernetes_utils.create_charts()
