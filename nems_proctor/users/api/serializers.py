from rest_framework import serializers

from nems_proctor.users.models import BaseImage
from nems_proctor.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["username", "name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"},
        }


class BaseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseImage
        fields = ["id", "user", "image", "uploaded_at"]
        read_only_fields = ["id", "user", "uploaded_at"]
