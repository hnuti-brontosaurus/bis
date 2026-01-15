from feedback.models import EventFeedback, FeedbackForm, Inquiry, Reply
from nested_admin.nested import NestedStackedInline, NestedTabularInline

from bis.admin_permissions import ReadonlyMixin


class InquiryAdmin(ReadonlyMixin, NestedTabularInline):
    model = Inquiry


class ReplyAdmin(ReadonlyMixin, NestedTabularInline):
    model = Reply


class EventFeedbackAdmin(ReadonlyMixin, NestedStackedInline):
    model = EventFeedback
    inlines = (ReplyAdmin,)
    classes = ("collapse",)


class FeedbackFormAdmin(ReadonlyMixin, NestedStackedInline):
    model = FeedbackForm
    inlines = (InquiryAdmin,)

    classes = ("collapse",)
    readonly_fields = "introduction", "after_submit_text", "sent_at"
