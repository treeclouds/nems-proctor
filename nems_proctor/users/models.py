from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import ForeignKey
from django.db.models import ImageField
from django.db.models.deletion import CASCADE
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from nems_proctor.core.models import BaseModel

# Error messages as constants
NO_IMAGE_ERROR = "No image file provided"
IMAGE_TOO_LARGE_ERROR = "Image file too large ( > 5MB )"
VALID_EXTENSIONS = [".jpg", ".jpeg", ".png"]
INVALID_EXTENSION_ERROR = (
    f"Unsupported file extension. Allowed: {', '.join(VALID_EXTENSIONS)}"
)
UPLOAD_FAILED_ERROR = "Failed to upload image: {error}"


def get_base_image_path(instance, filename):
    """
    Generate the upload path for base images.
    Format: users/base_image/{user_id}/{filename}
    """
    # Get the file extension
    ext = filename.split(".")[-1]
    # Generate new filename using the timestamp to avoid conflicts
    new_filename = (
        f"{instance.user.id}_{instance.uploaded_at.strftime('%Y%m%d_%H%M%S')}.{ext}"
    )
    return Path("users") / "base_image" / str(instance.user.id) / new_filename


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

    def upload_base_image(self, image):
        """
        Upload a new base image for face recognition.
        Returns the created BaseImage instance.
        Raises ValidationError if image is invalid.
        """
        try:
            # Validate the image
            validate_image(image)
            # Create the base image with company_id
            return BaseImage.objects.create(
                user=self,
                image=image,
                company_id=self.company_id,  # Explicitly set company_id
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
    uploaded_at = DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Override save method to set company_id from user"""
        if not self.company_id and self.user:
            self.company_id = self.user.company_id
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete method to ensure file is removed from storage"""
        if self.image and default_storage.exists(self.image.path):
            default_storage.delete(self.image.path)
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ["-uploaded_at"]
