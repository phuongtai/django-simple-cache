import hazelcast
from django.conf import settings
from django.core.management.base import BaseCommand
from common.hazelcast_cache.backends.base import parse_url


class Command(BaseCommand):
    help = "Test connect hazelcast"
    # def add_arguments(self, parser):
    #     # Positional arguments
    #     parser.add_argument('url_host', nargs='+', type=str)

    def handle(self, *args, **options):
        # url_host = 'admin:admin@localhost:5071'
        config = hazelcast.ClientConfig()
        username, password, host = parse_url(settings.HAZELCAST_HOST)
        config.group_config.name = username
        config.group_config.password = password
        config.network_config.connection_attempt_limit = 1
        config.network_config.addresses.append(host)

        client = hazelcast.HazelcastClient(config)
        self.stdout.write(self.style.SUCCESS("SUCCESS"))