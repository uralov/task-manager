from django.conf.urls import url

from task_management.views import (
    TaskListView, TaskCreateView, TaskUpdateView, TaskDetailView,
    TaskDeleteView, SubTaskCreateView, CommentCreateView,
    AcceptTaskView
)


urlpatterns = [
    url(r'^$', TaskListView.as_view(), name='list'),
    url(r'^create/$', TaskCreateView.as_view(), name='create'),
    url(r'^(?P<pk>[0-9]+)/$', TaskDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/update/$', TaskUpdateView.as_view(), name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', TaskDeleteView.as_view(), name='delete'),

    url(r'^(?P<parent_pk>[0-9]+)/sub_task_create/$',
        SubTaskCreateView.as_view(), name='sub_task_create'),

    url(r'^(?P<task_pk>[0-9]+)/comment_create/$', CommentCreateView.as_view(),
        name='comment_create'),

    url(r'^(?P<task_pk>[0-9]+)/accept/$', AcceptTaskView.as_view(),
        name='accept'),
]
