from django.conf.urls import url

from task_management.views import (
    TaskListView, TaskCreateView, TaskUpdateView, TaskDetailView,
    TaskDeleteView,
    SubTaskCreateView)


urlpatterns = [
    url(r'^$', TaskListView.as_view(), name='list'),
    url(r'^create/', TaskCreateView.as_view(), name='create'),
    url(r'^detail/(?P<pk>[0-9]+)/', TaskDetailView.as_view(), name='detail'),
    url(r'^update/(?P<pk>[0-9]+)/', TaskUpdateView.as_view(), name='update'),
    url(r'^delete/(?P<pk>[0-9]+)/', TaskDeleteView.as_view(), name='delete'),

    url(r'^sub_task_create/(?P<parent_pk>[0-9]+)/',
        SubTaskCreateView.as_view(), name='sub_task_create'),
]
