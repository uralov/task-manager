from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView
from django.views.static import serve

from task_management.views import live_unread_notification_list

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^media/(?P<path>.*)$', serve,
        {'document_root': settings.MEDIA_ROOT}),
    url(r'^$', RedirectView.as_view(pattern_name='task_management:list'),
        name='index'),

    url(r'^task_management/', include('task_management.urls',
                                      namespace='task_management')),

    # override notifications unread list
    url(r'^inbox/notifications/api/unread_list/$',
        live_unread_notification_list, name='live_unread_notification_list'),
    url('^inbox/notifications/',
        include('notifications.urls', namespace='notifications')),
]
