from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import SessionPhotoViewSet
from .views import SessionRecordViewSet
from .views import SessionViewSet

router = DefaultRouter()
router.register(r"sessions", SessionViewSet)
router.register(r"sessionrecords", SessionRecordViewSet)
router.register(r"sessionphotos", SessionPhotoViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
