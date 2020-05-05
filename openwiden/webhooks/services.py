import hashlib
import hmac

from openwiden.webhooks import models
from django.db import models as m


class RepositoryWebhook:
    @staticmethod
    def all() -> m.QuerySet:
        return models.RepositoryWebhook.objects.all()

    @staticmethod
    def compare_signatures(webhook: models.RepositoryWebhook, msg, signature: str) -> bool:
        """
        Compares signature for received GitHub webhook.
        """
        generated = hmac.new(webhook.secret.encode("utf-8"), msg, hashlib.sha1)
        return True if hmac.compare_digest(generated.hexdigest(), signature) else False
