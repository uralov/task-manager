from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden

from task_management.models import TaskOwnerChain


class TaskChangePermitMixin(LoginRequiredMixin):
    """ Mixin which verifies that the current user can edit task. """
    def dispatch(self, request, *args, **kwargs):
        # only creator and owner accepted task can update task
        task = self.get_object()
        is_owner_and_accept_task = (
            request.user == task.owner and task.owner_accept_task()
        )
        if request.user == task.creator or is_owner_and_accept_task:
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()


class TaskViewPermitMixin(LoginRequiredMixin):
    """ Mixin which verifies that the current user can view task. """

    def dispatch(self, request, *args, **kwargs):
        # only creator and contributors can view task
        task = self.get_object()
        task_owner_chain = TaskOwnerChain.objects.filter(task=task) \
            .prefetch_related('user')
        owners = (obj.user for obj in task_owner_chain)
        if request.user == task.creator or request.user in owners:
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()


class TaskDeletePermitMixin(LoginRequiredMixin):
    """ Mixin which verifies that the current user can delete task. """

    def dispatch(self, request, *args, **kwargs):
        # only task creator can delete task
        task = self.get_object()
        if request.user == task.creator:
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden()
