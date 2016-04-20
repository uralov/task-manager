from django.conf.urls import url

from task_management.views import TaskListView, TaskCreateView, \
    TaskUpdateView, TaskDetailView, TaskDeleteView, SubTaskCreateView, \
    CommentCreateView, AcceptTaskView, RejectTaskView, ApproveTaskView, \
    DeclineTaskView, ReassignTaskView, ActionLogListView


urlpatterns = [
    url(r'^$', TaskListView.as_view(), name='list'),
    url(r'^create/$', TaskCreateView.as_view(), name='create'),
    url(r'^(?P<pk>[0-9]+)/$', TaskDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/update/$', TaskUpdateView.as_view(), name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', TaskDeleteView.as_view(), name='delete'),

    url(r'^(?P<pk>[0-9]+)/sub_task_create/$',
        SubTaskCreateView.as_view(), name='sub_task_create'),

    url(r'^(?P<pk>[0-9]+)/comment_create/$', CommentCreateView.as_view(),
        name='comment_create'),

    url(r'^(?P<pk>[0-9]+)/accept/$', AcceptTaskView.as_view(), name='accept'),
    url(r'^(?P<pk>[0-9]+)/reject/$', RejectTaskView.as_view(), name='reject'),

    url(r'^(?P<pk>[0-9]+)/approve/$', ApproveTaskView.as_view(),
        name='approve'),
    url(r'^(?P<pk>[0-9]+)/decline/$', DeclineTaskView.as_view(),
        name='decline'),

    url(r'^(?P<pk>[0-9]+)/reassign/$', ReassignTaskView.as_view(),
        name='reassign'),

    url(r'^action_log/$', ActionLogListView.as_view(), name='action_log'),
]
