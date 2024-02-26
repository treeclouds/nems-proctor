from drf_spectacular.utils import extend_schema
from proctoring.models import Session
from proctoring.models import SessionPhoto
from proctoring.models import SessionRecord
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .serializers import SessionPhotoCreateSerializer
from .serializers import SessionPhotoSerializer
from .serializers import SessionRecordCreateSerializer
from .serializers import SessionRecordSerializer
from .serializers import SessionSerializer


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    tags = ["Session"]

    @extend_schema(
        request=SessionPhotoCreateSerializer,
        responses={201: SessionPhotoCreateSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="add_photo",
        parser_classes=[MultiPartParser, FormParser],
    )
    def add_photo(self, request, pk=None):
        session = self.get_object()
        serializer = SessionPhotoCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(session=session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=SessionRecordCreateSerializer,
        responses={201: SessionRecordCreateSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="add_record",
        parser_classes=[MultiPartParser, FormParser],
    )
    def add_record(self, request, pk=None):
        session = self.get_object()
        serializer = SessionRecordCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(session=session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SessionRecordViewSet(viewsets.ModelViewSet):
    queryset = SessionRecord.objects.all()
    serializer_class = SessionRecordSerializer
    tags = ["Session Record"]


class SessionPhotoViewSet(viewsets.ModelViewSet):
    queryset = SessionPhoto.objects.all()
    serializer_class = SessionPhotoSerializer
    tags = ["Session Photo"]
