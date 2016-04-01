from django import forms
from multiupload.fields import MultiFileField

from task_management.models import Task


class TaskFrom(forms.ModelForm):
    """  """
    class Meta:
        model = Task
        fields = ['title', 'description', 'criticality', 'date_due',
                  'assigned_to', ]

    attachments = MultiFileField(min_num=1, max_num=5)
