from django import forms
from django.contrib.auth.models import User

from multiupload.fields import MultiFileField

from task_management.models import Task, TaskAttachment, TaskOwner


class TaskFrom(forms.ModelForm):
    """ Form for creating task """
    class Meta:
        model = Task
        fields = ['title', 'description', 'criticality', 'date_due']

    attachments = MultiFileField(max_num=10, required=False)
    assigned_to = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(), required=False
    )

    def save(self, commit=True):
        assigned_to = list(self.cleaned_data['assigned_to'])
        if assigned_to:
            self.instance.status = Task.STATUS_PENDING
        task = super().save(commit)

        if assigned_to:
            # Create owner for first task
            TaskOwner.objects.create(user=assigned_to.pop(0), task=task)

        for each in self.cleaned_data['attachments']:
            TaskAttachment.objects.create(attachment=each, task=task)

        for owner in assigned_to:
            # create separate task for every assigned user except first
            task_duplicate = task
            task_duplicate.pk = None
            task_duplicate.save()

            TaskOwner.objects.create(user=owner, task=task_duplicate)

            for each in self.cleaned_data['attachments']:
                TaskAttachment.objects.create(attachment=each,
                                              task=task_duplicate)

        return task
