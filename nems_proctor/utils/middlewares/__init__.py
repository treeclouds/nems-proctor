from functools import cached_property

from django.utils.module_loading import import_string


class LazyObject:
    def __init__(self, import_path):
        self._import_path = import_path
        self._object = None

    def __get__(self, instance, owner):
        if self._object is None:
            self._object = import_string(self._import_path)
        return self._object


class LazyMiddlewareLoader:
    @cached_property
    def tenant_middleware(self):
        """Lazy loads TenantMiddleware class"""
        return import_string("nems_proctor.utils.middlewares.tenant.TenantMiddleware")

    @cached_property
    def company_filter_queryset(self):
        """Lazy loads CompanyFilterQuerySet class"""
        return import_string(
            "nems_proctor.utils.middlewares.tenant.CompanyFilterQuerySet",
        )

    @cached_property
    def company_filter_model(self):
        """Lazy loads CompanyFilterModel class"""
        return import_string("nems_proctor.utils.middlewares.tenant.CompanyFilterModel")

    @cached_property
    def get_current_company_id(self):
        """Lazy loads get_current_company_id function"""
        return import_string(
            "nems_proctor.utils.middlewares.tenant.get_current_company_id",
        )

    @cached_property
    def get_current_user(self):
        """Lazy loads get_current_user function"""
        return import_string("nems_proctor.utils.middlewares.tenant.get_current_user")


_loader = LazyMiddlewareLoader()

# Export the lazy-loaded classes and functions with their original PascalCase names
TenantMiddleware = _loader.tenant_middleware
CompanyFilterQuerySet = _loader.company_filter_queryset
CompanyFilterModel = _loader.company_filter_model
get_current_company_id = _loader.get_current_company_id
get_current_user = _loader.get_current_user

__all__ = [
    "TenantMiddleware",
    "CompanyFilterQuerySet",
    "CompanyFilterModel",
    "get_current_company_id",
    "get_current_user",
]
