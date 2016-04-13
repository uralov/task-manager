from functools import reduce
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

from task_management.models import Task, TaskAssignedUser


@receiver(post_save, sender=Task)
def add_user_to_assign_chain(sender, instance, **kwargs):
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
        task.status = Task.STATUS_DECLINE

    task.save()


@receiver(pre_save, sender=Task)
def recalculate_parent_task_status(sender, instance, **kwargs):
    """ Signal recalculate status for parent task.

    It will cause recursion for all parents.
    """
    if instance.parent:
        if instance.id:
            task = Task.objects.get(id=instance.id)
            if task.status != instance.status:
                # task status changes
                recalculate_status(instance.parent, instance)
        else:
            recalculate_status(instance.parent, instance)


def recalculate_status(parent_task, current_task):
    """ Calculate parent task status by average child task status. """
    children = parent_task.get_children()
    children_status = [i.status for i in children if i.id != current_task.id]
    children_status.append(current_task.status)
    status_sum = reduce(lambda x, y: x + y, children_status)
    status_avg = int(status_sum/len(children_status))
    parent_task.status = status_avg
    parent_task.save()
