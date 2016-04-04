from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^task_management/', include('task_management.urls',
                                      namespace='task_management')),
    url(
        r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}
    ),
]
