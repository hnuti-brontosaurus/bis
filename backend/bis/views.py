from urllib.parse import urlencode

from django import forms
from django.contrib.auth import REDIRECT_FIELD_NAME, login
from django.core.exceptions import ValidationError
from django.forms import EmailField, Form, NumberInput, TextInput
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView
from rest_framework.exceptions import AuthenticationFailed, Throttled

from bis import emails
from bis.models import User
from login_code.models import LoginCode
from translation.translate import _


class LoginForm(Form):
    email = EmailField(
        label=_("generic.email"), widget=TextInput(attrs={"autofocus": "autofocus"})
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if not User.objects.filter(all_emails__email=email).exists():
            raise ValidationError(_("login.user_does_not_exist"))

        user = User.objects.get(all_emails__email=email)
        try:
            login_code = LoginCode.make(user)
        except Throttled:
            raise ValidationError(_("login.too_many_retries"))

        emails.login_code(email, login_code.code)

        return email


class LoginView(FormView):
    template_name = "bis/login.html"
    form_class = LoginForm

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        args = {"email": email}
        next = self.request.GET.get(REDIRECT_FIELD_NAME)
        if next:
            args[REDIRECT_FIELD_NAME] = next

        url = reverse("code")
        query_string = urlencode(args)
        url = f"{url}?{query_string}"
        return HttpResponseRedirect(url)


class CodeForm(Form):
    code = forms.IntegerField(widget=NumberInput(attrs={"autofocus": "autofocus"}))


class CodeView(FormView):
    template_name = "bis/code.html"
    form_class = CodeForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["code"].label = _(
            "login.code_form_header", email=self.request.GET["email"]
        )
        return form

    def form_valid(self, form):
        email = self.request.GET["email"]
        code = form.cleaned_data["code"]
        next = self.request.GET.get(REDIRECT_FIELD_NAME, "/admin/")
        if not next:
            next = "/admin/"

        user = User.objects.get(all_emails__email=email)
        try:
            LoginCode.is_valid(user, code)
            login(self.request, user)

            return HttpResponseRedirect(next)

        except Throttled:
            form.add_error("code", _("login.too_many_retries"))

        except AuthenticationFailed:
            form.add_error("code", _("login.code_invalid"))

        return self.form_invalid(form)
