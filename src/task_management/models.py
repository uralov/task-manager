from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField


class Task(MPTTModel):
    """ Task model """
    STATUS_DECLINED = 0
    STATUS_DRAFT = 1
    STATUS_PENDING = 2
    STATUS_WORKING = 3
    STATUS_HALF_DONE = 4
    STATUS_ALMOST_DONE = 5
    STATUS_COMPLETE = 6
    STATUS_APPROVE = 7
    STATUS_CHOICES = (
        (STATUS_DECLINED, 'Declined'),
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PENDING, 'Pending Acceptance'),
        (STATUS_WORKING, 'Working On It'),
        (STATUS_HALF_DONE, 'Half Way Done'),
        (STATUS_ALMOST_DONE, 'Almost Done'),
        (STATUS_COMPLETE, 'Completed'),
        (STATUS_APPROVE, 'Approve'),
    )

    CRITICALITY_LOW = 0
    CRITICALITY_MEDIUM = 1
    CRITICALITY_HIGH = 2
    CRITICALITY_CHOICES = (
        (CRITICALITY_HIGH, 'High'),
        (CRITICALITY_MEDIUM, 'Medium'),
        (CRITICALITY_LOW, 'Low'),
    )
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children', db_index=True)
    title = models.CharField('Title', max_length=4096)
    description = models.TextField('Description')
    creator = models.ForeignKey(User, verbose_name='Creator',
                                related_name='created_tasks')
    owner = models.ForeignKey(
        User, verbose_name='Owner', related_name='owned_tasks',
        blank=True, null=True
    )
    owners = TreeManyToManyField(
        User, verbose_name='Owners', through='TaskAssignedUser',
        blank=True, null=True
    )
    status = models.SmallIntegerField('Status', choices=STATUS_CHOICES,
                                      default=STATUS_DRAFT)
    status_description = models.TextField('Status description')
    criticality = models.SmallIntegerField('Criticality',
                                           choices=CRITICALITY_CHOICES,
                                           default=CRITICALITY_MEDIUM)
    date_due = models.DateField('Due date', blank=True, null=True)
    time_create = models.DateTimeField('Time of create', auto_now_add=True)
    time_update = models.DateTimeField('Time of update', auto_now=True)

    def get_absolute_url(self):
        return reverse('task_management:detail', kwargs={'pk': self.pk})

    def is_owner_accept_task(self):
        return TaskAssignedUser.objects.filter(task=self).order_by(
            'time_assign').last().assign_accept

    def get_owners_chain(self, assign_accept=None):
        """ get chain of assignment users
        :param assign_accept:
        :return: list of assignment users
        """
        task_owner_chain = TaskAssignedUser.objects.filter(task=self).order_by(
            'time_assign').prefetch_related('user')
        if assign_accept:
            task_owner_chain.filter(assign_accept=assign_accept)

        return [obj.user for obj in task_owner_chain]

    def get_assign_accept_owner_chain(self):
        return self.get_owners_chain(assign_accept=True)

    @staticmethod
    def is_status_can_change(status):
        return Task.STATUS_PENDING < status < Task.STATUS_APPROVE

    def __str__(self):
        return self.title


class TaskAssignedUser(MPTTModel):
    """ Stores chain of assignments of tasks to users """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE,
                             related_name='owners_chain')
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children', db_index=True)
    time_assign = models.DateTimeField(auto_now_add=True)
    assign_accept = models.NullBooleanField(verbose_name='Accept assign')
    assign_description = models.TextField(verbose_name='Description',
                                          blank=True, null=True)

    class Meta:
        unique_together = ('user', 'task')
        ordering = ('time_assign', )


class TaskAttachment(models.Model):
    """ Task attachments model """
    task = models.ForeignKey(Task, related_name='attachments',
                             verbose_name='Attachment task')
    attachment = models.FileField('Attachment',
                                  upload_to='task_attachment/%Y/%m/%d/')


class TaskComment(models.Model):
    """ Task comments model """
    task = models.ForeignKey(Task, related_name='comments',
                             verbose_name='Comment task')
    author = models.ForeignKey(User, verbose_name='Author of comment')
    message = models.TextField('Comment message')
    time_create = models.DateTimeField('Time of create', auto_now_add=True)
    time_update = models.DateTimeField('Time of update', auto_now=True)


class TaskActionLog(models.Model):
    """ User action log on tasks """
    ACTION_TASK_CREATE = 0
    ACTION_TASK_CHANGE = 1
    ACTION_ATTACHMENT_UPLOAD = 2
    ACTION_SUB_TASK_CREATE = 3
    ACTION_TASK_STATUS_CHANGE = 4
    ACTION_TASK_COMMENT = 5
    ACTION_CHOICES = (
        (ACTION_TASK_CREATE, 'Task create'),
        (ACTION_TASK_CHANGE, 'Task change'),
        (ACTION_ATTACHMENT_UPLOAD, 'Attachment upload'),
        (ACTION_SUB_TASK_CREATE, 'Sub task create'),
        (ACTION_TASK_STATUS_CHANGE, 'Task status change'),
        (ACTION_TASK_COMMENT, 'Task comment'),
    )

    task = models.ForeignKey(Task, related_name='actions',
                             verbose_name='Action task')
    actor = models.ForeignKey(User, verbose_name='Actor')
    action_type = models.SmallIntegerField('Action type',
                                           choices=ACTION_CHOICES)
    time_action = models.DateTimeField('Time of action', auto_now_add=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
