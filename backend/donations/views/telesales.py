from django import forms
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone

from categories.models import DonorEventCategory
from donations.models import Donor, DonorEvent, FundraisingCampaign
from donations.telesales import (
    get_donor_campaign_context,
    get_finished,
    get_reminders_due,
    get_worklist,
)

OUTCOME_CHOICES = [
    ("call_no_answer", "Nezvedl"),
    ("call_declined", "Odmítl"),
    ("call_postponed", "Odloženo"),
    ("call_reached", "Odvoláno"),
]

OUTCOME_LABELS = dict(OUTCOME_CHOICES)


class CallForm(forms.Form):
    outcome = forms.ChoiceField(choices=OUTCOME_CHOICES)
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    pledge = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))
    reminder = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"],
    )
    do_not_call = forms.BooleanField(required=False, label="Už nevolat")
    do_not_solicit = forms.BooleanField(required=False, label="Už nežádat o dar")

    def clean(self):
        cleaned = super().clean()
        outcome = cleaned.get("outcome")
        reminder = cleaned.get("reminder")
        now = timezone.now()

        if outcome == "call_postponed":
            if not reminder:
                self.add_error("reminder", "Připomenutí je povinné pro odložení.")
            elif reminder <= now:
                self.add_error("reminder", "Připomenutí musí být v budoucnosti.")

        if outcome == "call_reached" and reminder and reminder <= now:
            self.add_error("reminder", "Připomenutí musí být v budoucnosti.")

        return cleaned


def _has_permission(request):
    return request.user.is_fundraiser or request.user.is_superuser


def telesales_worklist_view(model_admin, request, campaign_id):
    if not _has_permission(request):
        return HttpResponseForbidden("Nemáš oprávnění pro telesales.")

    campaign = get_object_or_404(FundraisingCampaign, pk=campaign_id)
    now = timezone.now()

    reminders = list(get_reminders_due(campaign))
    worklist = list(get_worklist(campaign))
    finished = list(get_finished(campaign))

    return TemplateResponse(
        request,
        "donations/telesales/worklist.html",
        {
            **model_admin.admin_site.each_context(request),
            "title": "Telesales",
            "campaign": campaign,
            "reminders": reminders,
            "worklist": worklist,
            "finished": finished,
            "now": now,
            "opts": FundraisingCampaign._meta,
        },
    )


def telesales_call_view(model_admin, request, campaign_id, donor_id):
    if not _has_permission(request):
        return HttpResponseForbidden("Nemáš oprávnění pro telesales.")

    campaign = get_object_or_404(FundraisingCampaign, pk=campaign_id)
    donor = get_object_or_404(Donor, pk=donor_id)

    if request.method == "POST":
        form = CallForm(request.POST)
        if form.is_valid():
            outcome = form.cleaned_data["outcome"]
            DonorEvent.objects.create(
                donor=donor,
                event_type=DonorEventCategory.objects.get(slug=outcome),
                campaign=campaign,
                note=form.cleaned_data["note"],
                pledge=form.cleaned_data["pledge"],
                reminder=form.cleaned_data["reminder"],
                created_by=request.user,
            )
            donor.do_not_call = form.cleaned_data["do_not_call"]
            donor.do_not_solicit = form.cleaned_data["do_not_solicit"]
            donor.save(update_fields=["do_not_call", "do_not_solicit"])
            messages.success(
                request, f"Zaznamenáno: {donor} — {OUTCOME_LABELS[outcome]}."
            )
            return HttpResponseRedirect(
                reverse("admin:donations_telesales_worklist", args=[campaign.id])
            )
    else:
        form = CallForm(
            initial={
                "do_not_call": donor.do_not_call,
                "do_not_solicit": donor.do_not_solicit,
            }
        )

    donor_context = get_donor_campaign_context(donor, campaign)

    return TemplateResponse(
        request,
        "donations/telesales/call.html",
        {
            **model_admin.admin_site.each_context(request),
            "title": f"Zavolat: {donor}",
            "campaign": campaign,
            "donor": donor,
            "form": form,
            "donor_context": donor_context,
            "outcome_choices": OUTCOME_CHOICES,
            "opts": FundraisingCampaign._meta,
        },
    )
