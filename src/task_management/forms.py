from django import forms
from multiupload.fields import MultiFileField

from task_management.models import Task, TaskAttachment


class TaskFrom(forms.ModelForm):
    """  """
    class Meta:
        model = Task
        fields = ['title', 'description', 'criticality', 'date_due',
                  'assigned_to', ]

    attachments = MultiFileField(max_num=10, required=False)

    def save(self, commit=True):
        instance = super().save(commit)
        for each in self.cleaned_data['attachments']:
            TaskAttachment.objects.create(file=each, task=instance)

        return instance
