from django.contrib.auth import get_user_model
from django.db.models import ObjectDoesNotExist
from rest_framework import serializers

from nems_proctor.proctoring.models import Exam
from nems_proctor.proctoring.models import Session
from nems_proctor.proctoring.models import SessionPhoto
from nems_proctor.proctoring.models import SessionRecord
from nems_proctor.users.models import User


class CreateUserSlugRelatedField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(**{self.slug_field: data})
        except ObjectDoesNotExist:
            user_model = get_user_model()
            user, created = user_model.objects.get_or_create(username=data)
            return user


class SessionSerializer(serializers.ModelSerializer):
    taker = CreateUserSlugRelatedField(
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
        return super().create(validated_data)

    def update(self, instance, validated_data):
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


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = "__all__"


class GetTakersByExamSerializer(serializers.ModelSerializer):
    attempts_count = serializers.IntegerField(read_only=True)
    latest_attempt = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "attempts_count", "latest_attempt")
