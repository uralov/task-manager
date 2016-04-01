from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


class Task(models.Model):
    """ Task model """
    STATUS_DECLINED = 0
    STATUS_DRAFT = 1
    STATUS_PENDING = 2
    STATUS_WORKING = 3
    STATUS_HALF_DONE = 4
    STATUS_ALMOST_DONE = 5
    STATUS_COMPLETE = 6
    STATUS_CHOICES = (
        (STATUS_DECLINED, 'Declined'),
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PENDING, 'Pending Acceptance'),
        (STATUS_WORKING, 'Working On It'),
        (STATUS_HALF_DONE, 'Half Way Done'),
        (STATUS_ALMOST_DONE, 'Almost Done'),
        (STATUS_COMPLETE, 'Completed'),
    )

    CRITICALITY_LOW = 0
    CRITICALITY_MEDIUM = 1
    CRITICALITY_HIGH = 2
    CRITICALITY_CHOICES = (
        (CRITICALITY_LOW, 'Low criticality'),
        (CRITICALITY_MEDIUM, 'Medium criticality'),
        (CRITICALITY_HIGH, 'High criticality'),
    )

    title = models.CharField('Task title', max_length=4096)
    description = models.TextField('Task description')
    author = models.ForeignKey(User, verbose_name='Author of task',
                               related_name='task_author')
    assigned_to = models.ManyToManyField(User, blank=True,
                                         verbose_name='Task assigned to',
                                         related_name='task_assigned')
    status = models.SmallIntegerField('Task status', choices=STATUS_CHOICES)
    criticality = models.SmallIntegerField('Task criticality',
                                           choices=CRITICALITY_CHOICES)
    date_due = models.DateField('Task due date', blank=True, null=True)
    time_create = models.DateTimeField('Time of create', auto_now_add=True)
    time_update = models.DateTimeField('Time of update', auto_now=True)


class TaskDecline(models.Model):
    """ Declined tasks model """
    task = models.ForeignKey(Task, related_name='declines',
                             verbose_name='Declined task')
    reason = models.TextField('Reason for decline')
    time_decline = models.DateTimeField('Time of decline', auto_now_add=True)


class TaskAttachment:
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
