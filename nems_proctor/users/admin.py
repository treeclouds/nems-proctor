from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from nems_proctor.users.forms import UserAdminChangeForm
from nems_proctor.users.forms import UserAdminCreationForm
from nems_proctor.users.models import BaseImage
from nems_proctor.users.models import User

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    admin.site.login = login_required(admin.site.login)  # type: ignore[method-assign]


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ("id", "username", "name", "is_active", "is_staff")
        export_order = ("id", "username", "name", "is_active", "is_staff")


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin, ImportExportModelAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    resource_class = UserResource
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "company_id",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "name", "is_superuser"]
    search_fields = ["name"]


class BaseImageResource(resources.ModelResource):
    class Meta:
        model = BaseImage
        fields = ("id", "user", "image", "uploaded_at")
        export_order = ("id", "user", "image", "uploaded_at")


@admin.register(BaseImage)
class BaseImageAdmin(ImportExportModelAdmin):
    resource_class = BaseImageResource
    list_display = ["id", "user", "company_id", "image_preview", "uploaded_at"]
    list_filter = ["uploaded_at", "user", "company_id"]
    search_fields = ["user__username", "user__name", "company_id"]
    readonly_fields = ["image_preview", "uploaded_at", "company_id"]
    raw_id_fields = ["user"]

    @admin.display(
        description="Image Preview",
    )
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" />'
        return "No Image"


class BaseImageResource(resources.ModelResource):
    class Meta:
        model = BaseImage
        fields = ("id", "user", "company_id", "image", "uploaded_at")
        export_order = ("id", "user", "company_id", "image", "uploaded_at")
