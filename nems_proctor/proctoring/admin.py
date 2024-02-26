from django.contrib import admin

from .models import Exam
from .models import Session
from .models import SessionPhoto
from .models import SessionRecord


class SessionRecordInline(admin.TabularInline):
    model = SessionRecord
    extra = 0  # Removes extra empty forms


class SessionPhotoInline(admin.TabularInline):
    model = SessionPhoto
    extra = 0  # Removes extra empty forms


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    inlines = [SessionRecordInline, SessionPhotoInline]
    list_display = (
        "exam",
        "taker",
        "proctor",
        "start_time",
        "is_active",
    )  # Customize as needed
    search_fields = (
        "exam__exam_title",
        "taker__username",
        "proctor__username",
    )  # Customize as needed


admin.site.register(Exam)
admin.site.register(
    SessionRecord,
)  # Optional if you want SessionRecord to be editable standalone
admin.site.register(
    SessionPhoto,
)  # Optional if you want SessionPhoto to be editable standalone
