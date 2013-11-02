from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
                       url(r'^$', 'django.contrib.auth.views.login', {'template_name':'users/login.html', 'extra_context':{'next':'/user/home'}}, name='login'),
                       url(r'^user/', include('users.urls', namespace='user')),
)

# Service MEDIA from here if in DEBUG mode.
if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)', 'serve', {'document_root': settings.MEDIA_ROOT}))
    
