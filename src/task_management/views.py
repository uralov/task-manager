from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView
)

from task_management.forms import TaskFrom
from task_management.models import Task, TaskOwner


class TaskListView(LoginRequiredMixin, ListView):
    """ View to display the list of tasks """
    model = Task
    context_object_name = 'tasks_assigned'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(owners__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_created'] = Task.objects.filter(
            creator=self.request.user
        )
        return context


class TaskStatusMixin(object):
    """ Common status logic mixin """
    def form_valid(self, form):
        if form.cleaned_data['assigned_to']:
            form.instance.status = Task.STATUS_PENDING

        return super().form_valid(form)


class TaskCreateView(LoginRequiredMixin, TaskStatusMixin, CreateView):
    model = Task
    form_class = TaskFrom

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, TaskStatusMixin, UpdateView):
    model = Task
    form_class = TaskFrom


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('task_management:list')
