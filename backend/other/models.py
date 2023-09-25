from datetime import timedelta

from dateutil.utils import today
from django.contrib.gis.db.models import *

from bis.helpers import permission_cache
from bis.models import User
from categories.models import RoleCategory
from translation.translate import translate_model


@translate_model
class DuplicateUser(Model):
    user = ForeignKey(User, on_delete=CASCADE, related_name='duplicates')
    other = ForeignKey(User, on_delete=CASCADE, related_name='other_duplicates')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.user == self.other:
            if not self._state.adding:
                self.delete()

            return

        super().save(force_insert, force_update, using, update_fields)

    @classmethod
    def filter_queryset(cls, queryset, perm):
        visible_users = User.filter_queryset(User.objects.all(), perm)
        return queryset.filter(user__in=visible_users, other__in=visible_users)

    def can_be_merged_by(self, user):
        if user.is_superuser: return True
        if user.is_office_worker:
            return not (self.user.is_superuser or self.other.is_superuser)
        return False

    def __str__(self):
        return 'Duplicita'

    class Meta:
        ordering = 'id',
        unique_together = 'user', 'other'


@translate_model
class Feedback(Model):
    user = ForeignKey(User, on_delete=CASCADE, related_name='feedbacks')
    feedback = TextField()
    created_at = DateTimeField(auto_now=True)
    is_resolved = BooleanField(default=False)

    @classmethod
    def filter_queryset(cls, queryset, perm):
        return queryset.filter(user=perm.user)

    def __str__(self):
        return 'Zpětná vazba'

    class Meta:
        ordering = 'id',

    @permission_cache
    def has_edit_permission(self, user):
        return user.is_superuser or user.is_office_worker


@translate_model
class DashboardItem(Model):
    date = DateField()
    name = CharField(max_length=63)
    description = TextField(blank=True)
    repeats_every_year = BooleanField(default=False)

    for_roles = ManyToManyField(RoleCategory, related_name='dashboard_items')

    def __str__(self):
        return self.name

    class Meta:
        ordering = '-date',

    @classmethod
    def get_items_for_user(cls, user):
        dashboard_items = list(
            DashboardItem.objects.filter(for_roles__in=user.roles.all(), date__gte=today().date()).distinct()
        )

        for application in user.applications.filter(
                event_registration__event__start__gte=today(),
                event_registration__event__is_canceled=False):
            event = application.event_registration.event
            dashboard_items.append(
                DashboardItem(
                    date=event.start,
                    name=f'Začíná ti akce {event.name}'
                )
            )

        for event in user.events_where_was_organizer.filter(start__gte=today(), is_canceled=False):
            dashboard_items.append(
                DashboardItem(
                    date=event.start,
                    name=f'Organizuješ akci {event.name}'
                )
            )

        for event in (user.events_where_was_organizer
                .exclude(is_closed=True)
                .exclude(is_canceled=True)
                .filter(is_complete=False)):
            dashboard_items.append(
                DashboardItem(
                    date=event.start + timedelta(days=20),
                    name=f'Deadline pro uzavření akce {event.name}'
                )
            )

        dashboard_items.sort(key=lambda obj: obj.date)

        return dashboard_items
