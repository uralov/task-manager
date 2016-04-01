from django.conf.urls import url

from task_management.views import TaskListView


urlpatterns = [
    url(r'^', TaskListView.as_view(), name='task_list'),
    # url(r'^create/',
    #     GenerateFilterChoicesApi.as_view(),
    #     name='get_filter_choices'),
]
