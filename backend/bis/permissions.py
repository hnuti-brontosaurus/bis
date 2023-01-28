from administration_units.models import BrontosaurusMovement, AdministrationUnit, AdministrationUnitAddress, \
    AdministrationUnitContactAddress, GeneralMeeting
from bis.models import Qualification, User, UserAddress, UserContactAddress, UserEmail, Location, LocationPhoto, \
    Membership, LocationContactPerson, UserClosePerson, LocationPatron, EYCACard
from donations.models import Donation, UploadBankRecords, VariableSymbol, Donor
from event.models import Event, EventDraft
from opportunities.models import OfferedHelp, Opportunity
from other.models import Feedback, DuplicateUser, DashboardItem
from questionnaire.models import Answer, Questionnaire, Question, EventApplication, EventApplicationClosePerson, \
    EventApplicationAddress


class Permissions:
    def __init__(self, user, model, source):
        self.user = user
        self.model = model
        self.source = source

    def raise_error(self, method):
        raise RuntimeError(f'Uncheck {method} permission for user {self.user}, model {self.model}')

    def can_view_all_objs(self):
        return self.user.can_see_all or \
               self.model in [Location, LocationPhoto, LocationContactPerson, LocationPatron,
                              AdministrationUnit, AdministrationUnitAddress, AdministrationUnitContactAddress,
                              GeneralMeeting]

    def is_readonly(self):
        return self.model._meta.app_label in ['categories', 'regions'] or \
               self.model in [Donation, Feedback]

    def filter_queryset(self, queryset):
        if self.can_view_all_objs():
            return queryset

        if self.model in [BrontosaurusMovement] or self.model._meta.app_label in ['categories', 'regions']:
            return queryset

        queryset = self.model.filter_queryset(queryset, self)

        return queryset

    def has_view_permission(self, obj=None):
        # individual objects are filtered using get_queryset,
        # this is used only for disabling whole admin model
        if self.source == 'frontend':
            return True

        if self.model in [BrontosaurusMovement] or self.model._meta.app_label in ['categories', 'regions']:
            return self.user.can_see_all

        if self.model in [UploadBankRecords, DashboardItem] or (not obj and self.model in [DuplicateUser]):
            return self.user.is_superuser or self.user.is_office_worker

        if self.can_view_all_objs() or self.user.is_board_member:
            return True

        if self.user.is_education_member:
            return self.model in [Qualification, User, UserAddress, UserContactAddress, UserClosePerson, Feedback,
                                  DuplicateUser]

        raise RuntimeError("Should never happen")

    def has_add_permission(self, obj=None):
        if self.model is Feedback: return True
        if self.model is BrontosaurusMovement: return False
        if self.is_readonly(): return False

        if self.user.is_superuser:
            return True

        if self.user.is_office_worker:
            if self.model not in [UserEmail]:
                return True

        # for admin
        if self.model is DuplicateUser and not obj: return False

        if self.user.is_education_member:
            if self.model in [User, Qualification, DuplicateUser, Feedback]:
                return True

        # for any user
        if self.model in [UserAddress, UserContactAddress, UserClosePerson, EYCACard, OfferedHelp, EventApplication,
                          EventApplicationClosePerson, EventApplicationAddress, Answer, EventDraft]:
            if not obj or obj.has_edit_permission(self.user):
                return True

        # common for organizers and board members
        if self.user.is_organizer or self.user.is_board_member:
            if self.model in [Location, LocationPhoto, LocationContactPerson, LocationPatron, User, Event, Opportunity,
                              Questionnaire, Question] \
                    or self.model._meta.app_label in ['event']:
                if not obj or obj.has_edit_permission(self.user):
                    return True

        if self.user.is_board_member:
            if self.model in [Donor, DuplicateUser, Membership, AdministrationUnitAddress,
                              AdministrationUnitContactAddress, GeneralMeeting]:
                if not obj or obj.has_edit_permission(self.user):
                    return True

        return False

    def has_change_permission(self, obj=None):
        if self.model in [VariableSymbol]: return False
        if self.is_readonly(): return False
        if self.user.is_superuser: return True

        if self.user.is_office_worker:
            if self.model not in [BrontosaurusMovement, UserEmail]:
                return True

        if self.model is DuplicateUser and not obj: return False

        if self.user.is_education_member:
            if self.model in [User, Qualification, DuplicateUser]:
                return True

        # for any user
        if self.model in [User, UserAddress, UserContactAddress, UserClosePerson, EYCACard, OfferedHelp, Donor, EventDraft]:
            if not obj or obj.has_edit_permission(self.user):
                return True

        # common for organizers and board members
        if self.user.is_organizer or self.user.is_board_member:
            if self.model in [Location, LocationContactPerson, LocationPatron, Event, Opportunity, Questionnaire,
                              Question, EventApplication] \
                    or self.model._meta.app_label in ['event']:
                if not obj or obj.has_edit_permission(self.user):
                    return True

        if self.user.is_board_member:
            if self.model in [DuplicateUser, Membership, AdministrationUnit, AdministrationUnitAddress,
                              AdministrationUnitContactAddress, GeneralMeeting]:
                if not obj or obj.has_edit_permission(self.user):
                    return True

        return False

    def has_delete_permission(self, obj=None):
        if self.model in [BrontosaurusMovement, UploadBankRecords]: return False
        if self.is_readonly(): return False
        if self.user.is_superuser: return True

        if self.user.is_office_worker:
            if self.model not in [UserEmail]:
                return True

        if self.model is DuplicateUser and not obj: return False

        if self.user.is_education_member:
            if self.model in [Qualification, DuplicateUser]:
                return True

        # for any user
        if self.model in [UserContactAddress, UserClosePerson, OfferedHelp, EventDraft]:
            if not obj or obj.has_edit_permission(self.user):
                return True

        # common for organizers and board members
        if self.user.is_organizer or self.user.is_board_member:
            if self.model in [Opportunity, Questionnaire, Question] or self.model._meta.app_label in ['event']:
                if not obj or obj.has_edit_permission(self.user):
                    return True

        if self.user.is_board_member:
            if self.model in [DuplicateUser, Membership, AdministrationUnitContactAddress, GeneralMeeting]:
                if not obj or obj.has_edit_permission(self.user):
                    return True

        return False
