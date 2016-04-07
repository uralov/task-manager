from django.apps import AppConfig


class TaskManageConfig(AppConfig):
    name = 'task_management'

    def ready(self):
        import task_management.signals
