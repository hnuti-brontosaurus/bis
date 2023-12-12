from bis.admin_permissions import PermissionMixin
from nested_admin.forms import SortableHiddenMixin
from nested_admin.nested import NestedStackedInline, NestedTabularInline
from questionnaire.models import *


class QuestionAdmin(PermissionMixin, SortableHiddenMixin, NestedTabularInline):
    model = Question
    sortable_field_name = "order"
    extra = 0


class AnswerAdmin(PermissionMixin, NestedTabularInline):
    model = Answer
    extra = 0

    readonly_fields = "question", "answer"


class EventApplicationClosePersonAdmin(PermissionMixin, NestedStackedInline):
    model = EventApplicationClosePerson


class EventApplicationAddressAdmin(PermissionMixin, NestedStackedInline):
    model = EventApplicationAddress


class EventApplicationAdmin(PermissionMixin, NestedStackedInline):
    model = EventApplication
    inlines = (
        EventApplicationClosePersonAdmin,
        EventApplicationAddressAdmin,
        AnswerAdmin,
    )
    extra = 0
    classes = ("collapse",)

    autocomplete_fields = ("user",)


class QuestionnaireAdmin(PermissionMixin, NestedStackedInline):
    model = Questionnaire
    inlines = (QuestionAdmin,)

    classes = ("collapse",)
