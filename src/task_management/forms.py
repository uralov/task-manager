from django import forms
from django.contrib.auth.models import User

from multiupload.fields import MultiFileField

from task_management.models import Task, TaskAttachment, TaskAssignUser


class TaskFrom(forms.ModelForm):
    """ Form for creating task """
    class Meta:
        model = Task
        fields = ['title', 'description', 'criticality', 'date_due']

    attachments = MultiFileField(max_num=10, required=False)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        excluded_users = []
        instance = kwargs['instance']
        if instance:
            assign = TaskAssignUser.objects.get(user=user, task=instance)
            assign_children = assign.get_children()
            excluded_users = instance.assigned_to.all()

        self.fields['assigned_to'] = forms.ModelMultipleChoiceField(
            # queryset=User.objects.exclude(id__in=excluded_users),
            queryset=User.objects.all(),
            required=False
        )

    def save(self, commit=True):
        instance = super().save(commit)
        for each in self.cleaned_data['attachments']:
            TaskAttachment.objects.create(attachment=each, task=instance)

        return instance
