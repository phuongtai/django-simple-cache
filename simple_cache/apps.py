from django.apps import AppConfig
from common.swagger_schema import EndpointEnumerator
from .portable import Resource
from .utils import HazelcastClient


def sync_endpoint():
    # Connect client Hazelcast and initial a map and a list
    client = HazelcastClient()
    client.portable_factories(Resource.FACTORY_ID, Resource.CLASS_ID, Resource)
    client = client.get_client()

    resource_map = client.get_map('resource_map')
    scope_list = client.get_list('scope_list')

    # Get all endpoints.
    EndpointEnumeratorInstance = EndpointEnumerator()
    apis = EndpointEnumeratorInstance.get_api_endpoints(only_regex=True)
    for api in apis:
        url_regex, method, class_view = api[0], api[1], api[2]
        code_name = ''
        if not class_view.cls.authentication_classes:
            continue
        if hasattr(class_view, 'view_class'):
            view = class_view.view_class
            action = method.lower()
        else:
            view = class_view.cls
            action = class_view.actions[method.lower()]
        view_name = view().get_view_name()
        code_name = '{}.{}'.format(view_name, action)

        # Put them into Hazelcast
        if not scope_list.contains(view_name):
            scope_list.add(view_name)
        resource_map.put(code_name, Resource(action, view_name, url_regex, method))

    client.shutdown()


class HazelcastCacheConfig(AppConfig):
    name = 'common.hazelcast_cache'

    # def ready(self):
    #     sync_endpoint()
