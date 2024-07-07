from django.db import models

import uuid

from accounts.models import User
# Create your models here.

class Organisation(models.Model):
    orgId = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User, related_name='organisations')

    def __str__(self):
        return self.name
