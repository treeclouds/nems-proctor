from django.contrib.auth import get_user_model
from rest_framework import serializers

from nems_proctor.proctoring.models import Exam
from nems_proctor.proctoring.models import Session
from nems_proctor.proctoring.models import SessionPhoto
from nems_proctor.proctoring.models import SessionRecord


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

    def create(self, validated_data):
        taker_data = validated_data.get("taker")
        if isinstance(taker_data, str):
            user = get_user_model()
            taker, created = user.objects.get_or_create(username=taker_data)
            validated_data["taker"] = taker
        return super().create(validated_data)

    def update(self, instance, validated_data):
        taker_data = validated_data.get("taker")
        if taker_data and isinstance(taker_data, str):
            user = get_user_model()
            taker, created = user.objects.get_or_create(username=taker_data)
            validated_data["taker"] = taker
        return super().update(instance, validated_data)

    def end_session(self, instance, validated_data):
        instance.end_session()
        return super().update(instance, validated_data)


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
