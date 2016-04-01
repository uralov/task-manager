from django.shortcuts import render
from django.views.generic import ListView, CreateView

from task_management.models import Task


class TaskListView(ListView):
    model = Task
    template_name = 'task_management/task_list.html'
    context_object_name = 'tasks_assigned'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(assigned_to=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_created'] = Task.objects.filter(author=self.request.user)

        return context
