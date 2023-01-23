import typing as t

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.core.management.base import BaseCommand
from django.utils.datetime_safe import date

from administration_units.models import (
    AdministrationUnit,
    AdministrationUnitAddress,
    BrontosaurusMovement,
)
from bis.models import User, Qualification, Location, Membership
from categories.models import (
    MembershipCategory,
    EventCategory,
    EventProgramCategory,
    QualificationCategory,
    AdministrationUnitCategory,
    EventIntendedForCategory,
    EventGroupCategory,
)
from event.models import Event


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        self._email_number = 0

        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        call_command("flush", no_input=False)
        call_command("create_init_data")
        call_command("import_regions")
        call_command("import_zip_codes")
        self.create_testing_db()
        call_command("import_locations")

    def create_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        birthday: date = None,
        qualification: t.Tuple[str, date, User] = None,
    ):
        """
        :param qualification: Triplet of (slug, valid_since, approved_by)
        """
        if birthday is None:
            birthday = date(1980, 1, 1)
        new_user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            birthday=birthday,
        )

        if qualification:
            (
                qualification_slug,
                qualification_valid_since_date,
                qualification_approved_by,
            ) = qualification
            ctg_qualification = QualificationCategory.objects.get(
                slug=qualification_slug
            )
            Qualification.objects.update_or_create(
                defaults=dict(
                    user=new_user,
                    category=ctg_qualification,
                    valid_since=qualification_valid_since_date,
                    approved_by=qualification_approved_by,
                )
            )
        return new_user

    def create_brontosaurus(self):
        # Brontosaurus movement structure, one person for each role.
        director = self.create_user("Pan", "Reditel", "mountdoom@centrum.cz")
        finance_director = self.create_user(
            "Andrej", "Babis", "prezident@prezident.gov.cz"
        )
        admin = self.create_user("Ich Bin", "Admin", self._next_email())
        kancl = self.create_user("Ich Bin", "Kancl", self._next_email())
        krk = self.create_user("Ich Bin", "KRK", self._next_email())
        vv = self.create_user("Ich Bin", "VV", self._next_email())
        edu = self.create_user("Ich Bin", "EDU", self._next_email())

        brontosaurus = BrontosaurusMovement.objects.create(
            director=director,
            finance_director=finance_director,
        )
        brontosaurus.bis_administrators.add(admin)
        brontosaurus.office_workers.add(kancl)
        brontosaurus.audit_committee.add(krk)
        brontosaurus.executive_committee.add(vv)
        brontosaurus.education_members.add(edu)

    def create_administration_unit(
        self,
        name: str,
        abbreviation: str,
        existed_since: date,
        chairman: User,
        slug_category: str = "basic_section",
        manager: User = None,
        address: t.Tuple[str, str, str] = None,
    ):
        """Create new administration unit.

        :param address: Address is a triplet of (street, city, zip_code)
        """
        category = AdministrationUnitCategory.objects.get(slug=slug_category)
        au = AdministrationUnit.objects.create(
            name=name,
            abbreviation=abbreviation,
            existed_since=existed_since,
            chairman=chairman,
            category=category,
            manager=manager,
            is_for_kids=True,
            phone=self._random_phonenum(),
            email=self._next_email(),
        )

        if address:
            street, city, zip_code = address
            AdministrationUnitAddress.objects.update_or_create(
                administration_unit=au,
                defaults=dict(
                    street=street,
                    city=city,
                    zip_code=zip_code,
                ),
            )
        return au

    def add_user_to_administration_unit(
        self,
        administration_unit: AdministrationUnit,
        user: User,
        membership: t.Tuple[str, int],
    ):
        """Add user to administration unit and assign qualification.

        :param membership: Pair of (slug, member_since_year)
        """
        membership_slug, membership_from_year = membership

        ctg_membership = MembershipCategory.objects.get(slug=membership_slug)

        Membership.objects.update_or_create(
            defaults=dict(
                user=user,
                category=ctg_membership,
                administration_unit=administration_unit,
                year=membership_from_year,
            )
        )

    def create_event(
        self,
        name: str,
        start: date,
        end: date,
        administration_units: t.Union[AdministrationUnit, t.List[AdministrationUnit]],
        main_organizer: User,
        group_slug: str = "weekend_event",
        category_slug: str = "public__volunteering",
        program_slug: str = "nature",
        intended_for_slug: str = "for_all",
        other_organizers: t.List[User] = None,
        location_name: str = "Online",
        is_canceled: bool = False,
        is_complete: bool = None,
        is_closed: bool = None,
    ):
        ctg_group = EventGroupCategory.objects.get(slug=group_slug)
        ctg_category = EventCategory.objects.get(slug=category_slug)
        ctg_program = EventProgramCategory.objects.get(slug=program_slug)
        ctg_intended_for = EventIntendedForCategory.objects.get(slug=intended_for_slug)
        location = Location.objects.get(name=location_name)

        if is_complete is None:
            is_complete = start.year <= 2022
        if is_closed is None:
            is_closed = start.year <= 2022

        event = Event.objects.create(
            name=name,
            start=start,
            end=end,
            is_canceled=is_canceled,
            is_complete=is_complete,
            is_closed=is_closed,
            location=location,
            group=ctg_group,
            category=ctg_category,
            program=ctg_program,
            intended_for=ctg_intended_for,
            main_organizer=main_organizer,
        )

        if other_organizers:
            event.other_organizers.set(other_organizers)

        if not isinstance(administration_units, (list, tuple)):
            administration_units = [administration_units]

        for adm_unit in administration_units:
            event.administration_units.add(adm_unit)
        return event

    def create_testing_db(self):
        # Brontosaurus movement
        self.create_brontosaurus()
        # Virtual basic section
        zc_chairman = self.create_user("Predseda", "ZC", self._next_email())
        zc_manager = self.create_user("Hospodar", "ZC", self._next_email())
        basic_section = self.create_administration_unit(
            name="Zakladni clanek",
            abbreviation="ZC",
            existed_since=date(2000, 1, 1),
            address=("Pricna ulice", "Kvikalkov", "666 66"),
            chairman=zc_chairman,
            manager=zc_manager,
        )

        # Add organizer to virtual basic section
        user = self.create_user(
            "User",
            "Name",
            self._next_email(),
            qualification=("organizer", date(2020, 1, 1), zc_chairman),
        )
        self.add_user_to_administration_unit(
            basic_section,
            user,
            membership=("adult", 2000),
        )
        # Create event for basic section
        self.create_event(
            "Udalost", date(2020, 1, 1), date(2020, 12, 12), basic_section, user
        )

    def _next_email(self):
        """Generator of email address."""
        self._email_number += 1
        return f"original_email{self._email_number}@email.com"

    def _random_phonenum(self):
        return "666 666 666"
