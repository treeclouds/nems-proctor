from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from nems_proctor.users.forms import UserAdminChangeForm
from nems_proctor.users.forms import UserAdminCreationForm
from nems_proctor.users.models import User

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
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
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "name", "is_superuser"]
    search_fields = ["name"]
