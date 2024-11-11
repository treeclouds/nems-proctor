import base64
import io
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import BinaryField
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import ForeignKey
from django.db.models import ImageField
from django.db.models import Index
from django.db.models.deletion import CASCADE
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from PIL import Image
from PIL import UnidentifiedImageError

from nems_proctor.core.models import BaseModel

# Error messages as constants
NO_IMAGE_ERROR = "No image file provided"
IMAGE_TOO_LARGE_ERROR = "Image file too large ( > 5MB )"
VALID_EXTENSIONS = [".jpg", ".jpeg", ".png"]
INVALID_EXTENSION_ERROR = (
    f"Unsupported file extension. Allowed: {', '.join(VALID_EXTENSIONS)}"
)
UPLOAD_FAILED_ERROR = "Failed to upload image: {error}"
IMAGE_PROCESSING_ERROR = "Error processing image: {error}"


def process_image(image_file) -> tuple[bytes, bytes]:
    """
    Process image file to create both regular and base64 versions
    Returns tuple of (processed_image_bytes, base64_bytes)
    """
    try:
        # Open and convert image to RGB if necessary
        img = Image.open(image_file)
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Convert to JPEG format for Rekognition
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        image_bytes = buffer.getvalue()
    except UnidentifiedImageError as e:
        raise ValidationError(IMAGE_PROCESSING_ERROR.format(error=str(e))) from e
    except OSError as e:
        raise ValidationError(IMAGE_PROCESSING_ERROR.format(error=str(e))) from e
    else:
        # Create base64 version only if image processing succeeded
        base64_bytes = base64.b64encode(image_bytes)
        return image_bytes, base64_bytes


def get_base_image_path(instance, filename) -> str:
    """
    Generate the upload path for base images.
    Format: users/base_image/{user_id}/{timestamp}_{filename}
    """
    # Get the file extension
    ext = Path(filename).suffix

    # Use current timestamp with timezone
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")

    # Generate new filename
    new_filename = f"{instance.user.id}_{timestamp}{ext}"

    # Convert to string as Django's FileField expects a string path
    return str(Path("users") / "base_image" / str(instance.user.id) / new_filename)


def validate_image(image):
    """Validate the image file"""
    if not image:
        raise ValidationError(NO_IMAGE_ERROR)

    # Check file size (e.g., max 5MB)
    if image.size > 5 * 1024 * 1024:
        raise ValidationError(IMAGE_TOO_LARGE_ERROR)

    # Check file extension
    ext = Path(image.name).suffix.lower()
    if ext not in VALID_EXTENSIONS:
        raise ValidationError(INVALID_EXTENSION_ERROR)


class User(AbstractUser, BaseModel):
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]

    def get_absolute_url(self) -> str:
        return reverse("users:detail", kwargs={"username": self.username})

    def upload_base_image(self, image) -> Optional["BaseImage"]:
        """
        Upload a new base image for face recognition.
        Processes the image for both regular storage and Rekognition use.
        Returns the created BaseImage instance.
        Raises ValidationError if image is invalid.
        """
        try:
            # Validate the image
            validate_image(image)

            # Process image for both storage and Rekognition
            image_bytes, base64_bytes = process_image(image)

            # Create ContentFile for regular image storage
            content_file = ContentFile(image_bytes)
            content_file.name = Path(image.name).name

            # Create the base image with both regular and base64 versions
            return BaseImage.objects.create(
                user=self,
                image=content_file,
                image_base64=base64_bytes,
                company_id=self.company_id,
            )
        except ValidationError as e:
            raise ValidationError(str(e)) from e
        except OSError as e:
            error_msg = UPLOAD_FAILED_ERROR.format(error=str(e))
            raise ValidationError(error_msg) from e

    def get_base_images(self):
        """Retrieve all base images for the user."""
        return self.baseimage_set.all().order_by("-uploaded_at")

    def delete_base_images(self):
        """Delete all base images for the user."""
        for base_image in self.baseimage_set.all():
            if base_image.image and default_storage.exists(base_image.image.path):
                default_storage.delete(base_image.image.path)
        self.baseimage_set.all().delete()


class BaseImage(BaseModel):
    """Model to store base images for face recognition."""

    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    image = ImageField(
        upload_to=get_base_image_path,
        validators=[validate_image],
    )
    image_base64 = BinaryField(
        verbose_name=_("Base64 Image Data"),
        help_text=_(
            "Base64 encoded image data for Rekognition use",
        ),  # Shortened help text
        null=True,
    )
    uploaded_at = DateTimeField(auto_now_add=True)

    def get_base64_string(self) -> str | None:
        """
        Get the base64 string representation for Rekognition.
        Returns base64 encoded string if available, None otherwise.
        """
        if self.image_base64:
            return self.image_base64.decode("utf-8")
        return None

    def save(self, *args, **kwargs):
        """Override save method to set company_id from user and process image"""
        if not self.company_id and self.user:
            self.company_id = self.user.company_id

        # If image changed and no base64 data provided, process image
        if self.image and not self.image_base64:
            _, base64_bytes = process_image(self.image)
            self.image_base64 = base64_bytes

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete method to ensure file is removed from storage"""
        if self.image and default_storage.exists(self.image.path):
            default_storage.delete(self.image.path)
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [
            Index(fields=["company_id"]),
            Index(fields=["user"]),
            Index(fields=["uploaded_at"]),
        ]
