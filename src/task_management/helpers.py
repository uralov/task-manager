import datetime
from django.core.mail import send_mail
from django.conf import settings
from conf.app_celery import app

from notifications.signals import notify

from task_management.models import Task


def send_message(actor, verb, task, recipients=()):
    """ Send message to notification and email
    :param actor: the object that performed the activity
    :param verb: the verb phrase that identifies the action of the activity
    :param task: task object
    :param recipients: recipients list
    :return:
    """
    if not recipients:
        recipients = get_recipients_by_task(task)

    # actor not receive messages about self activities
    recipients = [user for user in recipients if user != actor]

    email_msg = "{actor} {verb} <a href='{url}'>{task}</a>".format(
        actor=actor, verb=verb, url=task.get_absolute_url(),
        task=task.title
    )

    for recipient in recipients:
        # send notification
        notify.send(actor, recipient=recipient, verb=verb, target=task)

        # send mail via delay task
        send_email.delay(recipient.email, email_msg)


def get_recipients_by_task(task):
    """ Get recipients list by task owners chain.
    :param task: task object
    :return: task owners list
    """
    owners_chain = set(task.get_owners_chain())
    owners_chain.add(task.creator)

    return list(owners_chain)


@app.task(name='send_email')
def send_email(recipient, message):
    send_mail('New notification', message, settings.EMAIL_FROM, [recipient])


@app.task(name='send_deadline_notifications')
def send_deadline_notifications():
    """ Send reminders about coming deadlines
    :return:
    """
    deadline_interval_date = (
        datetime.date.today() +
        datetime.timedelta(days=settings.TASK_DEADLINE_INTERVAL)
    )
    tasks = Task.objects.filter(date_due=deadline_interval_date,
                                status__lt=Task.STATUS_COMPLETE)
    for task in tasks:
        send_message(task.creator, 'reminds about task', task)
