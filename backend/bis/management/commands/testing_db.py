from datetime import timedelta
from os.path import join
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
    PronounCategory,
)
from event.models import Event, EventPropagation,EventPropagationImage,  EventRecord

from project.settings import BASE_DIR


class Command(BaseCommand):

    # Some events require propagation images.
    # TODO: Generate simple image for testing during runtime.
    event_propagation_image_path = join(BASE_DIR, 'bis', 'static', 'favicon.png')

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
        sex_slug: str = None,
        birthday: date = None,
        password="password",
        qualification: t.Tuple[str, date, User] = None,
    ):
        """Create users, optionally with qualification.

        :param qualification: Triplet of (slug, valid_since_date, approved_by_user)
        """
        if birthday is None:
            birthday = date(1980, 1, 1)
        if sex_slug:
            ctg_sex = PronounCategory.objects.get(slug=sex_slug)
        else:
            ctg_sex = None
        new_user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            birthday=birthday,
            pronoun=ctg_sex,
        )
        if password:
            new_user.set_password(password)
            new_user.save()

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
        director = self.create_user("Pan", "??editel", "director@hb.nope")
        finance_director = self.create_user("Finan??n??", "??editel", "finance_director@hb.nope")
        kancl = self.create_user("Zam??stnanec", "Kancl", "office_worker@hb.nope")
        krk = self.create_user("Zam??stnanec", "KRK", "auditor@hb.nope")
        vv = self.create_user("Zam??stnanec", "VV", "executive@hb.nope")
        edu = self.create_user("Zam??stnanec", "EDU", "education_member@hb.nope")

        admins = [
            self.create_user("Syst??mov??", "Administr??tor", "admin@hb.nope"),
        ]

        brontosaurus = BrontosaurusMovement.objects.create(
            director=director,
            finance_director=finance_director,
        )

        brontosaurus.office_workers.add(kancl)
        brontosaurus.audit_committee.add(krk)
        brontosaurus.executive_committee.add(vv)
        brontosaurus.education_members.add(edu)
        brontosaurus.bis_administrators.set(admins)

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

        event.administration_units.set(administration_units)

        # Create eventrecord so we can add particants
        EventRecord.objects.create(
            event=event,
            total_hours_worked=8,
            comment_on_work_done="",
        )

        if participants:
            event.record.participants.set(participants)

        # Event propagation
        main_organizer_full_name = f'{main_organizer.first_name} {main_organizer.last_name}'
        event_propagation = EventPropagation.objects.create(event=event,
                is_shown_on_web=False,
                working_hours=8,
                cost='100',
                accommodation='',
                organizers=main_organizer_full_name,
                web_url='',
                _contact_url='',
                invitation_text_introduction='Co n??s ??ek???',
                invitation_text_practical_information='Co, kde a jak',
                invitation_text_work_description='Dobrovolnick?? pomoc',
                invitation_text_about_us='Mal?? ochutn??vka',
                contact_name=main_organizer_full_name,
                contact_phone=self._random_phonenum(),
                contact_email=main_organizer.email,
            )

        EventPropagationImage.objects.create(
            propagation=event_propagation,
            image=self.event_propagation_image_path,
            order=0
        )

        return event

    def create_testing_db(self):
        # Brontosaurus movement
        self.create_brontosaurus()
        # Virtual basic section
        zc_chairman = self.create_user("P??edseda", "ZC", "chairman@hb.nope")
        zc_manager = self.create_user("Hospod????", "ZC", "manager@hb.nope")
        basic_section = self.create_administration_unit(
            name="Z??kladn?? ??l??nek",
            abbreviation="DEMO",
            existed_since=date(2000, 1, 1),
            address=("P??????n?? ulice", "Kvik??lkov", "666 66"),
            chairman=zc_chairman,
            manager=zc_manager,
        )

        # Adults
        adult_members = [
            self.create_user("Jan", "Nov??k", self._next_email(), sex_slug="man"),
            self.create_user("Al??b??ta", "Dvo????kov??", self._next_email(), sex_slug="woman"),
            self.create_user("Jan", "Svoboda", self._next_email(), sex_slug="man"),
            self.create_user("Simona", "Pag????ov??", self._next_email(), sex_slug="woman"),
            self.create_user("Jan", "Bodl????ek", self._next_email(), sex_slug="man"),
            self.create_user("Krist??na", "Dvo????kov??", self._next_email(), sex_slug="woman"),
            self.create_user("Jan", "Hn??d??", self._next_email(), sex_slug="man"),
            self.create_user("Kate??ina", "Dvo????kov??", self._next_email(), sex_slug="woman"),
            self.create_user("P??emysl", "Bodl????ek", self._next_email(), sex_slug="man"),
            self.create_user("Tom????", "Nov??k", self._next_email(), sex_slug="man"),
            self.create_user("Simona", "Vy??kovsk??", self._next_email(), sex_slug="woman"),
            self.create_user("Tom????", "Svoboda", self._next_email(), sex_slug="man"),
            self.create_user("Tom????", "Bodl????ek", self._next_email(), sex_slug="man"),
            self.create_user("Tom????", "Hn??d??", self._next_email(), sex_slug="man"),
            self.create_user("Martin", "Nov??k", self._next_email(), sex_slug="man"),
            self.create_user("Al??b??ta", "Srokov??", self._next_email(), sex_slug="woman"),
            self.create_user("Kate??ina", "Srokov??", self._next_email(), sex_slug="woman"),
            self.create_user("Kate??ina", "Pag????ov??", self._next_email(), sex_slug="woman"),
            self.create_user("Simona", "Dvo????kov??", self._next_email(), sex_slug="woman"),
            self.create_user("Martin", "Svoboda", self._next_email(), sex_slug="man"),
            self.create_user("Martin", "Bodl????ek", self._next_email(), sex_slug="man"),
            self.create_user("Martin", "Hn??d??", self._next_email(), sex_slug="man"),
            self.create_user("Krist??na", "Pag????ov??", self._next_email(), sex_slug="woman"),
            self.create_user("Veronika", "Dvo????kov??", self._next_email(), sex_slug="woman"),
            self.create_user("Michal", "Nov??k", self._next_email(), sex_slug="man"),
            self.create_user("Michal", "Svoboda", self._next_email(), sex_slug="man"),
            self.create_user("Michal", "Bodl????ek", self._next_email(), sex_slug="man"),
            self.create_user("Krist??na", "Srokov??", self._next_email(), sex_slug="woman"),
            self.create_user("Veronika", "Vy??kovsk??", self._next_email(), sex_slug="woman"),
            self.create_user("Veronika", "Srokov??", self._next_email(), sex_slug="woman"),
            self.create_user("Michal", "Hn??d??", self._next_email(), sex_slug="man"),
            self.create_user("Krist??na", "Svoboda", self._next_email(), sex_slug="woman"),
            self.create_user("Kate??ina", "Vy??kovsk??", self._next_email(), sex_slug="woman"),
            self.create_user("P??emysl", "Nov??k", self._next_email(), sex_slug="man"),
            self.create_user("P??emysl", "Svoboda", self._next_email(), sex_slug="man"),
            self.create_user("Veronika", "Pag????ov??", self._next_email(), sex_slug="woman"),
            self.create_user("Al??b??ta", "Vy??kovsk??", self._next_email(), sex_slug="woman"),
            self.create_user("Al??b??ta", "Pag????ov??", self._next_email(), sex_slug="woman"),
            self.create_user("P??emysl", "Hn??d??", self._next_email(), sex_slug="man"),
            self.create_user("Simona", "Srokov??", self._next_email(), sex_slug="woman"),
        ]
        # Students
        student_members = [
            self.create_user("Tom????", "Vojtek", self._next_email(), sex_slug="man", birthday=date(1998, 5, 1)),
            self.create_user("Dalimil", "Ku??n??", self._next_email(), sex_slug="man", birthday=date(1998, 11, 15)),
            self.create_user("Milan", "Benna", self._next_email(), sex_slug="man", birthday=date(1999, 5, 12)),
            self.create_user("Oliver", "Stan??k", self._next_email(), sex_slug="man", birthday=date(2000, 2, 11)),
            self.create_user("Tom????", "Kolouch", self._next_email(), sex_slug="man", birthday=date(2000, 4, 12)),
            self.create_user("V??ra", "Balcov??", self._next_email(), sex_slug="woman", birthday=date(2001, 4, 25)),
            self.create_user("Radka", "Leov??", self._next_email(), sex_slug="woman", birthday=date(2001, 6, 29)),
            self.create_user("Hana", "M????ov??", self._next_email(), sex_slug="woman", birthday=date(2002, 8, 1)),
            self.create_user("Alice", "Je????kov??", self._next_email(), sex_slug="woman", birthday=date(2003, 2, 8)),
            self.create_user("Monika", "Vesel??", self._next_email(), sex_slug="woman", birthday=date(1997, 1, 13)),
            self.create_user("Tom????", "Paprota", self._next_email(), sex_slug="man", birthday=date(1999, 4, 12)),
            self.create_user("Pavel", "Va??ko", self._next_email(), sex_slug="man", birthday=date(1999, 4, 25)),
            self.create_user("Dalibor", "Hanzl??k", self._next_email(), sex_slug="man", birthday=date(2000, 8, 6)),
            self.create_user("Hana", "Paprotov??", self._next_email(), sex_slug="woman", birthday=date(2004, 12, 17)),
            self.create_user("Erik", "Va??ko", self._next_email(), sex_slug="man", birthday=date(2003, 2, 8)),
            self.create_user("Monika", "Chaloupkov??", self._next_email(), sex_slug="woman", birthday=date(2004, 5, 18)),
            self.create_user("Daniela", "Luk????ov??", self._next_email(), sex_slug="woman", birthday=date(2000, 5, 1)),
            self.create_user("V??ra", "Balcov??", self._next_email(), sex_slug="woman", birthday=date(2001, 1, 2)),
            self.create_user("Radka", "Leov??", self._next_email(), sex_slug="woman", birthday=date(2000, 3, 8)),
            self.create_user("Hana", "Hanzl??k", self._next_email(), sex_slug="woman", birthday=date(1999, 8, 7)),
            self.create_user("Daniela", "Je????kov??", self._next_email(), sex_slug="woman", birthday=date(1998, 2, 26)),
            self.create_user("Monika", "Va??ko", self._next_email(), sex_slug="woman", birthday=date(2004, 1, 13)),
        ]
        # Oganizers with qualification
        organizers = [
            self.create_user("Oganiz??tor", "Honza", self._next_email(), sex_slug="man", qualification=("weekend_organizer", date(2018, 1, 1), zc_chairman)),
            self.create_user("Oganiz??tor", "Filip", self._next_email(), sex_slug="man", qualification=("weekend_organizer", date(2018, 1, 1), zc_chairman)),
            self.create_user("Oganiz??tor", "Pepa", self._next_email(), sex_slug="man", qualification=("weekend_organizer", date(2018, 1, 1), zc_chairman)),
            self.create_user("Oganiz??tor", "Jarda", self._next_email(), sex_slug="man", qualification=("weekend_organizer", date(2018, 1, 1), zc_chairman)),
            self.create_user("Oganiz??tor", "Ondra", self._next_email(), sex_slug="man", qualification=("weekend_organizer", date(2018, 1, 1), zc_chairman)),
            self.create_user("Oganiz??torka", "Mon??a", self._next_email(), sex_slug="woman", qualification=("weekend_organizer", date(2018, 1, 1), zc_chairman)),
            self.create_user("Oganiz??torka", "Jan??a", self._next_email(), sex_slug="woman", qualification=("weekend_organizer", date(2018, 1, 1), zc_chairman)),
            self.create_user("Oganiz??torka", "B??ra", self._next_email(), sex_slug="woman", qualification=("weekend_organizer", date(2018, 1, 1), zc_chairman)),
            self.create_user("Oganiz??torka", "Natka", self._next_email(), sex_slug="woman", qualification=("weekend_organizer", date(2018, 1, 1), zc_chairman)),
            self.create_user("Oganiz??torka", "Nik??a", self._next_email(), sex_slug="woman", qualification=("weekend_organizer", date(2018, 1, 1), zc_chairman)),
        ]

        for member in adult_members:
            self.add_administration_unit_member(basic_section, member, membership=("adult", 2010))
        for member in student_members:
            self.add_administration_unit_member(basic_section, member, membership=("student", 2015))
        for member in organizers:
            self.add_administration_unit_member(basic_section, member, membership=("adult", 2018))

        all_members = adult_members + student_members + organizers

        # Generate events in this timerange
        event_starting_date = date(2019, 1, 1)
        event_ending_date = date(2023, 2, 1)
        time_delta = timedelta(weeks=10)
        category_slugs = ["public__volunteering", "public__only_experiential", "public__club__lecture", "public__other__for_public"]

        current_event_time = event_starting_date
        event_number = 1
        # Generation parameters have been chosen, so that
        # event parameters (such as number of participants,
        # categories and organizers) simulate real events.
        while current_event_time < event_ending_date:
            category_slug = category_slugs[event_number % len(category_slugs)]
            main_organizer = organizers[event_number % len(organizers)]
            event_name = f"Ud??lost od {main_organizer.last_name} ({event_number})"
            # Max 3 other organizers
            other_organizers = organizers[event_number % 3 : event_number % 3 + (event_number % 4)] + [main_organizer]
            participants = all_members[event_number % 8 :: event_number % 4 + 2]
            self.create_event(
                event_name,
                current_event_time,
                current_event_time + time_delta,
                basic_section,
                main_organizer,
                other_organizers=other_organizers,
                participants=participants,
                category_slug=category_slug,
            )

            current_event_time += time_delta
            event_number += 1

    def _next_email(self):
        """Generator of unique email address."""
        self._email_number += 1
        return f"original_email{self._email_number}@email.com"

    def _random_phonenum(self):
        return "777 777 777"
