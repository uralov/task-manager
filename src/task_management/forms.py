from django import forms
from django.contrib.auth.models import User

from task_management.helpers import send_message
from task_management.models import (
    Task, TaskAttachment, TaskComment, TaskAssignedUser,
    TaskActionLog
)


class MultiFileInput(forms.FileInput):
    def render(self, name, value, attrs=None):
        attrs['multiple'] = 'multiple'
        return super(MultiFileInput, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        else:
            value = files.get(name)
            if isinstance(value, list):
                return value
            else:
                return [value]


class MultiFileField(forms.FileField):
    widget = MultiFileInput

    def to_python(self, data):
        ret = []
        for item in data:
            i = super(MultiFileField, self).to_python(item)
            if i:
                ret.append(i)
        return ret


class TaskForm(forms.ModelForm):
    """ Form for creating task """
    class Meta:
        model = Task
        fields = ['title', 'description', 'criticality', 'date_due']

    def __init__(self, user=None, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.user = user
        task = kwargs.get('instance')

        if not task or not task.owner:
            # multiple task assign
            self.fields['assigned_to'] = forms.ModelMultipleChoiceField(
                queryset=User.objects.all(),
                required=False
            )

        if task and Task.is_status_can_change(task.status) \
                and task.is_leaf_node():
            # change task status
            self.fields['status'] = forms.ChoiceField(
                choices=[i for i in Task.STATUS_CHOICES
                         if Task.is_status_can_change(i[0])],
                initial=task.status
            )

        if task and task.status == Task.STATUS_DECLINE and user == task.creator:
            # if task was reject, creator can choose new task owner
            self.fields['assigned_to'] = forms.ModelChoiceField(
                queryset=User.objects.all(), required=False,
                label='Assign again'
            )

        # multiple upload file field
        self.fields['attachments'] = MultiFileField(required=False)

        if task:
            attachments = task.attachments.all()
            if attachments:
                # delete attachment
                self.fields['delete_attachment'] = forms.ModelMultipleChoiceField(
                    queryset=attachments,
                    widget=forms.CheckboxSelectMultiple,
                    required=False,
                )

    def _save_attachment(self, task):
        """ Save attachment files
        :param task: Task object
        :return:
        """""
        for each in self.cleaned_data['attachments']:
            TaskAttachment.objects.create(attachment=each, task=task)

        if self.cleaned_data['attachments']:
            TaskActionLog.log(self.user, 'add attachments to task', task)
            send_message(self.user, 'add attachments to task', task)

    def _delete_attachment(self, task):
        """ Delete checked attachment files
        :param task: Task object
        :return:
        """
        for each in self.cleaned_data.get('delete_attachment', []):
            each.delete()

    def _save_multi_assign(self, assigned_to, task):
        """ Create separate task for every assigned user except first.
        :param assigned_to:
        :param task:
        :return:
        """
        for owner in assigned_to:
            task_duplicate = task
            task_duplicate.pk = None
            task_duplicate.owner = owner
            task_duplicate.save()
            self._save_attachment(task_duplicate)

            TaskActionLog.log(self.user, 'create task', task_duplicate)
            if task_duplicate.owner:
                send_message(self.user, 'assigned you task', task_duplicate,
                             [task_duplicate.owner])

    def save(self, commit=True):
        """ Save task form to object
        :param commit: save form if True
        :return: task object
        """
        status = self.cleaned_data.get('status')
        if status:
            self.instance.status = status

        assigned_to = self.cleaned_data.get('assigned_to', [])
        try:
            assigned_to = list(assigned_to)
        except TypeError:
            assigned_to = [assigned_to]
        if assigned_to:
            self.instance.owner = assigned_to.pop(0)

        task = super(TaskForm, self).save()
        if task.owner:
            send_message(self.user, 'assigned you task', task, [task.owner])

        self._save_attachment(task)
        self._delete_attachment(task)

        self._save_multi_assign(assigned_to, task)

        return task


class CommentForm(forms.ModelForm):
    """ Form for comments """
    class Meta:
        model = TaskComment
        fields = ['message', ]


class RejectTaskForm(forms.ModelForm):
    """ Form for reject task """
    class Meta:
        model = TaskAssignedUser
        fields = ['assign_description', ]

    def save(self, commit=True):
        self.instance.assign_accept = False

        return super(RejectTaskForm, self).save(commit)


class DeclineTaskForm(forms.ModelForm):
    """ From for decline task """
    class Meta:
        model = Task
        fields = ['status_description', ]

    def save(self, commit=True):
        self.instance.status = Task.STATUS_DECLINE

        return super(DeclineTaskForm, self).save(commit)


class ReassignTaskForm(forms.ModelForm):
    """ From for re-assign task """
    class Meta:
        model = Task
        fields = ['owner', ]

    def __init__(self, *args, **kwargs):
        super(ReassignTaskForm, self).__init__(*args, **kwargs)
        task = kwargs.get('instance')
        owners_chain_id = [user.id for user in task.get_owners_chain()]
        owners_chain_id.append(task.creator_id)

        self.fields['owner'] = forms.ModelChoiceField(
            queryset=User.objects.all().exclude(id__in=owners_chain_id),
            required=True, label='Re-assign to'
        )
