from hazelcast.serialization.api import Portable, StreamSerializer
from hazelcast.core import HazelcastJsonValue


class Resource(Portable):
    FACTORY_ID = 666  # Random integer
    CLASS_ID = 2

    def __init__(self, code_name=None, scope=None, url_regex=None, method=None):
        self.scope = scope
        self.code_name = code_name
        self.url_regex = url_regex
        self.method = method

    def write_portable(self, writer):
        writer.write_utf("scope", self.scope)
        writer.write_utf("code_name", self.code_name)
        writer.write_utf("url_regex", self.url_regex)
        writer.write_utf("method", self.method)

    def read_portable(self, reader):
        self.scope = reader.read_utf("scope")
        self.code_name = reader.read_utf("code_name")
        self.url_regex = reader.read_utf("url_regex")
        self.method = reader.read_utf("method")

    def get_factory_id(self):
        return self.FACTORY_ID

    def get_class_id(self):
        return self.CLASS_ID

    def __str__(self):
        return "Resource[ code_name:{} url_regex:{} ]".format(self.code_name, self.url_regex)

    def __eq__(self, other):
        return type(self) == type(other) and self.code_name == other.code_name and self.url_regex == other.url_regex


class Permissions:
    def __init__(self, scope, actions):
        '''
        To create a object visualize as {scope:[actions]}
        Example {'role':['create', 'update', 'patch']}
        '''
        self.scope = scope
        self.actions = actions


class PermissionSerializer(StreamSerializer):
    def get_type_id(self):
        return 10

    def destroy(self):
        return super().destroy()

    def write(self, out, obj):
        out.write_utf(obj.scope)
        out.write_utf_array(obj.actions)

    def read(self, inp):
        return Permissions(inp.read_utf(), inp.read_utf_array())


class JsonValue(HazelcastJsonValue):
    pass
