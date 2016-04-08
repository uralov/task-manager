from django.dispatch import receiver
from django.db.models.signals import post_save

from task_management.models import Task, TaskAssignedUser


@receiver(post_save, sender=Task)
def create_task_owner_chain(sender, instance, **kwargs):
    if instance.owner:
        owner_chain_last_el = TaskAssignedUser.objects.filter(task=instance)\
            .order_by('time_assign').last()

        if not owner_chain_last_el:
            TaskAssignedUser.objects.create(user=instance.owner, task=instance)

        if owner_chain_last_el and owner_chain_last_el.user != instance.owner:
            TaskAssignedUser.objects.create(user=instance.owner, task=instance,
                                            parent=owner_chain_last_el)
