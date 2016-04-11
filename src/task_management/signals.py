from django.dispatch import receiver
from django.db.models.signals import post_save

from task_management.models import Task, TaskAssignedUser


@receiver(post_save, sender=Task)
def create_task_assign_chain(sender, instance, **kwargs):
    """ Add user to task owner chain if owner changes """
    if instance.owner:
        owner_chain_last_el = TaskAssignedUser.objects.filter(task=instance)\
            .order_by('time_assign').last()

        if not owner_chain_last_el:
            TaskAssignedUser.objects.create(user=instance.owner, task=instance)

        if owner_chain_last_el and owner_chain_last_el.user != instance.owner:
            TaskAssignedUser.objects.create(user=instance.owner, task=instance,
                                            parent=owner_chain_last_el)


@receiver(post_save, sender=TaskAssignedUser)
def change_assign_status(sender, instance, **kwargs):
    """ Change task status if user accept or reject assign """
    task = Task.objects.get(pk=instance.task.pk)

    if instance.assign_accept is None:
        task.status = Task.STATUS_PENDING

    if instance.assign_accept is True:
        task.status = Task.STATUS_WORKING

    if instance.assign_accept is False:
        task.status = Task.STATUS_DECLINED

    task.save()
