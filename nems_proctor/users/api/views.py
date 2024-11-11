from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_field
from rest_framework import permissions
from rest_framework import serializers
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.parsers import FormParser
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from nems_proctor.users.api.serializers import UserSerializer
from nems_proctor.users.models import BaseImage
from nems_proctor.users.models import User


class BaseImageUploadSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.ImageField(
            max_length=1000000,
            allow_empty_file=False,
            use_url=True,
        ),
        write_only=True,
    )


class ImageDetailSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField()

    class Meta:
        model = BaseImage
        fields = ["path", "uploaded_at"]

    def get_path(self, obj):
        return obj.image.url if obj.image else None


class UserBaseImagesSerializer(serializers.Serializer):
    user = serializers.IntegerField(source="id")
    images = serializers.SerializerMethodField()

    @extend_schema_field(
        [
            {
                "path": str,
                "uploaded_at": str,
            },
        ],
    )
    def get_images(self, obj):
        base_images = obj.baseimage_set.all()
        return ImageDetailSerializer(base_images, many=True).data


@extend_schema(tags=["User"])
class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        methods=["POST"],
        request=BaseImageUploadSerializer,
        responses={201: UserBaseImagesSerializer},
        description="Upload multiple base images for the user",
    )
    @extend_schema(
        methods=["GET"],
        responses={200: UserBaseImagesSerializer},
        description="Get all base images for the user",
    )
    @action(
        detail=True,
        methods=["get", "post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def base_images(self, request, username=None):
        user = self.get_object()
        if request.method == "GET":
            serializer = UserBaseImagesSerializer(user)
            return Response(serializer.data)
        if request.method == "POST":
            files = request.FILES.getlist("images", [])
            if not files:
                return Response(
                    {"error": "No images provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            for image in files:
                user.upload_base_image(image)

            serializer = UserBaseImagesSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
