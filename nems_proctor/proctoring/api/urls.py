from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import GetTakersByExam

router = DefaultRouter()


urlpatterns = [
    path("", include(router.urls)),
    path(
        "sessions/takers/<str:exam_code>/",
        GetTakersByExam.as_view(),
        name="get-takers-by-exam",
    ),
]
