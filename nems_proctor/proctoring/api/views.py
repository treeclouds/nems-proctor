from django.db.models import Count
from django.db.models import Max
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from nems_proctor.proctoring.models import Exam
from nems_proctor.proctoring.models import Session
from nems_proctor.proctoring.models import SessionPhoto
from nems_proctor.proctoring.models import SessionRecord
from nems_proctor.users.models import User

from .serializers import ExamSerializer
from .serializers import GetTakersByExamSerializer
from .serializers import SessionPhotoCreateSerializer
from .serializers import SessionPhotoSerializer
from .serializers import SessionRecordCreateSerializer
from .serializers import SessionRecordSerializer
from .serializers import SessionSerializer

sort_param = OpenApiParameter(
    name="sort",
    type="string",
    enum=["asc", "desc"],
    default="asc",
    description="""
        Sort order for taker username.
        Values: 'asc' (ascending), 'desc' (descending).
        Default is 'asc'.
        """,
)


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
    tags=["Session"],
)
class SessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows sessions to be viewed or edited.

    Query Parameters:
    - `taker`: Filter sessions by taker username.
    - `exam`: Filter sessions by exam code.
    - `proctor`: Filter sessions by proctor username.
    """

    queryset = Session.objects.all()
    serializer_class = SessionSerializer

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

    @action(detail=False, methods=["post"], url_path="start_session")
    def start_session(self, request):
        serializer = SessionSerializer(data=request.data)  # Use your updated serializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="end_session")
    def end_session(self, request, pk=None):
        """
        Ends an active session. Only authenticated users can end sessions.
        """
        session = self.get_queryset().get(pk=pk)

        if not session.is_active:
            error_message = "This session is already closed."
            return Response(
                {"detail": f"{error_message}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session.is_active = False
        session.save()

        return Response(
            {"detail": "Session successfully ended."},
            status=status.HTTP_200_OK,
        )

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
        """
        Add a photo to an active session.

        An active session is required to add a new photo. If the session is closed,
        the operation will be rejected.
        """
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
        """
        API endpoint for managing session records.

        Provides standard model viewset actions
        for example: (list, create, retrieve, update, destroy)
        to work with session records.
        """
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


@extend_schema(tags=["Session Record"])
class SessionRecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing session photos.

    Supports actions to list, create, retrieve, update, and delete session photos.
    """

    queryset = SessionRecord.objects.all()
    serializer_class = SessionRecordSerializer


@extend_schema(tags=["Session Photo"])
class SessionPhotoViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing session records.

    Supports actions to list, create, retrieve, update, and delete session photos.
    """

    queryset = SessionPhoto.objects.all()
    serializer_class = SessionPhotoSerializer


@extend_schema(tags=["Exam"])
class ExamViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing exams.

    Supports actions to list, create, retrieve, update, and delete exams.
    """

    queryset = Exam.objects.all()
    serializer_class = ExamSerializer


@extend_schema(tags=["Session"])
class GetTakersByExam(APIView):
    serializer_class = GetTakersByExamSerializer

    def get(self, request, exam_code):
        exam = get_object_or_404(Exam, exam_code=exam_code)
        sessions = (
            Session.objects.filter(exam=exam)
            .values("taker")
            .annotate(attempts_count=Count("id"), latest_attempt=Max("start_time"))
            .order_by("taker")
        )

        # Map session data to taker IDs
        session_data_map = {session["taker"]: session for session in sessions}

        # Fetch the user instances
        user_ids = session_data_map.keys()
        users = User.objects.filter(id__in=user_ids)

        # Annotate users with session data
        for user in users:
            user_data = session_data_map.get(user.id)
            user.attempts_count = user_data["attempts_count"]
            user.latest_attempt = user_data["latest_attempt"]

        serializer = self.serializer_class(
            users,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)


@extend_schema(
    tags=["Session"],
    parameters=[
        OpenApiParameter(
            name="sort",
            type=OpenApiTypes.STR,
            description="""
            Sorts the sessions by ID.
            Use 'asc' for ascending or 'desc' for descending order.
            Default is 'asc'.
            """,
            required=False,
        ),
    ],
)
class GetSessionsByExamAndTaker(APIView):
    """
    Retrieve a list of sessions for a given exam code and taker username.

    This endpoint provides a list of sessions
    who have the specified exam code and taker username.
    """

    serializer_class = SessionSerializer

    def get(self, request, exam_code, taker_username):
        exam = get_object_or_404(Exam, exam_code=exam_code)
        taker = get_object_or_404(User, username=taker_username)

        sort_order = request.query_params.get("sort", "asc")
        order_by = "-id" if sort_order == "desc" else "id"

        sessions = Session.objects.filter(exam=exam, taker=taker).order_by(order_by)
        session_count = sessions.count()
        session_photo_count = SessionPhoto.objects.filter(session__in=sessions).count()
        session_record_count = SessionRecord.objects.filter(
            session__in=sessions,
        ).count()

        data = {
            "count": session_count,
            "photo_count": session_photo_count,
            "record_count": session_record_count,
            "sessions": self.serializer_class(
                sessions,
                many=True,
                context={"request": request},
            ).data,
        }

        return Response(data)


@extend_schema(tags=["Session"])
class GetSessionsPhotoBySession(APIView):
    """
    Retrieve a list of photos for a given session id.

    This endpoint provides a list of photos
    who have sessions associated with the specified session id.
    """

    serializer_class = SessionPhotoSerializer

    def get(self, request, session_id):
        session = get_object_or_404(Session, id=session_id)
        photos = SessionPhoto.objects.filter(session=session)
        serializer = self.serializer_class(
            photos,
            many=True,
            context={"request": request},
        )
        data = {
            "count": photos.count(),
            "photos": serializer.data,
        }

        return Response(data)


@extend_schema(tags=["Session"])
class GetSessionsRecordBySession(APIView):
    """
    Retrieve a list of records for a given session id.

    This endpoint provides a list of records
    who have sessions associated with the specified session id.
    """

    serializer_class = SessionRecordSerializer

    def get(self, request, session_id):
        session = get_object_or_404(Session, id=session_id)
        records = SessionRecord.objects.filter(session=session)
        serializer = self.serializer_class(
            records,
            many=True,
            context={"request": request},
        )

        data = {
            "count": records.count(),
            "records": serializer.data,
        }

        return Response(data)
