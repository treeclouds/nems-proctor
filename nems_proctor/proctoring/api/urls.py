from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import GetSessionsByExamAndTaker
from .views import GetSessionsPhotoBySession
from .views import GetSessionsRecordBySession
from .views import GetTakersByExam

router = DefaultRouter()


urlpatterns = [
    path("", include(router.urls)),
    path(
        "sessions/takers/<str:exam_code>/",
        GetTakersByExam.as_view(),
        name="get-takers-by-exam",
    ),
    path(
        "sessions/<int:session_id>/photos/",
        GetSessionsPhotoBySession.as_view(),
        name="get-session-photos-by-session",
    ),
    path(
        "sessions/<int:session_id>/records/",
        GetSessionsRecordBySession.as_view(),
        name="get-session-records-by-session",
    ),
    path(
        "sessions/<str:exam_code>/<str:taker_username>/",
        GetSessionsByExamAndTaker.as_view(),
        name="get-sessions-by-exam-and-taker",
    ),
]
