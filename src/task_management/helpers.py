from django.core.mail import send_mail
from django.conf import settings
from notifications.signals import notify


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

        # send email
        send_mail('New notification', email_msg, settings.EMAIL_FROM,
                  [recipient.email])


def get_recipients_by_task(task):
    """ Get recipients list by task owners chain.
    :param task: task object
    :return: task owners list
    """
    owners_chain = set(task.get_owners_chain())
    owners_chain.add(task.creator)

    return list(owners_chain)
