import requests
from administration_units.models import AdministrationUnit
from bis.helpers import print_progress
from bis.models import User, UserAddress
from categories.models import DonationSourceCategory
from dateutil.parser import isoparse
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from donations.models import Donation, Donor


class Command(BaseCommand):
    help = "Import new donations from darujme"

    base_url = "https://www.darujme.cz/api/v1"
    api_secrets = (
        f"apiId={settings.DARUJME_API_KEY}&apiSecret={settings.DARUJME_SECRET}"
    )

    def project_data(self, project_id):
        url = f"{self.base_url}/project/{project_id}?{self.api_secrets}"

        return requests.get(url).json()

    def handle(self, *args, **options):
        if not settings.DARUJME_API_KEY:
            return

        url = f"{self.base_url}/organization/206/pledges-by-filter?{self.api_secrets}"

        data = requests.get(url).json()

        projects = {}

        for i, pledge in enumerate(data["pledges"]):
            print_progress("importing donations", i, len(data["pledges"]))

            project_id = pledge["projectId"]
            if project_id not in projects:
                name = self.project_data(project_id)["project"]["title"]["cs"]
                projects[project_id] = DonationSourceCategory.objects.update_or_create(
                    _import_id=project_id,
                    defaults=dict(name=name, slug=slugify(name)[:50]),
                )[0]

            donation_source = projects[project_id]
            donor = pledge["donor"]
            custom = pledge["customFields"]

            transactions = pledge["transactions"]
            transactions = [
                t for t in transactions if t["state"] == "sent_to_organization"
            ]

            if not transactions:
                continue

            email = donor["email"].lower()
            user = User.objects.get_or_create(
                all_emails__email=email,
                defaults=dict(
                    first_name=donor["firstName"],
                    last_name=donor["lastName"],
                    phone=donor["phone"],
                    email=email,
                ),
            )[0]

            UserAddress.objects.get_or_create(
                user=user,
                defaults=dict(
                    street=donor["address"]["street"],
                    city=donor["address"]["city"],
                    zip_code=donor["address"]["postCode"],
                ),
            )

            donor = Donor.objects.get_or_create(user=user)[0]

            basic_section_support = custom.get("Brontosaurus_adopce_ZC")
            if basic_section_support:
                if basic_section_support == "Draci":
                    basic_section_support = "Brďo Draci"
                if basic_section_support == "BRĎO Gingo":
                    basic_section_support = "1.BRĎO Tišnov GINGO"

                basic_section_support = AdministrationUnit.objects.get(
                    abbreviation=basic_section_support
                )

            regional_center_support = custom.get(
                "Brontosaurus_adopce_RC"
            ) and AdministrationUnit.objects.get(
                abbreviation=custom["Brontosaurus_adopce_RC"]
            )
            date_joined = isoparse(pledge["pledgedAt"])
            has_recurrent_donation = pledge["isRecurrent"]

            donor.date_joined = min(donor.date_joined, date_joined.date())
            donor.basic_section_support = (
                donor.basic_section_support or basic_section_support
            )
            donor.regional_center_support = (
                donor.regional_center_support or regional_center_support
            )
            donor.has_recurrent_donation = (
                has_recurrent_donation or donor.has_recurrent_donation
            )
            donor.save()

            for transaction in transactions:
                Donation.objects.get_or_create(
                    _import_id=transaction["transactionId"],
                    defaults=dict(
                        donor=donor,
                        donated_at=isoparse(transaction["receivedAt"]),
                        amount=transaction["sentAmount"]["cents"] / 100,
                        donation_source=donation_source,
                        info=f'přeposlaná částka: {transaction["outgoingAmount"]["cents"] / 100}',
                    ),
                )
