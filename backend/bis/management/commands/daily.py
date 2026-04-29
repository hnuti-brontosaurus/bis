from datetime import date

from bis import emails
from bis.helpers import try_to_run
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        try_to_run(emails.event_not_closed_10_days)
        try_to_run(emails.event_not_closed_20_days)
        try_to_run(emails.send_automatic_feedback)
        try_to_run(emails.qualification_about_to_end)
        try_to_run(emails.qualification_ended)
        try_to_run(emails.recurrent_donor_stopped)
        try_to_run(emails.new_recurrent_donors)
        try_to_run(emails.donated_10k)
        try_to_run(emails.donates_for_years)

        today = date.today()

        # weekly
        if today.weekday() == 0:
            try_to_run(emails.events_summary)
            try_to_run(emails.opportunities_created_summary)
            try_to_run(emails.expressed_engagement_in_feedback)

        day_of_year = (today.day, today.month)

        if day_of_year == (15, 10):
            try_to_run(emails.fill_memberships, call=1)
        if day_of_year == (27, 10):
            try_to_run(emails.fill_memberships, call=2)

        if day_of_year == (31, 1):
            try_to_run(emails.qualification_ends_this_year)

        if day_of_year in [
            (15, 1),
            (15, 3),
            (15, 5),
            (15, 9),
            (30, 11),
        ]:
            try_to_run(emails.send_opportunities_summary)
