from django.dispatch import receiver
from django.db.models.signals import post_save

from task_management.models import Task, TaskAssignedUser


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
