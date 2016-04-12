from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden

from task_management.models import TaskAssignedUser, Task


class TaskChangePermitMixin(LoginRequiredMixin):
    """ Mixin which verifies that the current user can edit task. """

    def dispatch(self, request, *args, **kwargs):
        # only creator and owner accepted task can update task
        task = self.get_object()
        user = request.user
        if user == task.creator or user in task.get_owners_chain(True):
            return super(TaskChangePermitMixin, self).dispatch(
                request, *args, **kwargs
            )

        return HttpResponseForbidden()


class TaskViewPermitMixin(LoginRequiredMixin):
    """ Mixin which verifies that the current user can view task. """

    def dispatch(self, request, *args, **kwargs):
        # only creator and contributors can view task
        task = self.get_object()
        if request.user == task.creator or request.user in task.owners.all():
            return super(TaskViewPermitMixin, self).dispatch(
                request, *args, **kwargs
            )

        return HttpResponseForbidden()


class TaskDeletePermitMixin(LoginRequiredMixin):
    """ Mixin which verifies that the current user can delete task. """

    def dispatch(self, request, *args, **kwargs):
        # only task creator can delete task
        task = self.get_object()
        if request.user == task.creator:
            return super(TaskDeletePermitMixin, self).dispatch(
                request, *args, **kwargs
            )

        return HttpResponseForbidden()


class TaskAcceptPermitMixin(LoginRequiredMixin):
    """ Mixin which verifies that the current user can accept/reject task. """
    task = None

    def get_task(self):
        if not self.task:
            self.task = Task.objects.get(pk=self.kwargs['task_pk'])

        return self.task

    def dispatch(self, request, *args, **kwargs):
        # only task owner can accept/reject task
        task = self.get_task()
        if request.user == task.owner and task.owner_accept_task() is None:
            return super(TaskAcceptPermitMixin, self).dispatch(
                request, *args, **kwargs
            )

        return HttpResponseForbidden()


class TaskApprovePermitMixin(LoginRequiredMixin):
    """ Mixin which verifies that the current user can approve/decline task.
    """

    def dispatch(self, request, *args, **kwargs):
        # only task owner can approve/decline task if status = 'complete'
        task = self.get_object()
        if request.user == task.creator and task.status == task.STATUS_COMPLETE:
            return super(TaskApprovePermitMixin, self).dispatch(
                request, *args, **kwargs
            )

        return HttpResponseForbidden()
