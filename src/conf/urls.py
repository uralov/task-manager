from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView
from django.views.static import serve


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^task_management/', include('task_management.urls',
                                      namespace='task_management')),
    url(r'^media/(?P<path>.*)$', serve,
        {'document_root': settings.MEDIA_ROOT}),
    url(r'^$', RedirectView.as_view(pattern_name='task_management:list'),
        name='index')
]
