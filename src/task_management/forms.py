from django import forms
from django.contrib.auth.models import User

from multiupload.fields import MultiFileField

from task_management.models import Task, TaskAttachment, TaskComment


class TaskForm(forms.ModelForm):
    """ Form for creating task """
    class Meta:
        model = Task
        fields = ['title', 'description', 'criticality', 'date_due']

    attachments = MultiFileField(max_num=10, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if not instance or not instance.owner:
            self.fields['assigned_to'] = forms.ModelMultipleChoiceField(
                queryset=User.objects.all(),
                required=False
            )

    def _save_attachment(self, task):
        for each in self.cleaned_data['attachments']:
            TaskAttachment.objects.create(attachment=each, task=task)

    def save(self, commit=True):
        assigned_to = list(self.cleaned_data.get('assigned_to', []))
        if assigned_to:
            self.instance.status = Task.STATUS_PENDING
            self.instance.owner = assigned_to.pop(0)

        task = super().save()
        self._save_attachment(task)

        for owner in assigned_to:
            # create separate task for every assigned user except first
            task_duplicate = task
            task_duplicate.pk = None
            task_duplicate.owner = owner
            task_duplicate.save()
            self._save_attachment(task_duplicate)

        return task


class CommentForm(forms.ModelForm):
    """ Form for comments """
    class Meta:
        model = TaskComment
        fields = ['message', ]
