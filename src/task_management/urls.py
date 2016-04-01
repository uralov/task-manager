from django.conf.urls import url

from task_management.views import TaskListView, TaskCreateView


urlpatterns = [
    url(r'^', TaskListView.as_view(), name='task_list'),
    url(r'^create/', TaskCreateView.as_view(), name='task_create'),
]
