from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


class RecordingType(models.TextChoices):
    """Defines the types of recordings that can be associated with a session."""

    VIDEO = "video", "Video"
    AUDIO = "audio", "Audio"
    SCREENSHOT = "screenshot", "Screenshot"


class Exam(models.Model):
    exam_title = models.CharField(
        max_length=255,
        verbose_name="Exam Title",
    )
    exam_code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Exam Code",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date Created",
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated",
    )

    class Meta:
        verbose_name = "Exam"
        verbose_name_plural = "Exams"

    def __str__(self):
        return f"{self.exam_title} ({self.exam_code})"


class Session(models.Model):
    """
    Represents an exam session,
    including details about the exam, participant, and proctor
    """

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, db_index=True)
    taker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_sessions",
        db_index=True,
    )
    proctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="proctoring_sessions",
        null=True,
        blank=True,
        db_index=True,
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        """
        Returns a string representation of the session,
        including exam title and taker username.
        """
        return f"Session for '{self.exam.exam_title}' by {self.taker.username}"


class SessionRecord(models.Model):
    """
    Stores a record associated with a session,
    including type and file of the recording.
    """

    session = models.ForeignKey(
        "Session",
        on_delete=models.CASCADE,
    )
    recording_type = models.CharField(
        max_length=10,
        choices=RecordingType.choices,
    )
    file = models.FileField(
        upload_to="recordings/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["mp4", "webm", "ogg", "jpg", "png"],
            ),
        ],
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the recording,
        including its type and associated session ID.
        """
        return f"{self.recording_type} recording for session {self.session.id}"

    def clean(self):
        """
        Validates the file extension based on the recording type.
        Raises a ValidationError if the file's extension is not allowed
        for the recording type.
        """
        valid_extensions = {
            RecordingType.VIDEO: ["mp4", "webm", "ogg"],
            RecordingType.AUDIO: ["mp3", "wav", "ogg"],
            RecordingType.SCREENSHOT: ["jpg", "png"],
        }
        extension = self.file.name.split(".")[-1].lower()  # Get file extension
        if extension not in valid_extensions[self.recording_type]:
            error_message = f"""
                Invalid file extension for {self.recording_type} recording type.
                Allowed extensions: {valid_extensions[self.recording_type]}."""
            raise ValidationError(error_message)


class SessionPhoto(models.Model):
    """
    Represents a photo taken during a session,
    storing the image file and capture time.
    """

    session = models.ForeignKey("Session", on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="photos/")
    captured_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the photo,
        including session ID and capture time.
        """
        return f"Photo for session {self.session.id} captured at {self.captured_at}"
