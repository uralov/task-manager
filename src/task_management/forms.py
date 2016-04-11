from django import forms
from django.contrib.auth.models import User

from multiupload.fields import MultiFileField

from task_management.models import (
    Task, TaskAttachment, TaskComment, TaskAssignedUser
)


class TaskForm(forms.ModelForm):
    """ Form for creating task """
    class Meta:
        model = Task
        fields = ['title', 'description', 'criticality', 'date_due']

    attachments = MultiFileField(max_num=10, required=False)

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        task = kwargs.get('instance')
        task_assign = TaskAssignedUser.objects.filter(task=task).exists()
        if not task or not task_assign:
            self.fields['assigned_to'] = forms.ModelMultipleChoiceField(
                queryset=User.objects.all(),
                required=False
            )

        if task and Task.is_status_can_change(task.status):
            self.fields['status'] = forms.ChoiceField(
                choices=[i for i in Task.STATUS_CHOICES
                         if Task.is_status_can_change(i[0])],
                initial=task.status
            )

    def _save_attachment(self, task):
        for each in self.cleaned_data['attachments']:
            TaskAttachment.objects.create(attachment=each, task=task)

    def save(self, commit=True):
        status = self.cleaned_data.get('status')
        if status:
            self.instance.status = status

        task = super(TaskForm, self).save()
        self._save_attachment(task)

        assigned_to = list(self.cleaned_data.get('assigned_to', []))
        if assigned_to:
            task.assign_to(assigned_to.pop(0))

        for owner in assigned_to:
            # create separate task for every assigned user except first
            task_duplicate = task
            task_duplicate.pk = None
            task_duplicate.save()
            self._save_attachment(task_duplicate)
            task_duplicate.assign_to(owner)

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
        self.instance.status = Task.STATUS_DECLINED

        return super(DeclineTaskForm, self).save(commit)
