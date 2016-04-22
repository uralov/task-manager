from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, \
    DetailView, DeleteView, View

from task_management.helpers import send_message, get_recipients_by_task
from task_management.forms import TaskForm, CommentForm, RejectTaskForm, \
    DeclineTaskForm, ReassignTaskForm
from task_management.models import Task, TaskComment, TaskAssignedUser, \
    TaskActionLog
from task_management.mixins import TaskChangePermitMixin, \
    TaskViewPermitMixin, TaskDeletePermitMixin, TaskAcceptPermitMixin, \
    TaskApprovePermitMixin, TaskReassignPermitMixin


class TaskListView(LoginRequiredMixin, ListView):
    """ View for display the list of tasks """
    model = Task

    def get_queryset(self):
        user = self.request.user
        queryset = super(TaskListView, self).get_queryset()
        queryset = queryset.filter(Q(owners=user) | Q(creator=user))

        return queryset

    @staticmethod
    def get_trees(task_queryset):
        """ Create task trees from queryset.
        :param task_queryset: Task model queryset
        :return: list of task trees
        """
        task_list = task_queryset.order_by('parent')
        trees = {}
        task_list_without_parent_node = []
        for t in task_list:
            if not t.parent:
                trees[(t.id,)] = (t,)
            else:
                task_list_without_parent_node.append(t)

        task_list = task_list_without_parent_node
        while task_list:
            t = task_list.pop(0)
            for k, v in trees.items():
                if t.parent_id in k:
                    trees[k+(t.id,)] = trees.pop(k) + (t,)
                    t = False
                    break

            if t:
                # if parent not fount create new element
                trees[(t.id,)] = (t,)

        return [v for k, v in trees.items()]

    def get_context_data(self, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)
        context['task_trees'] = self.get_trees(self.get_queryset())

        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    """ View for create new task """
    model = Task
    form_class = TaskForm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        result = super(TaskCreateView, self).form_valid(form)

        TaskActionLog.log(self.request.user, 'create task', self.object)

        return result

    def get_form_kwargs(self):
        kwargs = super(TaskCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})

        return kwargs

    def get_success_url(self):
        return reverse('task_management:list')


class SubTaskCreateView(TaskChangePermitMixin, TaskCreateView):
    """ View for create sub task """
    def form_valid(self, form):
        parent_task = Task.objects.get(pk=self.kwargs['pk'])
        form.instance.parent = parent_task
        result = super(SubTaskCreateView, self).form_valid(form)

        # send message
        recipients = get_recipients_by_task(parent_task)
        send_message(self.request.user, 'create sub task', self.object,
                     recipients)

        return result


class TaskUpdateView(TaskChangePermitMixin, UpdateView):
    """ View for update task """
    model = Task
    form_class = TaskForm

    def form_valid(self, form):
        task = self.object
        user = self.request.user
        if task.status == Task.STATUS_DECLINE and user == task.creator:
            if form.cleaned_data['assigned_to']:
                TaskAssignedUser.objects.filter(task=task).delete()

        form_task_status = form.cleaned_data.get('status')
        if form_task_status and str(task.status) != form_task_status:
            new_status = int(form_task_status)
            new_status = dict(form.fields['status'].choices)[new_status]
            send_message(
                self.request.user,
                'change status of task to {0}'.format(new_status),
                task
            )

        TaskActionLog.log(user, 'update task', task)

        return super(TaskUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(TaskUpdateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})

        return kwargs


class TaskDetailView(TaskViewPermitMixin, DetailView):
    """ View for display task detail """
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
    """ View for delete task """
    model = Task
    success_url = reverse_lazy('task_management:list')

    def post(self, request, *args, **kwargs):
        TaskActionLog.log(self.request.user,
                          'delete task {0}'.format(self.get_object().title))

        return super(TaskDeleteView, self).post(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CreateView):
    """ View for comment task """
    model = TaskComment
    form_class = CommentForm

    def form_invalid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        form.instance.task = Task.objects.get(pk=self.kwargs['pk'])
        form.instance.author = self.request.user

        result = super(CommentCreateView, self).form_valid(form)
        TaskActionLog.log(self.request.user, 'add comment', self.object)

        return result

    def get_success_url(self):
        return reverse('task_management:detail',
                       kwargs={'pk': self.kwargs['pk']})


class AcceptTaskView(TaskAcceptPermitMixin, View):
    """ View for accept task """
    def get(self, *args, **kwargs):
        task = self.get_task()
        assign = TaskAssignedUser.objects.get(task=task,
                                              user=self.request.user)
        assign.assign_accept = True
        assign.save()

        TaskActionLog.log(self.request.user, 'accept task', task)
        send_message(self.request.user, 'assigned task', task)

        return redirect(task)


class RejectTaskView(TaskAcceptPermitMixin, UpdateView):
    """ View for reject task """
    model = TaskAssignedUser
    form_class = RejectTaskForm
    template_name = 'task_management/task_reject_form.html'

    def get_object(self, queryset=None):
        return self.model.objects.get(task=self.get_task(),
                                      user=self.request.user)

    def post(self, request, *args, **kwargs):
        result = super(RejectTaskView, self).post(request, *args, **kwargs)
        TaskActionLog.log(self.request.user, 'reject task', self.object)
        send_message(self.request.user, 'reject task', self.get_task())

        return result

    def get_success_url(self):
        return reverse('task_management:detail',
                       kwargs={'pk': self.kwargs['pk']})


class ApproveTaskView(TaskApprovePermitMixin, View):
    """ View for reject task """
    object = None

    def get_object(self):
        if not self.object:
            self.object = Task.objects.get(pk=self.kwargs['pk'])

        return self.object

    def get(self, *args, **kwargs):
        task = self.get_object()
        task.status = Task.STATUS_APPROVE
        task.save()

        TaskActionLog.log(self.request.user, 'approve task', task)
        send_message(self.request.user, 'approve task', task)

        return redirect(task)


class DeclineTaskView(TaskApprovePermitMixin, UpdateView):
    """ View for decline task """
    model = Task
    form_class = DeclineTaskForm
    template_name = 'task_management/task_decline_form.html'

    def post(self, request, *args, **kwargs):
        result = super(DeclineTaskView, self).post(request, *args, **kwargs)
        TaskActionLog.log(self.request.user, 'decline task', self.object)
        send_message(self.request.user, 'decline task', self.object)

        return result


class ReassignTaskView(TaskReassignPermitMixin, UpdateView):
    """ View for re-assign task """
    model = Task
    form_class = ReassignTaskForm
    template_name = 'task_management/task_reassign_form.html'

    def post(self, request, *args, **kwargs):
        result = super(ReassignTaskView, self).post(request, *args, **kwargs)
        TaskActionLog.log(self.request.user, 're-assign task', self.object)
        send_message(
            self.request.user,
            're-assign task to {0}'.format(self.object.owner),
            self.object
        )

        return result


class ActionLogListView(LoginRequiredMixin, ListView):
    """ View for display the list of action logs """
    model = TaskActionLog
    template_name = 'task_management/action_log_list.html'
    paginate_by = 25

    def get_queryset(self):
        return TaskActionLog.objects.select_related('actor').all()


def live_unread_notification_list(request):
    """ Overriding notifications.views.live_unread_notification_list.
    Adding target_url in params.
    :param request:
    :return:
    """
    if not request.user.is_authenticated():
        data = {
           'unread_count': 0,
           'unread_list': [],
        }
        return JsonResponse(data)

    try:
        num_to_fetch = request.GET.get('max', 5)
        num_to_fetch = int(num_to_fetch)
        num_to_fetch = max(1, num_to_fetch)
        num_to_fetch = min(num_to_fetch, 100)
    except ValueError:
        num_to_fetch = 5  # If casting to an int fails, just make it 5.

    unread_list = []

    for n in request.user.notifications.unread()[0:num_to_fetch]:
        struct = model_to_dict(n)
        struct['slug'] = n.slug
        if n.actor:
            struct['actor'] = str(n.actor)
        if n.target:
            struct['target'] = str(n.target)
            struct['target_url'] = n.target.get_absolute_url()
        if n.action_object:
            struct['action_object'] = str(n.action_object)
        unread_list.append(struct)
    data = {
        'unread_count': request.user.notifications.unread().count(),
        'unread_list': unread_list,
    }
    return JsonResponse(data)
