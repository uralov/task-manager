from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView
)

from task_management.forms import TaskFrom
from task_management.models import Task, TaskAssignUser


class TaskListView(LoginRequiredMixin, ListView):
    """ View to display the list of tasks """
    model = Task
    context_object_name = 'tasks_assigned'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(assigned_to=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_created'] = Task.objects.filter(author=self.request.user)

        return context


class TaskStatusMixin(object):
    """ Common status logic mixin """
    def form_valid(self, form):
        if form.cleaned_data['assigned_to']:
            form.instance.status = Task.STATUS_PENDING

        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if not hasattr(self, 'user'):
            kwargs.update({'user': self.request.user})
        return kwargs


class TaskCreateView(LoginRequiredMixin, TaskStatusMixin, CreateView):
    model = Task
    form_class = TaskFrom

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        if form.cleaned_data['assigned_to']:
            TaskAssignUser.objects.create(user=self.request.user,
                                          task=form.instance)


class TaskUpdateView(LoginRequiredMixin, TaskStatusMixin, UpdateView):
    model = Task
    form_class = TaskFrom


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('task_management:list')
