from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    """ Task model """
    STATUS_DECLINED = 0
    STATUS_DRAFT = 1
    STATUS_PENDING = 2
    STATUS_IN_WORK = 3
    STATUS_HALF_DONE = 4
    STATUS_ALMOST_DONE = 5
    STATUS_COMPLETE = 6
    STATUS_CHOICES = (
        (STATUS_DECLINED, 'Declined'),
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PENDING, 'Pending Acceptance'),
        (STATUS_IN_WORK, 'Working On It'),
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

    title = models.CharField('Task title')
    description = models.TextField('Task description')
    assigned_to = models.ManyToManyField(User, blank=True,
                                         verbose_name='Task assigned to')
    status = models.SmallIntegerField('Task status', choices=STATUS_CHOICES)
    criticality = models.SmallIntegerField('Task criticality',
                                           choices=CRITICALITY_CHOICES)
    date_due = models.DateField('Task due date', blank=True, null=True)
    time_create = models.DateTimeField('Time of create', auto_now_add=True)
    time_update = models.DateTimeField('Time of update', auto_now=True)
