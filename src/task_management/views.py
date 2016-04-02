from django.core.urlresolvers import reverse_lazy
from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView
)
from task_management.forms import TaskFrom
from task_management.models import Task


class TaskListView(ListView):
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


class TaskCreateView(CreateView):
    model = Task
    form_class = TaskFrom

    def form_valid(self, form):
        form.instance.author = self.request.user

        return super().form_valid(form)


class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskFrom


class TaskDetailView(DetailView):
    model = Task


class TaskDeleteView(DeleteView):
    model = Task
    success_url = reverse_lazy('task_management:list')
