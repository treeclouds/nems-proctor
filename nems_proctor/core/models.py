from django.db import models

from nems_proctor.utils.middlewares.tenant import CompanyFilterModel
from nems_proctor.utils.middlewares.tenant import CompanyFilterQuerySet


class BaseModel(CompanyFilterModel):
    company_id = models.PositiveIntegerField(null=True, blank=True)

    objects = CompanyFilterQuerySet.as_manager()

    class Meta:
        abstract = True
