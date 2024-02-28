from django.contrib.auth import get_user_model
from nems_proctor.proctoring.models import Exam
from nems_proctor.proctoring.models import Session
from nems_proctor.proctoring.models import SessionPhoto
from nems_proctor.proctoring.models import SessionRecord
from rest_framework import serializers


class SessionSerializer(serializers.ModelSerializer):
    taker = serializers.SlugRelatedField(
        slug_field="username",
        queryset=get_user_model().objects.all(),
    )
    proctor = serializers.SlugRelatedField(
        slug_field="username",
        queryset=get_user_model().objects.all(),
        allow_null=True,  # Assuming proctor can be null
        required=False,  # Assuming proctor is not required
    )
    exam = serializers.SlugRelatedField(
        slug_field="exam_code",
        queryset=Exam.objects.all(),
    )

    class Meta:
        model = Session
        fields = "__all__"


class SessionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionRecord
        fields = "__all__"


class SessionRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionRecord
        fields = ("recording_type", "file")


class SessionPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionPhoto
        fields = "__all__"


class SessionPhotoCreateSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(max_length=None, use_url=True)

    class Meta:
        model = SessionPhoto
        fields = ("photo",)
