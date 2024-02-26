from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import OpenApiTypes
from drf_spectacular.utils import extend_schema
from proctoring.models import Exam
from proctoring.models import Session
from proctoring.models import SessionPhoto
from proctoring.models import SessionRecord
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from users.api.serializers import UserSerializer

from .serializers import SessionPhotoCreateSerializer
from .serializers import SessionPhotoSerializer
from .serializers import SessionRecordCreateSerializer
from .serializers import SessionRecordSerializer
from .serializers import SessionSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="taker",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter sessions by taker username.",
        ),
        OpenApiParameter(
            name="exam",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter sessions by exam code.",
        ),
        OpenApiParameter(
            name="proctor",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter sessions by proctor username.",
        ),
    ],
)
class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    tags = ["Session"]

    def get_queryset(self):
        queryset = super().get_queryset()
        taker_username = self.request.query_params.get("taker")
        exam_code = self.request.query_params.get("exam")
        proctor_username = self.request.query_params.get("proctor")

        if taker_username:
            queryset = queryset.filter(taker__username=taker_username)
        if exam_code:
            queryset = queryset.filter(exam__exam_code=exam_code)
        if proctor_username:
            queryset = queryset.filter(proctor__username=proctor_username)
        return queryset

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

        if not session.is_active:
            error_message = "This session has been closed and cannot accept new photo."
            return Response(
                {"detail": f"{error_message}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

        if not session.is_active:
            error_message = "This session has been closed and cannot accept new record."
            return Response(
                {"detail": f"{error_message}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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


class GetTakersByExam(APIView):
    def get(self, request, exam_code):
        exam = get_object_or_404(Exam, exam_code=exam_code)
        sessions = Session.objects.filter(exam=exam).distinct("taker__id")
        takers = [session.taker for session in sessions]

        serializer = UserSerializer(takers, many=True, context={"request": request})

        return Response(serializer.data)
