import threading

from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models.query import QuerySet
from django.urls import resolve
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin

_thread_locals = threading.local()

# Error messages as constants
COMPANY_REQUIRED_ERROR = "Company ID is required"
OBJECT_NOT_FOUND_ERROR = "Object not found in company scope"


def get_current_company_id() -> int | None:
    return getattr(_thread_locals, "company_id", None)


def get_current_user():
    return getattr(_thread_locals, "user", None)


class TenantMiddleware:
    """Middleware for handling company-based multitenancy"""

    EXEMPT_PATHS = {
        "/admin/",
        "/api/schema/",
        "/api/auth/",
        "/swagger/",
        "/redoc/",
        "/api/token/",
    }

    def __init__(self, get_response):
        self.get_response = get_response
        self._patched_views = set()

    def __call__(self, request):
        # Check if path is exempt
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return self.get_response(request)

        # Set tenant context
        if hasattr(request, "user") and request.user.is_authenticated:
            _thread_locals.company_id = request.user.company_id
            _thread_locals.user = request.user

        try:
            # Get the view
            resolved = resolve(request.path)
            if hasattr(resolved, "func"):
                view = resolved.func
                # Handle class-based views
                if hasattr(view, "view_class"):
                    view_class = view.view_class
                    if issubclass(view_class, APIView | ViewSetMixin):
                        self._patch_view_class(view_class)
                # Handle viewsets
                elif hasattr(view, "cls") and issubclass(
                    view.cls,
                    APIView | ViewSetMixin,
                ):
                    self._patch_view_class(view.cls)

            return self.get_response(request)
        finally:
            # Clean up thread local storage
            _thread_locals.company_id = None
            _thread_locals.user = None

    def _patch_view_class(self, view_class):
        """Patch a view class to enforce tenant isolation"""
        # Only patch each view class once
        if view_class in self._patched_views:
            return

        self._patched_views.add(view_class)
        self._apply_queryset_patch(view_class)
        self._apply_object_patch(view_class)

    def _apply_queryset_patch(self, view_class):
        """Apply the get_queryset patch to the view class"""
        original_get_queryset = getattr(view_class, "get_queryset", None)

        def get_queryset(self, *args, **kwargs):
            """Wrapped get_queryset method"""
            if original_get_queryset:
                queryset = original_get_queryset(self, *args, **kwargs)
            else:
                queryset = self.queryset.all()

            user = get_current_user()

            if not user or not user.is_authenticated:
                return queryset.none()

            if user.is_superuser:
                return queryset

            if hasattr(queryset.model, "company_id"):
                return queryset.filter(company_id=user.company_id)
            return queryset

        if hasattr(view_class, "get_queryset") or hasattr(view_class, "queryset"):
            view_class.get_queryset = get_queryset

    def _apply_object_patch(self, view_class):
        """Apply the get_object patch to the view class"""
        original_get_object = getattr(view_class, "get_object", None)

        def get_object(self, *args, **kwargs):
            """Wrapped get_object method"""
            if original_get_object:
                obj = original_get_object(self, *args, **kwargs)
            else:
                queryset = self.get_queryset()
                lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
                filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
                obj = queryset.get(**filter_kwargs)

            user = get_current_user()

            if user.is_superuser:
                return obj

            if hasattr(obj, "company_id") and obj.company_id != user.company_id:
                raise NotFound(OBJECT_NOT_FOUND_ERROR)
            return obj

        if hasattr(view_class, "get_object"):
            view_class.get_object = get_object


class CompanyFilterQuerySet(QuerySet):
    """QuerySet that automatically filters by company_id"""

    def filter_by_company(self):
        """Public method to filter queryset by company"""
        user = get_current_user()
        company_id = get_current_company_id()

        if user and user.is_superuser:
            return self

        if company_id is not None and hasattr(self.model, "company_id"):
            return self.filter(company_id=company_id)
        return self

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs).filter_by_company()

    def all(self, *args, **kwargs):
        return super().all(*args, **kwargs).filter_by_company()

    def get(self, *args, **kwargs):
        queryset = self.filter_by_company()
        return super(CompanyFilterQuerySet, queryset).get(*args, **kwargs)


class CompanyFilterModel(models.Model):
    """Abstract model that implements company filtering"""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.company_id:
            self.company_id = get_current_company_id()
        if not self.company_id:
            raise PermissionDenied(COMPANY_REQUIRED_ERROR)
        super().save(*args, **kwargs)
