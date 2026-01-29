from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from administration_units.models import AdministrationUnit, BrontosaurusMovement
from bis.models import User
from event.models import Event


@receiver(post_save, sender=AdministrationUnit, dispatch_uid="set_board_members")
def set_board_members(instance, **kwargs):
    if instance.chairman:
        instance.board_members.add(instance.chairman)
    if instance.vice_chairman:
        instance.board_members.add(instance.vice_chairman)
    if instance.manager:
        instance.board_members.add(instance.manager)


@receiver(
    m2m_changed,
    sender=AdministrationUnit.board_members.through,
    dispatch_uid="update_roles_cache1",
)
@receiver(
    m2m_changed,
    sender=BrontosaurusMovement.bis_administrators.through,
    dispatch_uid="update_roles_cache2",
)
@receiver(
    m2m_changed,
    sender=BrontosaurusMovement.office_workers.through,
    dispatch_uid="update_roles_cache3",
)
@receiver(
    m2m_changed,
    sender=BrontosaurusMovement.audit_committee.through,
    dispatch_uid="update_roles_cache4",
)
@receiver(
    m2m_changed,
    sender=BrontosaurusMovement.executive_committee.through,
    dispatch_uid="update_roles_cache5",
)
@receiver(
    m2m_changed,
    sender=BrontosaurusMovement.education_members.through,
    dispatch_uid="update_roles_cache6",
)
@receiver(
    m2m_changed,
    sender=Event.other_organizers.through,
    dispatch_uid="update_roles_cache7",
)
def update_roles_cache(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action.startswith("post"):
        if reverse:
            instance.update_roles()
        else:
            for pk in pk_set:
                User.objects.get(pk=pk).update_roles()
