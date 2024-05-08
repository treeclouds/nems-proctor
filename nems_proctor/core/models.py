from django.db import models


class BaseModel(models.Model):
    company_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        abstract = True
