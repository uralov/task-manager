from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView
)

from task_management.forms import TaskForm, CommentForm
from task_management.models import Task, TaskComment


class TaskListView(LoginRequiredMixin, ListView):
    """ View to display the list of tasks """
    model = Task
    context_object_name = 'tasks_assigned'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_created'] = Task.objects.filter(
            creator=self.request.user
        )
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class SubTaskCreateView(TaskCreateView):
    def form_valid(self, form):
        parent_task = Task.objects.get(pk=self.kwargs['parent_pk'])
        form.instance.parent = parent_task

        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task

    def get_context_data(self, **kwargs):
        kwargs['comment_form'] = CommentForm()
        kwargs['comments'] = TaskComment.objects.filter(task=self.object)\
            .prefetch_related('author')
        return super().get_context_data(**kwargs)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('task_management:list')


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = TaskComment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.task = Task.objects.get(pk=self.kwargs['task_pk'])
        form.instance.author = self.request.user

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('task_management:detail',
                       kwargs={'pk': self.kwargs['task_pk']})
