import os
import shlex
import subprocess
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from django_q.cluster import Stat
from django.core.management import autoreload


class Command(BaseCommand):
    help = _("Starts a Django Q Cluster for local development.")

    @classmethod
    def reload(cls):
        for stat in Stat.get_all():
            try:
                os.kill(stat.pid, 9)
            except ProcessLookupError:
                pass

        start_cmd = 'python -c "import django; django.setup(); from django_q.cluster import Cluster; Cluster().start()"'
        subprocess.call(shlex.split(start_cmd))

    def handle(self, *args, **options):
        autoreload.run_with_reloader(self.reload)
