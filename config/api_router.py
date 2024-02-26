from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from nems_proctor.proctoring.api.views import SessionPhotoViewSet
from nems_proctor.proctoring.api.views import SessionRecordViewSet
from nems_proctor.proctoring.api.views import SessionViewSet
from nems_proctor.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("sessions", SessionViewSet)
router.register("session-photos", SessionPhotoViewSet)
router.register("session-records", SessionRecordViewSet)


app_name = "api"
urlpatterns = router.urls
