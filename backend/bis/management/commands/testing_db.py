from itertools import product
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
from event.models import Event, EventRecord


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
        # call_command("import_locations")

    def create_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        birthday: date = None,
        password=None,
        qualification: t.Tuple[str, date, User] = None,
    ):
        """Create users, optionally with qualification.

        :param qualification: Triplet of (slug, valid_since_date, approved_by_user)
        """
        if birthday is None:
            birthday = date(1980, 1, 1)
        new_user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            birthday=birthday,
        )
        if password:
            new_user.set_password(password)

        if qualification:
            (
                qualification_slug,
                qualification_valid_since_date,
                qualification_approved_by,
            ) = qualification
            ctg_qualification = QualificationCategory.objects.get(slug=qualification_slug)
            Qualification.objects.create(
                user=new_user,
                category=ctg_qualification,
                valid_since=qualification_valid_since_date,
                approved_by=qualification_approved_by,
            )
        return new_user

    def create_brontosaurus(self):
        # Brontosaurus movement structure, one person for each role.
        director = self.create_user("Pan", "Reditel", "reditel@reditel.nope", password='password')
        finance_director = self.create_user("Ich Bin", "FinanceDirector", self._next_email(), password='password')
        admin = self.create_user("Ich Bin", "Admin", self._next_email(), password='password')
        kancl = self.create_user("Ich Bin", "Kancl", self._next_email(), password='password')
        krk = self.create_user("Ich Bin", "KRK", self._next_email(), password='password')
        vv = self.create_user("Ich Bin", "VV", self._next_email(), password='password')
        edu = self.create_user("Ich Bin", "EDU", self._next_email(), password='password')

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

    def add_administration_unit_member(
        self,
        administration_unit: AdministrationUnit,
        user: User,
        membership: t.Tuple[str, int],
    ):
        """Add user to administration unit as a member.

        :param membership: Pair of (slug, member_since_year).
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
        participants=None,
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

        EventRecord.objects.create(event=event,
                total_hours_worked=8,
                comment_on_work_done='',
            )
        
        if participants:
            event.record.participants.set(participants)
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

        # Regular members who joined in 2010
        members_since_2010 = [
            self.create_user(firstname, surname, self._next_email())
            for firstname, surname in product(
                ("James", "Robert", "John", "Jennifer", "Patricia"),
                ("Smith", "Jones", "Williams", "Brown"),
            )
        ]
        for member in members_since_2010:
            self.add_administration_unit_member(basic_section, member, membership=("adult", 2010))

        # Regular members who joined in 2018
        members_since_2018 = [
            self.create_user(firstname, surname, self._next_email())
            for firstname, surname in product(
                ("Cassandra", "Abbas", "Berger", "Josiah", "Jessie"),
                ("Mahoney", "Maddox", "Williams", "Franco"),
            )
        ]
        for member in members_since_2018:
            self.add_administration_unit_member(basic_section, member, membership=("adult", 2018))

        # Members since year 2015 with organizer qualification since 2018
        organizers_since_2018 = [
            self.create_user(
                firstname,
                surname,
                self._next_email(),
                qualification=("weekend_organizer", date(2018, 1, 1), zc_chairman),
            )
            for firstname, surname in product(
                (
                    "Organizer",
                ),
                ("Davies ", "Evans", "Taylor", "McDonald", "Morty"),
            )
        ]
        for member in organizers_since_2018:
            self.add_administration_unit_member(basic_section, member, membership=("adult", 2015))

        # Event defaults - weekend event, for all, public_volunteering, nature
        self.create_event("Udalost1", date(2018, 6, 8), date(2018, 6, 10), basic_section, organizers_since_2018[0], participants=members_since_2010[0:10])
        self.create_event("Udalost2", date(2018, 7, 13), date(2018, 7, 15), basic_section, organizers_since_2018[1], category_slug='public__only_experiential', participants=members_since_2010[10:15])
        self.create_event("Udalost3", date(2019, 10, 18), date(2019, 10, 20), basic_section, organizers_since_2018[2], category_slug='public__club__lecture', participants=members_since_2010[15:20])
        self.create_event("Udalost4", date(2020, 4, 10), date(2020, 4, 12), basic_section, organizers_since_2018[3], category_slug='public__only_experiential', participants=members_since_2018[0:10])
        self.create_event("Udalost5", date(2020, 5, 22), date(2020, 5, 24), basic_section, organizers_since_2018[4], participants=members_since_2018[10:20])

    def _next_email(self):
        """Generator of unique email address."""
        self._email_number += 1
        return f"original_email{self._email_number}@email.com"

    def _random_phonenum(self):
        return "666 666 666"
