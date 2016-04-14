from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView, View
)
from notifications.signals import notify

from task_management.forms import TaskForm, CommentForm, RejectTaskForm, \
    DeclineTaskForm, ReassignTaskForm
from task_management.models import Task, TaskComment, TaskAssignedUser
from task_management.mixins import (
    TaskChangePermitMixin, TaskViewPermitMixin, TaskDeletePermitMixin,
    TaskAcceptPermitMixin, TaskApprovePermitMixin, TaskReassignPermitMixin)


class TaskListView(LoginRequiredMixin, ListView):
    """ View to display the list of tasks """
    model = Task
    context_object_name = 'tasks_assigned'

    def get_queryset(self):
        queryset = super(TaskListView, self).get_queryset()
        return queryset.filter(owners=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)
        context['task_created'] = Task.objects.filter(
            creator=self.request.user
        )
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm

    def form_valid(self, form):
        user = self.request.user
        notify.send(user, recipient=user, verb='create task', )

        form.instance.creator = self.request.user
        return super(TaskCreateView, self).form_valid(form)


class SubTaskCreateView(TaskChangePermitMixin, TaskCreateView):
    def form_valid(self, form):
        parent_task = Task.objects.get(pk=self.kwargs['pk'])
        form.instance.parent = parent_task

        return super(SubTaskCreateView, self).form_valid(form)


class TaskUpdateView(TaskChangePermitMixin, UpdateView):
    model = Task
    form_class = TaskForm

    def form_valid(self, form):
        task = self.object
        user = self.request.user
        if task.status == Task.STATUS_DECLINE and user == task.creator:
            if form.cleaned_data['assigned_to']:
                TaskAssignedUser.objects.filter(task=task).delete()

        return super(TaskUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(TaskUpdateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})

        return kwargs


class TaskDetailView(TaskViewPermitMixin, DetailView):
    model = Task

    def get_context_data(self, **kwargs):
        kwargs['comment_form'] = CommentForm()
        kwargs['comments'] = TaskComment.objects.filter(task=self.object)\
            .prefetch_related('author')
        kwargs['task_assigned_to'] = TaskAssignedUser.objects.filter(
            task=self.object
        )
        return super(TaskDetailView, self).get_context_data(**kwargs)


class TaskDeleteView(TaskDeletePermitMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('task_management:list')


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = TaskComment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.task = Task.objects.get(pk=self.kwargs['pk'])
        form.instance.author = self.request.user

        return super(CommentCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('task_management:detail',
                       kwargs={'pk': self.kwargs['pk']})


class AcceptTaskView(TaskAcceptPermitMixin, View):
    def get(self, *args, **kwargs):
        task = self.get_task()
        assign = TaskAssignedUser.objects.get(task=task,
                                              user=self.request.user)
        assign.assign_accept = True
        assign.save()

        return redirect(task)


class RejectTaskView(TaskAcceptPermitMixin, UpdateView):
    model = TaskAssignedUser
    form_class = RejectTaskForm
    template_name = 'task_management/task_reject_form.html'

    def get_object(self, queryset=None):
        return self.model.objects.get(task=self.get_task(),
                                      user=self.request.user)

    def get_success_url(self):
        return reverse('task_management:detail',
                       kwargs={'pk': self.kwargs['pk']})


class ApproveTaskView(TaskApprovePermitMixin, View):
    object = None

    def get_object(self):
        if not self.object:
            self.object = Task.objects.get(pk=self.kwargs['pk'])

        return self.object

    def get(self, *args, **kwargs):
        task = self.get_object()
        task.status = Task.STATUS_APPROVE
        task.save()

        return redirect(task)


class DeclineTaskView(TaskApprovePermitMixin, UpdateView):
    model = Task
    form_class = DeclineTaskForm
    template_name = 'task_management/task_decline_form.html'


class ReassignTaskView(TaskReassignPermitMixin, UpdateView):
    model = Task
    form_class = ReassignTaskForm
    template_name = 'task_management/task_reassign_form.html'
