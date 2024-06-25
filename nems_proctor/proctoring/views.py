from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from .forms import SessionPhotoForm  # Assuming you have these forms defined
from .forms import SessionRecordForm  # Assuming you have these forms defined
from .models import Exam
from .models import Session


class SessionListView(ListView):
    """
    View for listing all exam sessions.
    """

    model = Session
    template_name = "sessions/session_list.html"
    context_object_name = "sessions"


class SessionCreateView(CreateView):
    """
    View for creating a new exam session.
    """

    model = Session
    fields = ["exam", "taker", "proctor", "is_active"]
    template_name = "sessions/session_form.html"
    success_url = "/sessions/"

    def form_valid(self, form):
        # Additional processing can be done here if necessary
        return super().form_valid(form)


class SessionRecordUploadView(View):
    """
    View for uploading a recording associated with a session.
    """

    def get(self, request, *args, **kwargs):
        form = SessionRecordForm()
        return render(request, "sessions/sessionrecord_form.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = SessionRecordForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("session_list")  # Redirect to the list of sessions
        return render(request, "sessions/sessionrecord_form.html", {"form": form})


class SessionPhotoUploadView(View):
    """
    View for uploading a photo for a session.
    """

    def get(self, request, *args, **kwargs):
        form = SessionPhotoForm()
        return render(request, "sessions/sessionphoto_form.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = SessionPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("session_list")  # Redirect to the list of sessions
        return render(request, "sessions/sessionphoto_form.html", {"form": form})


class ExamCreateView(LoginRequiredMixin, CreateView):
    model = Exam
    fields = ["exam_title", "exam_code", "description"]

    def form_valid(self, form):
        form.instance.company_id = self.request.user.company_id
        return super().form_valid(form)


class ExamUpdateView(LoginRequiredMixin, UpdateView):
    model = Exam
    fields = ["exam_title", "exam_code", "description"]

    def form_valid(self, form):
        form.instance.company_id = self.request.user.company_id
        return super().form_valid(form)
