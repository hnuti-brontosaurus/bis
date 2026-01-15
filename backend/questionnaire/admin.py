from nested_admin.forms import SortableHiddenMixin
from nested_admin.nested import NestedStackedInline, NestedTabularInline
from questionnaire.models import *

from bis.admin_permissions import PermissionMixin, ReadonlyMixin


class QuestionAdmin(ReadonlyMixin, NestedTabularInline):
    model = Question


class AnswerAdmin(ReadonlyMixin, NestedTabularInline):
    model = Answer


class EventApplicationClosePersonAdmin(ReadonlyMixin, NestedStackedInline):
    model = EventApplicationClosePerson


class EventApplicationAddressAdmin(ReadonlyMixin, NestedStackedInline):
    model = EventApplicationAddress


class EventApplicationAdmin(ReadonlyMixin, NestedStackedInline):
    model = EventApplication
    inlines = (
        EventApplicationClosePersonAdmin,
        EventApplicationAddressAdmin,
        AnswerAdmin,
    )

    classes = ("collapse",)


class QuestionnaireAdmin(ReadonlyMixin, NestedStackedInline):
    model = Questionnaire
    inlines = (QuestionAdmin,)

    classes = ("collapse",)
    readonly_fields = "introduction", "after_submit_text"
