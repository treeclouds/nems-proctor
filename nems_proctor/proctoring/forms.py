from django import forms

from .models import SessionPhoto
from .models import SessionRecord


class SessionRecordForm(forms.ModelForm):
    """
    Form for uploading a recording associated with a session.
    """

    class Meta:
        model = SessionRecord
        fields = ["session", "recording_type", "file"]
        widgets = {
            "session": forms.Select(attrs={"class": "form-control"}),
            "recording_type": forms.Select(attrs={"class": "form-control"}),
            "file": forms.FileInput(attrs={"class": "form-control"}),
        }


class SessionPhotoForm(forms.ModelForm):
    """
    Form for uploading a photo for a session.
    """

    class Meta:
        model = SessionPhoto
        fields = ["session", "photo"]
        widgets = {
            "session": forms.Select(attrs={"class": "form-control"}),
            "photo": forms.FileInput(attrs={"class": "form-control"}),
        }
